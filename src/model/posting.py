from itertools import starmap
from operator import sub

from .util import accumulate

import re

_delimiter = '/'
_position_delimiter = ','
_pattern = re.compile(f'^[0-9]*[{_delimiter}][0-9]*[{_delimiter}][0-9]+({_position_delimiter}[0-9]+)*$')

class Posting:

    def __init__(self, doc_id, term_frequency, positions=[], is_compressed=False):
        self.doc_id = doc_id
        self.term_frequency = term_frequency
        self.positions = []
        if is_compressed:
            self.positions = [p for p in positions]
        else:
            self.positions = accumulate(positions)

    @classmethod
    def parse(cls, posting_string, is_compressed=False):
        if not _pattern.match(posting_string):
            raise ValueError(f'invalid format: {posting_string}')

        doc_id, term_frequency, positions = posting_string.split(_delimiter)
        doc_id, term_frequency, positions = (
                int(doc_id), 
                int(term_frequency), 
                [int(x) for x in positions.split(_position_delimiter) if x != ''])

        return Posting(doc_id, term_frequency, positions, is_compressed)
    
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
