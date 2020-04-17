from collections import defaultdict
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
    '''

    def __init__(self, postings_file, dictionary_file, document_file):
        '''
        postings_file -> file to store postings.
        dictionary_file -> file to store dictionary of terms.
        document_file -> file to store documents' meta data.
        '''
        self.postings_file = postings_file
        self.dictionary_file = dictionary_file
        self.document_file = document_file
        self.dictionary = {}
        self.documents = {}

    def _generate_documents(self, data_file):
        '''
        generator for yielding (Document, content) tuples.
        '''
        csv.field_size_limit(sys.maxsize)
        with open(data_file, newline='') as f:
            data = csv.reader(f)
            next(data)
            for doc_id, title, content, date_posted, court in data:
                doc_id = int(doc_id)
                date_posted = string_to_date(date_posted)
                yield doc_id, Document(title, date_posted, court), content

    def count_documents(self, data_file):
        csv.field_size_limit(sys.maxsize)
        adder = lambda x, y: x + 1
        with open(data_file, newline='') as f:
            return reduce(adder, csv.reader(f), 0) - 1

    def _index_content(self, content):
        terms = defaultdict(list)
        words = word_tokenize(content)
        for index, word in enumerate(words):
            if has_any_alphanumeric(word):
                term = stem(word.strip().casefold())
                terms[word].append(index)
        for term in terms:
            if term not in self.dictionary:
                self.dictionary[term] = Term(0, line=len(self.dictionary))
            self.dictionary[term].doc_frequency += 1
        
        return terms

    def write_to_postings_file(self, term_postings):
        '''
        writes postings of terms to postings file.
        '''
        line_postings_pairs = [(self.dictionary[t].line, p) for t, p in term_postings.items()]
        line_postings_pairs = sorted(line_postings_pairs, key=lambda k: k[0], reverse=True)
        temp_postings_file = 'temp-postings.txt'
        with open(self.postings_file, 'a+') as f, open(temp_postings_file, 'w+') as t:
            f.seek(0)
            line_index = 0
            line_number, posting = line_postings_pairs[-1] if line_postings_pairs else (-1, [])
            line = f.readline()
            while line:
                if line_number == line_index:
                    postings_list = PostingsList.parse(line.strip()).decompress()
                    postings_list.add(posting)
                    t.write(str(postings_list.compress()) + '\n')
                    line_postings_pairs.pop()
                    line_number, posting = line_postings_pairs[-1] if line_postings_pairs else (-1, [])
                else:
                    t.write(line)
                line_index += 1
                line = f.readline()
            while line_postings_pairs:
                t.write(str(PostingsList([posting]).compress()) + '\n')
                line_postings_pairs.pop()
                line_number, posting = line_postings_pairs[-1] if line_postings_pairs else (-1, [])
        os.replace(temp_postings_file, self.postings_file)

    def index(self, data_file, limit=-1):
        '''
        indexes documents in the data file.
        '''
        doc_generator = self._generate_documents(data_file)
        doc_count = 0
        for doc_id, doc, content in doc_generator:
            if doc_count == limit:
                break
            term_postings = {}
            self.documents[doc_id] = doc
            length = 0
            for term, positions in self._index_content(content).items():
                term_frequency = len(positions)
                term_postings[term] = Posting(doc_id, term_frequency, positions)
                length += tf(term_frequency) ** 2
            doc.length = length
            doc_count += 1
            self.write_to_postings_file(term_postings)
            print(f'indexed {doc_count} documents', end='\r')
        print(f'indexed {doc_count} documents')
        
        # update the euclidean distance of documents (vector length)
        for doc in self.documents.values():
            doc.length = math.sqrt(doc.length)

        pointers = get_line_pointers(self.postings_file)
        for term, pointer in zip(self.dictionary.values(), pointers):
            term.offset = pointer # update pointer for efficient disk read of terms' postings lists.
            del term.line # remove line attribute as it is not needed after indexing.

        print(f'completed indexing {doc_count} documents')

        write_dictionary(self.dictionary, self.dictionary_file)
        write_documents(self.documents, self.document_file)
        
        print(f'saved dictionary and document meta data')

