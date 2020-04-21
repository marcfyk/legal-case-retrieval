#!/usr/bin/python3
from searchengine import Indexer

import getopt
import sys

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    print(f'usage: {sys.argv[0]} -i dataset-file -d dictionary-file -p postings-file')
    sys.exit(2)

for x, y in opts:
    if x == '-i':
        data_file = y
    elif x == '-d':
        dictionary_file = y
    elif x == '-p':
        postings_file = y
    else:
        raise AssertionError('unhandled option')

if not all([data_file, dictionary_file, postings_file]):
    print(f'usage: {sys.argv[0]} -i dataset-file -d dictionary-file -p postings-file')
    sys.exit(2)

document_file = 'document.txt'
open(postings_file, 'w+', encoding='utf8').close()
open(dictionary_file, 'w+', encoding='utf8').close()
open(document_file, 'w+', encoding='utf8').close()

indexer = Indexer(postings_file, dictionary_file, document_file)
indexer.index(data_file)
