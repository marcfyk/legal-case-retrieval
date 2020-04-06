from collections import defaultdict
from heapq import heapify
from heapq import heappop
from heapq import heappush
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
        for t in existing_terms:
            term_count[t] += 1
        weights = [tf(freq) * idf(len(self.documents), self.dictionary[term].doc_frequency) for term, freq in term_count.items()]

        scores = defaultdict(lambda: 0)
        
        for term, query_weight in zip(existing_terms, weights):
            postings_list = self.get_postings_list(term)
            for posting in postings_list:
                doc_id, term_freq = posting.doc_id, posting.term_frequency
                doc_weight = tf(term_freq)
                scores[doc_id] += doc_weight * query_weight
        
        for doc_id, score in scores.items():
            scores[doc_id] = score / self.documents[doc_id].length

        score_objs = [Score(doc_id, score) for doc_id, score in scores.items()]
        print(score_objs)
        max_score_heap = MaxScoreHeap(score_objs)

        output = []
        while len(max_score_heap):
            output.append(max_score_heap.pop())

        return output


class Score:
    '''
    represents a doc_id and score pairing.
    '''

    def __init__(self, doc_id, score):
        self.doc_id = doc_id
        self.score = score

    def __repr__(self):
        return f'{self.doc_id} : {self.score}'

    def __eq__(self, o):
        return type(o) == Score and self.score == o.score

    def __ne__(self, o):
        return type(o) == Score and self.score != o.score

    def __lt__(self, o):
        return type(o) == Score and self.score < o.score

    def __le__(self, o):
        return type(o) == Score and self.score <= o.score

    def __gt__(self, o):
        return type(o) == Score and self.score > o.score

    def __ge__(self, o):
        return type(o) == Score and self.score >= o.score

class MaxScoreHeap:
    '''
    max heap for score objects
    uses heapq to facilitate most of the logic.
    since heapq is a min heap, scores are negated before being added or
    removed from the max heap to simulate max heap behaviour from heapq.
    '''

    def __init__(self, scores):
        '''
        scores is an array to be heapified.
        '''
        self.scores = [self._negate_score(score) for score in scores]
        heapify(self.scores)

    def _negate_score(self, score):
        score.score = -score.score
        return score

    def pop(self):
        return self._negate_score(heappop(self.scores))

    def push(self, score):
        heappush(self._negate_score(score))

    def __len__(self):
        return len(self.scores)

