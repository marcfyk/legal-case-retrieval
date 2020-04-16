from searchengine import Query
from searchengine import ParseError
from searchengine import SearchEngine

import pickle

postings_file = 'postings.txt'
dictionary_file = 'dictionary.txt'
document_file = 'document.txt'
data_file = 'data/dataset.csv'
query_file = 'data/q1.txt'
results_file = ''

def read_query(query_file):
    query = ''
    relevant_doc_ids = []
    with open(query_file, 'r') as f:
        query = f.readline().strip()
        line = f.readline()
        while line:
            relevant_doc_ids.append(int(line.strip()))
            line = f.readline()
    print(f'query: {query}')
    print(f'relevant_docs: {relevant_doc_ids}')
    return Query.parse(query), relevant_doc_ids

with open(dictionary_file, 'rb') as f:
    dictionary = pickle.load(f)

with open(document_file, 'rb') as f:
    documents = pickle.load(f)

query, relevant_doc_ids = read_query(query_file)
print(f'query object:\n{query}')
search_engine = SearchEngine(dictionary, documents, postings_file)
try:
    result = search_engine.free_text_query(query.free_text, relevant_doc_ids)
except ParseError as e:
    print(f'parse error encountered: {e}')
