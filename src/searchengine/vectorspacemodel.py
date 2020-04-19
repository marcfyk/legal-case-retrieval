from heapq import heapify
from heapq import heappop
from heapq import heappush
from math import sqrt
from .postingslist import PostingsList
from .util import read_line_from_file
from .util import tf
from .util import idf

class VectorSpaceModel:
    '''
    vector space model.

    vectors are represented as dictionaries mapping terms to weights. terms not present
    in the dictionary indicates that the weight is zero for that term.

    Therefore document and query vectors are all represented as dictionaries.

    dictionary -> dictionary of term -> term objects
    '''

    def __init__(self, dictionary, documents, postings_file):
        self.dictionary = dictionary
        self.documents = documents
        self.postings_file = postings_file

    def _get_postings_list(self, term):
        '''
        gets the term's postings list.
        returns an empty postings list if term is not in dictionary.
        '''
        if term not in self.dictionary:
            return PostingsList()
        offset = self.dictionary[term].offset
        line = read_line_from_file(self.postings_file, offset)
        return PostingsList.parse(line).decompress()

    def _build_query_vector(self, terms):
        '''
        builds a query vector from the given terms.
        weights of the vector are derived from tf_idf weighting.
        '''
        vector = {}
        existing_terms = [t for t in terms if t in self.dictionary]
        for t in existing_terms:
            if t not in vector:
                vector[t] = 0
            vector[t] += 1
        for t, f in vector.items():
            tf_idf = tf(f) * idf(len(self.documents), self.dictionary[t].doc_frequency)
            vector[t] = tf_idf if tf_idf >= 0 else 0
        return vector

    def _build_centroid(self, vectors):
        '''
        returns a centroid of a list of vectors.
        '''
        centroid_vector = {}
        for vector in vectors:
            for t, w in vector.items():
                if t not in centroid_vector:
                    centroid_vector[t] = 0
                centroid_vector[t] += w
        for t, w in centroid_vector.items():
            centroid_vector = w / len(vectors)
        return centroid_vector

    def _build_adjusted_query(self, query_vector, centroid):
        '''
        returns an adjusted vector calculated from a query vector and a centroid.
        '''
        query_coefficient = 0.5
        centroid_coefficient = 0.5
        vector = {}
        for t, w in query_vector.items():
            if t not in vector:
                vector[t] = 0
            vector[t] += query_coefficient * w
        for t, w in centroid.items():
            if t not in vector:
                vector[t] = 0
            vector[t] += centroid_coefficient * w
        return vector

    def _build_adjusted_vector_query(self, query_vector, relevant_doc_ids=[]):
        vectors = [self.documents[doc_id].vector for doc_id in relevant_doc_ids if doc_id in self.documents]
        print(f'vectors: {vectors}')
        centroid = self._build_centroid(vectors)
        print(f'centroid: {centroid}')
        adjusted_vector = self._build_adjusted_query(query_vector, centroid)
        return adjusted_vector

    def retrieve(self, terms, relevant_doc_ids=[]):
        '''
        retrieves a ranked list of documents from searching the given terms.
        '''
        print(f'vector space search on {terms}')
        query_vector = self._build_query_vector(terms)
        print(f'original vector: {query_vector}')

        if relevant_doc_ids:
            query_vector = self._build_adjusted_vector_query(query_vector, relevant_doc_ids)
            print(f'adjusted vector: {query_vector}')
        
        return self.rank(query_vector, relevant_doc_ids)

    def rank(self, query_vector, relevant_doc_ids):
        '''
        ranks doc ids with the given query vector using cosine scoring.
        '''
        scores = {}
        for term, query_weight in query_vector.items():
            postings_list = self._get_postings_list(term)
            for posting in postings_list:
                doc_id, term_freq = posting.doc_id, posting.term_frequency
                doc_weight = tf(term_freq)
                if doc_id not in scores:
                    scores[doc_id] = 0
                scores[doc_id] += doc_weight * query_weight
        
        for doc_id, score in scores.items():
            print(doc_id, score, doc_id in self.documents)
            scores[doc_id] = score / self.documents[doc_id].length

        score_objs = [Score(doc_id, score) for doc_id, score in scores.items()]
        max_score_heap = MaxScoreHeap(score_objs)

        output = [doc_id for doc_id in relevant_doc_ids]
        top_results = set(relevant_doc_ids)
        while len(max_score_heap):
            next_score = max_score_heap.pop()
            print(f'score: {next_score}')
            if next_score.doc_id not in top_results:
                output.append(next_score.doc_id)

        return output

class Score:
    '''
    represents a doc_id and score pairing.
    ordering is defined to facilitate MaxScoreHeap operations.
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

