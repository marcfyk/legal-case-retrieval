#!/usr/bin/python3
from searchengine import Query
from searchengine import ParseError
from searchengine import SearchEngine
from searchengine import load_dictionary
from searchengine import load_documents

import getopt
import sys

def read_query(query_file):
    query = ''
    relevant_doc_ids = []
    with open(query_file, 'r', encoding='utf8') as f:
        query = f.readline().strip()
        line = f.readline()
        while line:
            relevant_doc_ids.append(int(line.strip()))
            line = f.readline()
    return Query.parse(query), relevant_doc_ids

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    print(f'usage: {sys.argv[0]} -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results')
    sys.exit(2)

dictionary_file = None
postings_file = None
query_file = None
results_file = None

for x, y in opts:
    if x == '-d':
        dictionary_file = y
    elif x == '-p':
        postings_file = y
    elif x == '-q':
        query_file = y
    elif x == '-o':
        results_file = y
    else:
        raise AssertionError('unhandled option')

if dictionary_file == None or postings_file == None or query_file == None or results_file == None:
    print(f'usage: {sys.argv[0]} -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results')
    sys.exit(2)

document_file = 'document.txt'
dictionary = load_dictionary(dictionary_file)
documents = load_documents(document_file)
search_engine = SearchEngine(dictionary, documents, postings_file)
query, relevant_doc_ids = read_query(query_file)

with open(results_file, 'w') as f:
    f.seek(0)
    try:
        result = search_engine.search(query, relevant_doc_ids)
        f.write(' '.join([str(i) for i in result]) + '\n')
    except ParseError as e:
        f.write(f'parse error encountered: {e}')

