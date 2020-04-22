# Legal Case Retrieval Search Engine

## Indexing
- `dataset-file`: csv file containing all documents to be indexed.
```
python3 index.py -i <dataset-file> -d <dictionary-file> -p <postings-file>
```
Format for csv file: `document id, title, content, date_posted, court`.

The first row in the csv file should not contain any document and should just contain the header fields.

The field `date_posted` should be in the format `YYYY-MM-DD hh:mm:ss`.

## Searching
- `query-file`: containing a single query.
```
python3 search.py -d <dictionary-file> -p <postings-file> -q <query-file> -o <output-file-of-results>
```
