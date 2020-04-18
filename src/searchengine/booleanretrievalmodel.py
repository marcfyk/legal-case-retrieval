from functools import reduce
from .postingslist import PostingsList
from .util import read_line_from_file
from .util import stem

class BooleanRetrievalModel:
    '''
    boolean retieval model.
    retrieves a list of doc ids that match the terms it is given.
    if a term is a phrase, the terms relative positioning is enforced when filtering doc ids.
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
        offset = self.dictionary[term].offset
        line = read_line_from_file(self.postings_file, offset)
        return PostingsList.parse(line).decompress()

    def retrieve(self, terms):
        '''
        retrieves terms from postings list.
        checks if terms are within proximity of each other by using the positional index in
        each postings list of the terms.
        '''
        print(f'boolean search on {terms}')
        merge = PostingsList.merge
        get_postings_list = self.get_postings_list
        postings_lists = [get_postings_list(t) for t in terms]
        result_postings_list = reduce(lambda x, y: merge(x, y, distance=1), postings_lists)
        return [p.doc_id for p in result_postings_list]

