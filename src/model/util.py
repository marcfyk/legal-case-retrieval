from math import log10
from nltk import PorterStemmer

porter_stemmer = PorterStemmer()

def tf(f):
    return 1 + log10(f)

def idf(n, d):
    return log10(n / d)

def stem(word):
    return porter_stemmer.stem(word.casefold())

def has_any_alphanumeric(word):
    for c in word:
        if c.isalnum():
            return True
    return False
