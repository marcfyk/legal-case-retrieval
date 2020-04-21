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
from .util import idf
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
    dictionary -> dictionary of term -> term objects to store information on terms.
    documents -> dictionary of doc_id -> document objects to store meta data and vectors on docs.
    '''

    def __init__(self, postings_file, dictionary_file, document_file):
        self.postings_file = postings_file
        self.dictionary_file = dictionary_file
        self.document_file = document_file
        self.dictionary = {}
        self.documents = {}

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
        this is to maintain accurate information on the absolute positions of terms (for a strict phrase query match).

        therefore for the text "a ... b", "a" and "b" are indexed while "..." is not, however, from the positional indexes,
        "a" and "b" are not adjacent to each other from this given text.
        '''
        terms = {}
        words = word_tokenize(content)

        if not len(words):
            return terms, offset

        for index, word in enumerate(words):
            if has_any_alphanumeric(word):
                term = stem(word)
                if term not in terms:
                    terms[term] = []
                terms[term].append(index + offset)
        for term in terms:
            if term not in self.dictionary:
                self.dictionary[term] = Term()
            self.dictionary[term].line = len(self.dictionary)
            self.dictionary[term].doc_frequency += 1

        return terms, index + offset

    def _build_doc_vector(self, content, k=20):
        '''
        builds a vector where terms are the axes of the vector.
        k denotes the top k terms to be stored as the vector, (measured by tf-idf weighting)
        this vector is to contain the top k weighted terms that the doc's content contains.
        '''
        terms = [stem(w) for w in word_tokenize(content) if has_any_alphanumeric(w)]
        term_weights = {}
        for term in terms:
            if term not in term_weights:
                term_weights[term] = 0
            term_weights[term] += 1
        for term, freq in term_weights.items():
            term_weights[term] = tf(freq) * idf(len(self.documents), self.dictionary[term].doc_frequency)
        
        top_k_terms = sorted(term_weights, key=lambda k: term_weights[k], reverse=True)[:k]
        vector = {t: term_weights[t] for t in top_k_terms}
        return vector

    def _write_to_postings_file(self, postings_lists):
        '''
        writes postings lists to file
        each line denotes a postings list
        '''
        with open(self.postings_file, 'a+', encoding='utf8') as f:
            f.seek(0)
            for term, postings_list in postings_lists.items():
                f.write(str(postings_list.compress()) + '\n')

    def index(self, data_file, limit=-1):
        '''
        indexes documents in the data file.
        builds dictionary of terms
        builds a collection of document objects (contains meta data)
        '''
        postings_lists = {}
        for index, data in enumerate(self._generate_documents(data_file)):
            if index == limit:
                break
            doc_id, title, date_posted, court, content = data
            if doc_id not in self.documents:
                self.documents[doc_id] = Document()
            doc = self.documents[doc_id]
            doc.add(title, date_posted, court)
            term_positions, word_count = self._index_content(content, doc.word_count)
            doc.word_count = word_count
            for term, positions in term_positions.items():
                term_frequency = len(positions)
                if term not in postings_lists:
                    postings_lists[term] = PostingsList()
                postings_lists[term].add(Posting(doc_id, term_frequency, positions))

        self._write_to_postings_file(postings_lists)
        pointers = get_line_pointers(self.postings_file)
        for term, pointer in zip(self.dictionary.values(), pointers):
            term.offset = pointer # update pointer for efficient disk read of terms' postings lists.
            del term.line # remove line attribute, not necessary after indexing.
        print(f'saved postings lists to {self.postings_file}')

        for index, data in enumerate(self._generate_documents(data_file)):
            if index == limit:
                break
            doc_id, title, date_posted, court, content = data
            doc = self.documents[doc_id]
            doc.update_vector(self._build_doc_vector(content)) # update document vectors and length

        for doc in self.documents.values():
            del doc.word_count # remove word_count attribute, not necessary after indexing.

        write_dictionary(self.dictionary, self.dictionary_file)
        print(f'saved dictionary to {self.dictionary_file}')
        write_documents(self.documents, self.document_file)
        print(f'saved documents to {self.document_file}')
        
