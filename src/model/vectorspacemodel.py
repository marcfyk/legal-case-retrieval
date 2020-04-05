from collections import defaultdict
from .postingslist import PostingsList
from .util import read_line_from_file
from .util import tf
from .util import idf

class VectorSpaceModel:
    '''
    vector space model.
    '''

    def __init__(self, dictionary, documents, postings_file):
        self.dictionary = dictionary
        self.documents = documents
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
        term_count = defaultdict(lambda: 0)
        existing_terms = [t for t in terms if t in self.dictionary]
        term_objs = [self.dictionary[t] for t in terms if t in self.dictionary]
        for t in term_objs:
            term_count[t] += 1
        weights = [tf(freq) * idf(len(self.documents), term.doc_frequency) for term, freq in term_count.items()]

        scores = defaultdict(lambda: 0)

        for term, weight in zip(term_objs, weights):
            postings_list = self.get_postings_list(term)
            for posting in postings_list:
                doc_id, term_freq = posting.doc_id, posting.term_frequency
                doc_weight = tf(term_freq)
                scores[doc_id] += postings
                pass
        
        for doc_id, score in scores.items():
            scores[doc_id] = score / self.documents[doc_id].length

        for doc_id, score in scores.items():
            print(f'{doc_id} : {score}')

        return scores