# Legal Case Retrieval Search Engine

## Indexing
- `dataset-file`: csv file containing all documents to be indexed.
```
python3 index.py -i <dataset-file> -d <dictionary-file> -p <postings-file>
```

## Searching
- `query-file`: containing a single query.
```
python3 search.py -d <dictionary-file> -p <postings-file> -q <query-file> -o <output-file-of-results>
```
