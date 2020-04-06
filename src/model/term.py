

class Term:
    
    def __init__(self, term, doc_frequency, file_position):
        self.term = term
        self.doc_frequency = doc_frequency
        self.file_position = file_position

    def __len__(self):
        return len(self.term)

    def __hash__(self):
        return hash(self.term)

    def __repr__(self):
        return f'''
        term: {self.term}\n
        doc_frequency: {self.doc_frequency}\n
        file_position: ({self.file_position})
        '''

class FilePosition:

    def __init__(self, line=-1, offset=-1):
        self.line = line
        self.offset = offset

    def __repr__(self):
        return f'line: {self.line}, offset: {self.offset}'

