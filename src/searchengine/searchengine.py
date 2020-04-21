from functools import reduce
from .booleanretrievalmodel import BooleanRetrievalModel
from .vectorspacemodel import VectorSpaceModel

class SearchEngine:
    '''
    facilitates all searches.
    manages a boolean retrieval model and vector space model to rank searches.
    can search free text or phrase / boolean queries.

    dictionary -> dictionary of term -> term object containing information.
    documents -> dictionary of doc_id -> document object containing meta data and vectors.
    postings_file -> file to read postings list from.
    boolean_retrieval_model -> model to run boolean queries on.
    vector_space_model -> model to run free text queries on.
    '''

    def __init__(self, dictionary, documents, postings_file):
        self.dictionary = dictionary
        self.documents = documents
        self.postings_file = postings_file
        self.boolean_retrieval_model = BooleanRetrievalModel(dictionary, postings_file)
        self.vector_space_model = VectorSpaceModel(dictionary, documents, postings_file)

    def search(self, query, relevant_doc_ids):
        '''
        runs a search on the given query, given the relevant_doc_ids
        from relevance judgements.
        if a query is a boolean query, run it on the boolean retrieval model.
        if not, run it on the vector space model.
        '''
        terms = query.terms
        if query.is_boolean_query:
            return self._search_boolean(terms, relevant_doc_ids)
        else:
            return self._search_free_text(terms, relevant_doc_ids)

    def _search_boolean(self, terms, relevant_doc_ids):
        '''
        obtains a set of docids from running the terms on the boolean retrieval model.
        then flatten the terms and run a free text search on the vector space model for ranking order.
        then filter the ranked result against the docids from the boolean retrieval model search.
        relevant doc ids from relevance judgements are ranked at the top.
        '''
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
        '''
        runs a search on terms in the vector space model, returning a list of ranked doc ids.
        '''
        return self.vector_space_model.retrieve(terms, relevant_doc_ids)
