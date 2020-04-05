from model import Query
from model import ParseError
from model import BooleanRetrievalModel

import pickle

postings_file = 'postings.txt'
dictionary_file = 'dictionary.txt'
document_file = 'document.txt'
data_file = 'data/dataset.csv'
query_file = ''
results_file = ''

with open(dictionary_file, 'rb') as f:
    dictionary = pickle.load(f)

brm = BooleanRetrievalModel(dictionary, postings_file)

for k, v in dictionary.items():
    print(f'{k} : {v}')

from model.util import stem
while 1:
    query = input('enter query:\n')
    terms = [stem(t) for t in query.split(' ')]
    # for t in terms:
    #     print(brm.get_postings_list(t))
    print(brm.retrieve(terms))
    # print(Query.parse(query))
