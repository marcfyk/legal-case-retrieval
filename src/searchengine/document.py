
class Document:

    def __init__(self, doc_id, title, date_posted, court, length=0):
        self.doc_id = doc_id
        self.title = title
        self.date_posted = date_posted
        self.court = court
        self.length = length

    def __hash__(self):
        return hash(self.doc_id)
    
    def __repr__(self):
        return f'''
        id: {self.doc_id}\n
        title: {self.title}\n
        date_posted: {self.date_posted}\n
        court: {self.court}
        '''