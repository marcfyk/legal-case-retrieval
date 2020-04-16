from functools import reduce
from itertools import accumulate

from .util import inverse_accumulate
from .util import union
from .util import within_proximity

import re

_postingslist_delimiter = ' '
_posting_delimiter = '/'
_postingposition_delimiter = ','
_posting_pattern = re.compile(f'^[0-9]*[{_posting_delimiter}][0-9]*[{_posting_delimiter}][0-9]+({_postingposition_delimiter}[0-9]+)*$')

class PostingsList:

    def __init__(self, postings=[]):
        self.postings = [p for p in postings]

    @classmethod
    def parse(cls, postings_list_string):
        '''
        parses a string into a postings list object.
        '''
        posting_strings = postings_list_string.split(_postingslist_delimiter)
        postings_list = PostingsList([Posting.parse(p) for p in posting_strings])
        return postings_list

    @classmethod
    def merge(cls, p1, p2, distance=0):
        '''
        linear merge of two postings lists p1 and p2 into another postings list.
        merge condition:
        -> posting ids are the same
        -> there exist positional indexes from both postings that occur at a certain distance. (|index1 - index2| = distance)
        '''
        i1, i2 = iter(p1), iter(p2)
        output = PostingsList()
        try:
            n1, n2 = next(i1), next(i2)
            while 1:
                id1, id2 = n1.doc_id, n2.doc_id
                if id1 < id2:
                    n1 = next(i1)
                elif id1 > id2:
                    n2 = next(i2)
                else:
                    indexes = within_proximity(n1.positions, n2.positions, distance=distance)
                    if indexes:
                        n = Posting(n2.doc_id, len(indexes), indexes)
                        output.add(n)
                    n1, n2 = next(i1), next(i2)
        except StopIteration:
            return output

    def add(self, posting):
        '''
        adds a posting object to the postings list.
        '''
        if type(posting) is not Posting:
            raise ValueError(f'{posting} is not a Posting object')
        self.postings.append(posting)

    def compress(self):
        '''
        compresses postings list by compressing doc_ids and postings' positional indexes.
        '''
        compressed_doc_ids = inverse_accumulate([p.doc_id for p in self.postings])
        for doc_id, posting in zip(compressed_doc_ids, self.postings):
            posting.doc_id = doc_id
            posting.compress()
        return self

    def decompress(self):
        '''
        decompresses postings list back from compressed state.
        '''
        decompressed_doc_ids = accumulate([p.doc_id for p in self.postings])
        for doc_id, posting in zip(decompressed_doc_ids, self.postings):
            posting.doc_id = doc_id
            posting.decompress()
        return self

    def __len__(self):
        return len(self.postings)

    def __iter__(self):
        for p in self.postings:
            yield p

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return _postingslist_delimiter.join([str(p) for p in self.postings])


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
        if not _posting_pattern.match(posting_string):
            raise ValueError(f'invalid format: {posting_string}')

        doc_id, term_frequency, positions = posting_string.split(_posting_delimiter)
        doc_id, term_frequency, positions = (
                int(doc_id), 
                int(term_frequency), 
                [int(x) for x in positions.split(_postingposition_delimiter) if x != ''])
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
        positions = _postingposition_delimiter.join([str(x) for x in self.positions])
        return _posting_delimiter.join([doc_id, term_frequency, positions])

    def __repr__(self):
        doc_id = str(self.doc_id)
        term_frequency = str(self.term_frequency)
        positions = _postingposition_delimiter.join([str(x) for x in self.positions])
        return _posting_delimiter.join([doc_id, term_frequency, positions])




