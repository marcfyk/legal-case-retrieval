from functools import reduce
from .postingslist import PostingsList
from .util import read_line_from_file
from .util import stem

class BooleanRetrievalModel:
    '''
    boolean retieval model.
    retrieves a set of doc ids that match the terms it is given.
    if a term is a phrase, the terms positioning is enforced when filtering doc ids.

    dictionary -> dictionary of terms which holds data to allow retrieval of the postings lists.
    postings_file -> file to read from to obtain postings lists.
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

    def retrieve(self, tokens):
        '''
        retrieves a set of document ids by searching each token
        and taking the intersection of each result in each token,
        where each token can be a single term or a phrase.
        '''
        output = [set(self._search_token(t)) for t in tokens]
        if output:
            return reduce(lambda x, y: x.intersection(y), output[1:], output[0])
        else:
            return set()


    def _search_token(self, token):
        '''
        gets the results from searching the token in the boolean retrieval model.
        the token can either be a phrase or a single term.
        '''
        is_phrase = len(token.strip().split(' ')) > 1
        if is_phrase:
            return self._search_phrase(token)
        else:
            return self._search_term(token)

    def _search_phrase(self, phrase):
        '''
        gets the result of searching the phrase in the boolean retrieval model.
        the postings lists are obtained for each term in the phrase.
        then, they are merged from left to right, checking for proximity of 1.
        this reduction ensures the positions of the terms in the phrase are enforced 
        when finding matching document ids.
        '''
        phrase_terms = [t.strip().casefold() for t in phrase.split(' ')]
        postings_lists = [self.get_postings_list(t) for t in phrase_terms]
        result = reduce(lambda x, y: PostingsList.merge(x, y, 1), postings_lists)
        return [p.doc_id for p in result]

    def _search_term(self, term):
        '''
        gets the result of searching the term in the boolean retrieval model.
        '''
        postings_list = self.get_postings_list(term)
        return [p.doc_id for p in postings_list]