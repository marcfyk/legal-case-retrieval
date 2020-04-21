from functools import reduce
from .booleanretrievalmodel import BooleanRetrievalModel
from .vectorspacemodel import VectorSpaceModel

class SearchEngine:
    '''
    facilitates all searches.

    manages a boolean retrieval model and vector space model to rank searches.
    can search free text or phrasal / boolean queries.
    '''

    def __init__(self, dictionary, documents, postings_file):
        self.dictionary = dictionary
        self.documents = documents
        self.postings_file = postings_file
        self.boolean_retrieval_model = BooleanRetrievalModel(dictionary, postings_file)
        self.vector_space_model = VectorSpaceModel(dictionary, documents, postings_file)

    def search(self, query, relevant_doc_ids):
        terms = query.terms
        if query.is_boolean_query:
            return self._search_boolean(terms, relevant_doc_ids)
        else:
            return self._search_free_text(terms, relevant_doc_ids)

    def _search_boolean(self, terms, relevant_doc_ids):
        boolean_result_set = self.boolean_retrieval_model.retrieve(terms)

        flattened_terms = []
        for term in terms:
            flattened_terms.extend([t.strip() for t in term.split(' ')])

        vector_result = self.vector_space_model.get_ranking(flattened_terms, relevant_doc_ids)
        relevant_doc_set = set(relevant_doc_ids)
        result = [d for d in relevant_doc_ids]
        for r in vector_result:
            if r not in relevant_doc_set and r in boolean_result_set:
                result.append(r)
                boolean_result_set.remove(r)
        for r in boolean_result_set:
            result.append(r)

        return result
        
    def _search_free_text(self, terms, relevant_doc_ids):
        return self.vector_space_model.retrieve(terms, relevant_doc_ids)
