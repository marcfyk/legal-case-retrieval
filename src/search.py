from searchengine import Query
from searchengine import ParseError
from searchengine import BooleanRetrievalModel
from searchengine import VectorSpaceModel

import pickle

postings_file = 'postings.txt'
dictionary_file = 'dictionary.txt'
document_file = 'document.txt'
data_file = 'data/dataset.csv'
query_file = ''
results_file = ''

with open(dictionary_file, 'rb') as f:
    dictionary = pickle.load(f)

with open(document_file, 'rb') as f:
    documents = pickle.load(f)

brm = BooleanRetrievalModel(dictionary, postings_file)
vsm = VectorSpaceModel(dictionary, documents, postings_file)

from model.util import stem
while 1:
    query = input('enter query:\n')
    terms = [stem(t) for t in query.split(' ')]
    for t in terms:
        postings_list = vsm.get_postings_list(t)
    print(vsm.retrieve(terms))
    # print(Query.parse(query))
