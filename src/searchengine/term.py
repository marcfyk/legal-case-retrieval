

class Term:
    
    def __init__(self, doc_frequency=0, line=-1, offset=-1):
        self.doc_frequency = doc_frequency
        self.line = line
        self.offset = offset

    def __repr__(self):
        return f' doc_frequency: {self.doc_frequency} offset: {self.offset}'

