from collections import defaultdict
from collections import deque
from functools import reduce

from nltk import PorterStemmer
from nltk import sent_tokenize
from nltk import word_tokenize

from .document import Document
from .postingslist import Posting
from .postingslist import PostingsList
from .term import Term
from .util import string_to_date
from .util import tf
from .util import stem
from .util import has_any_alphanumeric
from .util import get_line_pointers
from .util import write_dictionary
from .util import write_documents

import csv
import math
import os
import pickle
import sys

class Indexer:
    '''
    indexer class responsible for indexing documents.

    postings_file -> file to store postings.
    dictionary_file -> file to store dictionary of terms.
    document_file -> file to store documents' meta data.
    '''

    def __init__(self, postings_file, dictionary_file, document_file):
        self.postings_file = postings_file
        self.dictionary_file = dictionary_file
        self.document_file = document_file
        self.dictionary = defaultdict(lambda: Term())
        self.documents = defaultdict(lambda: Document())

    def _generate_documents(self, data_file):
        '''
        generator for yielding (doc id, title, date_posted, court, content) tuples
        allows program to read document by document without loading everything into memory
        '''
        csv.field_size_limit((1 << 31) - 1)
        with open(data_file, newline='', encoding='utf8') as f:
            data = csv.reader(f)
            next(data)
            for doc_id, title, content, date_posted, court in data:
                doc_id = int(doc_id)
                date_posted = string_to_date(date_posted)
                yield doc_id, title, date_posted, court, content

    def count_documents(self, data_file):
        '''
        counts the total documents in the data file
        this will iterate through all available documents in the file
        '''
        csv.field_size_limit(sys.maxsize)
        adder = lambda x, y: x + 1
        with open(data_file, newline='', encoding='utf8') as f:
            return reduce(adder, csv.reader(f), 0) - 1

    def _index_content(self, content, offset):
        '''
        indexes the content of a single document
        collects a dictionary of term -> list of positional indexes
        only words that contain at least one alphanumeric character is stored as a term
        however, positional indexes, takes into account all words, regardless of whether they are considered terms
        this is to maintain accurate information on the absolute positions of terms (for a strict phrase query match)
        '''
        terms = defaultdict(list)
        words = word_tokenize(content)

        if not len(words):
            return terms, offset

        for index, word in enumerate(words):
            if has_any_alphanumeric(word):
                term = stem(word.strip().casefold())
                terms[word].append(index + offset)
        for term in terms:
            self.dictionary[term].line = len(self.dictionary)
            self.dictionary[term].doc_frequency += 1

        return terms, index + offset

    def _write_to_postings_file(self, postings_lists):
        '''
        writes postings lists to file
        each line denotes a postings list
        '''
        sort_by_line_comparator = lambda k: self.dictionary[k[0]].line
        to_write = sorted(postings_lists.items(), key=sort_by_line_comparator)
        with open(self.postings_file, 'a+', encoding='utf8') as f:
            f.seek(0)
            for term, postings_list in to_write:
                f.write(str(postings_list.compress()) + '\n')

    def index(self, data_file, limit=-1):
        '''
        indexes documents in the data file.
        builds dictionary of terms
        builds a collection of document objects (contains meta data)
        '''
        doc_generator = self._generate_documents(data_file)
        postings_lists = defaultdict(lambda: PostingsList())
        for index, data in enumerate(doc_generator):
            if index == limit:
                break
            doc_id, title, date_posted, court, content = data
            doc = self.documents[doc_id]
            doc.add(title, date_posted, court)
            term_positions, word_count = self._index_content(content, doc.word_count)
            doc.word_count = word_count
            for term, positions in term_positions.items():
                term_frequency = len(positions)
                postings_lists[term].add(Posting(doc_id, term_frequency, positions))
                doc.length += tf(term_frequency) ** 2
            print(f'indexed {index} documents', end='\r')
        print(f'indexed {index} documents')
        self._write_to_postings_file(postings_lists)

        # update the euclidean distance of documents (vector length)
        for doc in self.documents.values():
            doc.length = math.sqrt(doc.length)
            del doc.word_count # remove word_count attribute, not necessary after indexing.

        pointers = get_line_pointers(self.postings_file)
        for term, pointer in zip(self.dictionary.values(), pointers):
            term.offset = pointer # update pointer for efficient disk read of terms' postings lists.
            del term.line # remove line attribute, not necessary after indexing.

        write_dictionary(self.dictionary, self.dictionary_file)
        print(f'saved dictionary to {self.dictionary_file}')
        write_documents(self.documents, self.document_file)
        print(f'saved documents to {self.document_file}')
        
