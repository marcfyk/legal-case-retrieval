from functools import reduce
from heapq import heapify
from heapq import heappop
from heapq import heappush
from math import sqrt
from .postingslist import PostingsList
from .util import read_line_from_file
from .util import tf
from .util import idf
from .util import stem
from .util import get_synonyms

class VectorSpaceModel:
    '''
    vector space model.

    vectors are represented as dictionaries mapping terms to weights. terms not present
    in the dictionary indicates that the weight is zero for that term.

    Therefore document and query vectors are all represented as dictionaries.

    dictionary -> dictionary of term -> term objects
    documents -> dictionary of doc_id -> doc objects
    postings_file -> file containing postings lists
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

    def _build_centroid_vector(self, doc_ids):
        '''
        returns a centroid of a list of vectors mapped from doc ids.
        '''
        vectors = [self.documents[d].get_normalized_vector() for d in doc_ids if d in self.documents]
        centroid_vector = {}
        for vector in vectors:
            for t, w in vector.items():
                if t not in centroid_vector:
                    centroid_vector[t] = 0
                centroid_vector[t] += w
        for t, w in centroid_vector.items():
            centroid_vector[t] = w / len(vectors)
        return centroid_vector

    def _adjust_vector(self, query_vector, centroid, query_coefficient, centroid_coefficient):
        '''
        returns an adjusted vector calculated from a query vector and a centroid.
        query_coefficient and centroid_coefficient dictates which vector has a stronger influence
        on the resultant vector.
        '''
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

    def _apply_relevance_feedback(self, query_vector, relevant_doc_ids):
        '''
        applies Rocchio (1971) algorithm -> 0.5 query_vector + 0.5 centroid
        where centroid is calculated from relevant doc ids' vectors.
        '''
        centroid_vector = self._build_centroid_vector(relevant_doc_ids)
        adjusted_vector = self._adjust_vector(query_vector, centroid_vector, 0.5, 0.5)
        return adjusted_vector

    def _apply_pseudo_relevance_feedback(self, query_vector, assumed_relevant_doc_ids):
        '''
        applies Rocchio (1971) algorithm -> 0.8 query_vector + 0.2 centroid
        where centroid is calculated from assumed relevant doc ids' vectors.
        '''
        centroid_vector = self._build_centroid_vector(assumed_relevant_doc_ids)
        adjusted_vector = self._adjust_vector(query_vector, centroid_vector, 0.8, 0.2)
        return adjusted_vector

    def _expand_query_vector(self, query_vector):
        '''
        expands the query vector by adding synonyms to each term.
        synonyms will have the same weight of the term they are derived from.
        if synonyms are derived from more than one term, 
        they have the average weight of their derived terms.
        '''
        expanded_terms = {}
        for term in query_vector:
            synonyms = get_synonyms(term)
            for s in synonyms:
                if s not in expanded_terms:
                    expanded_terms[s] = []
                expanded_terms[s].append(term)
        for synonym, terms in expanded_terms.items():
            weights = [query_vector[t] for t in terms]
            average_weight = sum(weights) / len(weights)
            query_vector[synonym] = average_weight
        return query_vector

    def get_ranking(self, terms, relevant_doc_ids):
        '''
        returns a ranked list of document ids from the a free text query, given relevant doc ids
        from relevance judgements.

        the query vector is refined with relevance feedback, apply Rocchio (1971) algorithm.
        no query expansion and no pseudo relevance feedback so applied to the vector.
        '''
        query_vector = self._build_query_vector(terms)
        if relevant_doc_ids:
            query_vector = self._apply_relevance_feedback(query_vector, relevant_doc_ids)
        result = self._rank(query_vector, relevant_doc_ids)
        return result

    def retrieve(self, terms, relevant_doc_ids):
        '''
        retrieves a ranked list of document ids from searching the given free text terms,
        given relevant doc ids from relevance judgements.

        the query vector is refined with relevance feedback first.
        then query expansion with wordnet is applied.
        an initial ranking of documents is obtained.
        after that, if the size of relevance judgements, |R| < 10, the top (10 - |R|) documents from
        the initial ranking are assumed as relevant and used for pseudo relevance feedback.

        then another ranking is done on the query vector and returned.
        '''        
        query_vector = self._build_query_vector(terms)

        if relevant_doc_ids:
            query_vector = self._apply_relevance_feedback(query_vector, relevant_doc_ids)

        query_vector = self._expand_query_vector(query_vector)

        relevant_feedback_total_size = 10
        relevant_size = len(relevant_doc_ids)
        assumed_relevant_size = max(0, relevant_feedback_total_size - relevant_size)
        result = self._rank(query_vector, relevant_doc_ids)
        assumed_relevant_doc_ids = result[relevant_size:relevant_size+assumed_relevant_size]
        if assumed_relevant_doc_ids:
            query_vector = self._apply_relevance_feedback(query_vector, assumed_relevant_doc_ids)
            result = self._rank(query_vector, relevant_doc_ids)

        return result

    def _rank(self, query_vector, relevant_doc_ids):
        '''
        ranks doc ids with the given query vector using cosine scoring.
        relevant doc ids are ranked at the top regardless of score.
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
            scores[doc_id] = score / self.documents[doc_id].length

        score_objs = [Score(doc_id, score) for doc_id, score in scores.items()]
        max_score_heap = MaxScoreHeap(score_objs)

        output = [doc_id for doc_id in relevant_doc_ids]
        top_results = set(relevant_doc_ids)
        while len(max_score_heap):
            next_score = max_score_heap.pop()
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
        scores is an array to be transformed into a max heap.
        '''
        self.scores = [self._negate_score(score) for score in scores]
        heapify(self.scores)

    def _negate_score(self, score):
        '''
        negates the score, so that numerically, the behaviour of the
        heapq simulates a max heap.
        '''
        score.score = -score.score
        return score

    def pop(self):
        '''
        returns the largest score in the max heap.
        '''
        return self._negate_score(heappop(self.scores))

    def push(self, score):
        '''
        adds the score to the max heap.
        '''
        heappush(self._negate_score(score))

    def __len__(self):
        '''
        returns the number of scores in the max heap.
        '''
        return len(self.scores)

