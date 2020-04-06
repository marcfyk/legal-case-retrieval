from functools import reduce
from .postingslist import PostingsList
from .util import read_line_from_file
from .util import stem

class BooleanRetrievalModel:
    '''
    boolean retieval model.
    '''

    def __init__(self, dictionary, postings_file):
        self.dictionary = dictionary
        self.postings_file = postings_file

    def get_postings_list(self, term):
        '''
        gets the term's postings list.
        returns an empty postings list if term is not in dictionary.
        '''
        if term not in self.dictionary:
            return PostingsList()
        offset = self.dictionary[term].file_position.offset
        line = read_line_from_file(self.postings_file, offset)
        return PostingsList.parse(line).decompress()

    def retrieve(self, terms):
        '''
        retrieves terms from postings list.
        checks if terms are within proximity of each other by using the positional index in
        each postings list of the terms.
        '''
        filtered_terms = [t for t in terms if t in self.dictionary]
        if not filtered_terms:
            return PostingsList()
        merge = PostingsList.merge
        get_postings_list = self.get_postings_list
        postings_lists = [get_postings_list(x) for x in filtered_terms]
        common_postings = reduce(lambda x, y: merge(x, y, distance=1), postings_lists)
        return common_postings

