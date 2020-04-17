from collections import defaultdict

class Document:

    def __init__(self, title, date_posted, court, length=0):
        self.title = title
        self.date_posted = date_posted
        self.court = court
        self.length = length

    def __repr__(self):
        return f'''
        title: {self.title}\n
        date_posted: {self.date_posted}\n
        court: {self.court}
        '''
