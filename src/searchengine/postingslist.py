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
    '''
    represents a postings list, which a list of posting objects.
    each posting in a postings list contains doc_id, term_frequency and a list of positional indexes.
    postings list represents a term from the dictionary.
    postings lists are compressed when written to disk, using gap encoding.
    when postings lists are read from disk, they are decompressed.

    postings -> list of posting objects.
    '''

    def __init__(self, postings=[]):
        self.postings = [p for p in postings]

    @classmethod
    def parse(cls, postings_list_string):
        '''
        parses a string into a postings list object.
        the string should be a compressed postings list.
        the output is the decompressed postings list.
        '''
        posting_strings = postings_list_string.split(_postingslist_delimiter)
        postings_list = PostingsList([Posting.parse(p) for p in posting_strings])
        return postings_list

    @classmethod
    def merge(cls, p1, p2, distance):
        '''
        linear merge of two postings lists p1 and p2 into another postings list.
        merge condition:
        -> posting ids are the same
        -> there exist positional indexes from both postings that occur at a certain distance. (|index1 - index2| = distance)

        example: 
        suppose t1 is the term with postings list p1, and t2 is the term with postings list p2.
        merge(p1, p2, 1) returns a postings list of doc ids where t2 occurs immediately after t1.
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
                    indexes = within_proximity(n1.positions, n2.positions, distance)
                    if indexes:
                        n = Posting(n2.doc_id, term_frequency=len(indexes), positions=indexes)
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
        compresses postings list by compressing doc_ids and postings' positional indexes using gap encoding.
        '''
        compressed_doc_ids = inverse_accumulate([p.doc_id for p in self.postings])
        for doc_id, posting in zip(compressed_doc_ids, self.postings):
            posting.doc_id = doc_id
            posting.compress()
        return self

    def decompress(self):
        '''
        decompresses postings list back from compressed state, reversing the gap encoding.
        '''
        decompressed_doc_ids = accumulate([p.doc_id for p in self.postings])
        for doc_id, posting in zip(decompressed_doc_ids, self.postings):
            posting.doc_id = doc_id
            posting.decompress()
        return self

    def __len__(self):
        '''
        returns the number of postings in this postings list.
        '''
        return len(self.postings)

    def __iter__(self):
        '''
        iterates through all postings in this postings list.
        '''
        for p in self.postings:
            yield p

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return _postingslist_delimiter.join([str(p) for p in self.postings])


class Posting:
    '''
    represents a collection of data:
    doc_id -> id of the document it represents.
    term_frequency -> how often this term occurs in document of doc_id.
    positions -> zero-based positional indexes of where this term occurs in document of doc_id.

    similar to postings list, the positional indexes are compressed with gap encoding.
    '''

    def __init__(self, doc_id, term_frequency=0, positions=[]):
        self.doc_id = doc_id
        self.term_frequency = term_frequency
        self.positions = [p for p in positions]

    @classmethod
    def parse(cls, posting_string):
        '''
        parses a string into a posting.
        string should be of a compressed posting.
        output is the decompressed posting.
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
        compresses posting's positional indexes with gap encoding.
        '''
        self.positions = inverse_accumulate(self.positions)
        return self

    def decompress(self):
        '''
        decompresses posting by reversing the gap encoding.
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




