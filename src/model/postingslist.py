from .posting import Posting
from .util import accumulate

class PostingsList:
    delimiter = ' '

    def __init__(self, postings=[], is_compressed=False):
        self._latest_id = 0
        if not is_compressed:
            doc_ids = accumulate([p.doc_id for p in postings])
            for doc_id, posting in zip(doc_ids, postings):
                posting.doc_id = doc_id
        self.postings = [p for p in postings]

    @classmethod
    def parse(cls, postings_list_string, is_compressed=False):
        posting_strings = postings_list_string.split(PostingsList.delimiter)
        return PostingsList([Posting.parse(p, is_compressed) for p in posting_strings], is_compressed)

    def add(self, posting, is_compressed=False):
        if type(posting) is not Posting:
            raise ValueError(f'{posting} is not a Posting object')
        if not is_compressed:
            posting.doc_id -= self._latest_id
        self.postings.append(posting)
        self._latest_id += posting.doc_id
    
    def __len__(self):
        return len(self.postings)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return PostingsList.delimiter.join([str(p) for p in self.postings])
