#!/usr/bin/python3
import re
import nltk
import sys
import getopt

from os import path

from searchengine import Indexer

postingsFile = 'postings.txt'
dictionaryFile = 'dictionary.txt'
documentFile = 'document.txt'
dataFile = 'data/dataset.csv'

open(postingsFile, 'w+', encoding='utf8').close()
open(dictionaryFile, 'w+', encoding='utf8').close()
open(documentFile, 'w+', encoding='utf8').close()

indexer = Indexer(postingsFile, dictionaryFile, documentFile)
indexer.index(dataFile)

