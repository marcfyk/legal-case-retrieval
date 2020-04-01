import re

class Posting:
    pattern = re.compile('^[0-9]*[/][0-9]*$')
    delimiter = '/'

    def __init__(self, doc_id, term_frequency):
        self.doc_id = doc_id
        self.term_frequency = term_frequency

    @classmethod
    def parse(cls, posting_string):
        if not cls.pattern.match(posting_string):
            raise ValueError(f'invalid format: {posting_string}')
        doc_id, term_frequency = [int(x) for x in posting_string.split(cls.delimiter)]
        return Posting(doc_id, term_frequency)
    
    def __str__(self):
        return f'{self.doc_id}{Posting.delimiter}{self.term_frequency}'

    def __repr__(self):
        return f'{self.doc_id}{Posting.delimiter}{self.term_frequency}'

