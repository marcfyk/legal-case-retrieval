from functools import reduce
from .booleanretrievalmodel import BooleanRetrievalModel
from .vectorspacemodel import VectorSpaceModel

class SearchEngine:

    def __init__(self, dictionary, documents, postings_file):
        self.dictionary = dictionary
        self.documents = documents
        self.postings_file = postings_file
        self.brm = BooleanRetrievalModel(dictionary, postings_file)
        self.vsm = VectorSpaceModel(dictionary, documents, postings_file)

    def search(self, query, relevent_doc_ids):
        free_text = query.free_text
        phrases = query.phrases
        phrases_result = self.phrase_query(phrases)
        free_text_result = self.free_text_query(free_text, relevent_doc_ids)
        result = [doc_id for doc_id in free_text_result if doc_id in phrases_result]
        return result

    def free_text_query(self, free_text_terms, relevent_doc_ids=[]):
        return self.vsm.retrieve(free_text_terms, relevent_doc_ids)
        
    def phrase_query(self, phrases):
        phrase_terms = [p.split(' ') for p in phrases]
        phrase_results = [set(self.brm.retrieve(terms)) for terms in phrase_terms]
        if phrase_results and all(phrase_results):
            return reduce(lambda x, y: x.intersection(y), phrase_results[1:], set(phrase_results[0]))
        else:
            return set()
