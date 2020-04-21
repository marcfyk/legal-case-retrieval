from copy import deepcopy
from math import sqrt
from heapq import heapify
from heapq import heappop
from heapq import heappush

class Document:

    def __init__(self, data=[], length=0, word_count=0, vector=None):
        self.data = [d for d in data]
        self.length = length
        self.word_count = word_count
        self.vector = deepcopy(vector) if vector else {}

    def add(self, title, date_posted, court):
        self.data.append([title, date_posted, court])

    def _get_vector_length(self):
        return sqrt(sum([i ** 2 for i in self.vector.values()]))

    def update_vector(self, vector):
        for k, v in vector.items():
            if k not in self.vector:
                self.vector[k] = 0
            self.vector[k] += v
        self.length = self._get_vector_length()

    def get_titles(self):
        return [title for title, date_posted, court in self.data]

    def get_normalized_vector(self):
        if self.length == 0:
            return 0
        return {k: v / self.length for k, v in self.vector.items()}

    def __repr__(self):
        return f'length: {self.length}, data: {self.data}, vector: {self.vector}'
