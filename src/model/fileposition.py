
class FilePosition:

    def __init__(self, line=-1, offset=-1):
        self.line = line
        self.offset = offset

    def __repr__(self):
        return f'''line: {self.line}, offset: {self.offset}'''
