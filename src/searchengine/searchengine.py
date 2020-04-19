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

    def search(self, query, relevant_doc_ids=[]):
        terms = query.terms

        if query.is_boolean_query:
            boolean_result = [set(self.boolean_retrieval_model.retrieve(t)) for t in terms]
            if all(boolean_result):
                boolean_result = reduce(lambda x, y: x.intersection(y), boolean_result[1:], boolean_result[0])
            else:
                boolean_result = set()

            flattened_terms = []
            for term in terms:
                flattened_terms.extend([t.strip() for t in term.split(' ')])
            vector_result = self.vector_space_model.retrieve(flattened_terms, relevant_doc_ids)
            matches = set(relevant_doc_ids).union(boolean_result)
            result = [doc_id for doc_id in relevant_doc_ids]
            result.extend([doc_id for doc_id in vector_result if doc_id in matches])
            return result
        else:
            return self.vector_space_model.retrieve(terms, relevant_doc_ids)

