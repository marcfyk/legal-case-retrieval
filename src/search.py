from searchengine import Query
from searchengine import ParseError
from searchengine import SearchEngine
from searchengine import load_dictionary
from searchengine import load_documents

postings_file = 'postings.txt'
dictionary_file = 'dictionary.txt'
document_file = 'document.txt'
data_file = 'data/dataset.csv'
q1_file = 'data/q1.txt'
q2_file = 'data/q2.txt'
q3_file = 'data/q3.txt'
results_file = 'output-file-of-results.txt'

def read_query(query_file):
    query = ''
    relevant_doc_ids = []
    with open(query_file, 'r', encoding='utf8') as f:
        query = f.readline().strip()
        line = f.readline()
        while line:
            relevant_doc_ids.append(int(line.strip()))
            line = f.readline()

    print(f'query object: {query}\n')
    print(f'relevant_docs: {relevant_doc_ids}\n')
    return Query.parse(query), relevant_doc_ids

def search_query(query_obj, relevant_doc_ids, search_engine):
    try:
        result = search_engine.search(query_obj, relevant_doc_ids)
        print(f'result: {result}\n')
    except ParseError as e:
        print(f'parse error encountered: {e}')

def search(query_file, search_engine):
    query_obj, relevant_doc_ids = read_query(query_file)
    print()
    search_query(query_obj, relevant_doc_ids, search_engine)
    print()
    print()

dictionary = load_dictionary(dictionary_file)
documents = load_documents(document_file)
search_engine = SearchEngine(dictionary, documents, postings_file)

search(q1_file, search_engine)
search(q2_file, search_engine)
search(q3_file, search_engine)

