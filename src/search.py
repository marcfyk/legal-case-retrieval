from model import Query
from model import ParseError

postings_file = 'postings.txt'
dictionary_file = 'dictionary.txt'
document_file = 'document.txt'
data_file = 'data/dataset.csv'
query_file = ''
results_file = ''

while 1:
    query = input('enter query:\n')
    print(Query.parse(query))
