from model import Indexer

postingsFile = 'postings.txt'
dictionaryFile = 'dictionary.txt'
documentFile = 'document.txt'
dataFile = 'data/dataset.csv'

open(postingsFile, 'w+').close()
open(dictionaryFile, 'w+').close()
open(documentFile, 'w+').close()

indexer = Indexer(postingsFile, dictionaryFile, documentFile)
indexer.index(dataFile, limit=5)