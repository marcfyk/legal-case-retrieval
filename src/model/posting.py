from itertools import accumulate

from .util import inverse_accumulate

import re

_delimiter = '/'
_position_delimiter = ','
_pattern = re.compile(f'^[0-9]*[{_delimiter}][0-9]*[{_delimiter}][0-9]+({_position_delimiter}[0-9]+)*$')

class Posting:

    def __init__(self, doc_id, term_frequency=0, positions=[]):
        self.doc_id = doc_id
        self.term_frequency = term_frequency
        self.positions = [p for p in positions]

    @classmethod
    def parse(cls, posting_string):
        '''
        parses a string into a posting.
        '''
        if not _pattern.match(posting_string):
            raise ValueError(f'invalid format: {posting_string}')

        doc_id, term_frequency, positions = posting_string.split(_delimiter)
        doc_id, term_frequency, positions = (
                int(doc_id), 
                int(term_frequency), 
                [int(x) for x in positions.split(_position_delimiter) if x != ''])
        return Posting(doc_id, term_frequency, positions)

    def compress(self):
        '''
        compresses posting's positional indexes.
        '''
        self.positions = inverse_accumulate(self.positions)
        return self

    def decompress(self):
        '''
        decompresses posting.
        '''
        self.positions = [p for p in accumulate(self.positions)]
        return self
    
    def __str__(self):
        doc_id = str(self.doc_id)
        term_frequency = str(self.term_frequency)
        positions = _position_delimiter.join([str(x) for x in self.positions])
        return _delimiter.join([doc_id, term_frequency, positions])

    def __repr__(self):
        doc_id = str(self.doc_id)
        term_frequency = str(self.term_frequency)
        positions = _position_delimiter.join([str(x) for x in self.positions])
        return _delimiter.join([doc_id, term_frequency, positions])
