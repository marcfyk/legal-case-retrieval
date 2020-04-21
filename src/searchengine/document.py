from copy import deepcopy
from math import sqrt
from heapq import heapify
from heapq import heappop
from heapq import heappush

class Document:
    '''
    Contains meta data and vector of a document.
    data -> list of [title, date_posted, court] lists. 
            the data is a list as there are multiple documents 
            with the same id, but with different [title, date_posted, court] details.
    length -> euclidean distance of the document vector.
    word_count -> counter for the number of words read under this document.
                  the counter allows reading different groups of content tagged under
                  the same id.
                  this field is for temporary use and is deleted at the end of indexing
                  to minimize space.
    vector -> a vector, which axes are represented by terms.
              represented by a dictionary of terms.
              this vector is not normalized. 
              to get the normalized vector, use get_normalized_vector()
    '''

    def __init__(self, data=[], length=0, word_count=0, vector=None):
        self.data = [d for d in data]
        self.length = length
        self.word_count = word_count
        self.vector = deepcopy(vector) if vector else {}

    def add(self, title, date_posted, court):
        '''
        adds [title, date_posted, court]
        '''
        self.data.append([title, date_posted, court])

    def _get_vector_length(self):
        '''
        gets the euclidean distance of a vector.
        '''
        return sqrt(sum([i ** 2 for i in self.vector.values()]))

    def update_vector(self, vector):
        '''
        adds the vector terms and weights to the existing vector.
        '''
        for k, v in vector.items():
            if k not in self.vector:
                self.vector[k] = 0
            self.vector[k] += v
        self.length = self._get_vector_length()

    def get_titles(self):
        '''
        gets a list of titles tagged to this document object.
        '''
        return [title for title, date_posted, court in self.data]

    def get_normalized_vector(self):
        '''
        gets a normalized vector from the vector tagged to this object.
        divides the vector by its euclidean distance.
        '''
        if self.length == 0:
            return 0
        return {k: v / self.length for k, v in self.vector.items()}

    def __repr__(self):
        return f'length: {self.length}, data: {self.data}, vector: {self.vector}'
