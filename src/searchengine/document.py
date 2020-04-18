from collections import defaultdict

class Document:

    def __init__(self, data=[], length=0, word_count=0):
        self.data = [d for d in data]
        self.length = length
        self.word_count = word_count

    def add(self, title, date_posted, court):
        self.data.append([title, date_posted, court])

    def __repr__(self):
        return f'''length: {self.length}, word_count: {self.word_count}\ndata: {self.data}'''

