

class Term:
    '''
    contains a collection of information:
    doc_frequency -> the total number of documents where the term has occured in.
    line -> the line number the postings list of this term is at.
            this field is for temporary use, and is deleted after indexing to minimize
            storage space.
    offset -> the offset to the postings list of this term. 
    '''
    
    def __init__(self, doc_frequency=0, line=-1, offset=-1):
        self.doc_frequency = doc_frequency
        self.line = line
        self.offset = offset

    def __repr__(self):
        return f' doc_frequency: {self.doc_frequency} offset: {self.offset}'

