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
    '''
    checks if a word contains >= 1 alphanumeric character.
    '''
    for c in word:
        if c.isalnum():
            return True
    return False

def accumulate(numbers):
    '''
    takes in a list X and returns a list Y,
    where for a valid index i, X[i] == sum of all elements from Y[0] to Y[i] (inclusive)
    [1,2,5] -> [1, 1, 3]
    '''
    output = []
    total = 0
    for i in range(len(numbers)):
        delta = numbers[i] - total
        output.append(delta)
        total += delta
    return output

def read_line_from_file(file_name, ptr):
    '''
    reads a line from a file given a ptr (offset).
    '''
    with open(file_name, 'a+') as f:
        f.seek(ptr)
        line = f.readline()
    return line

def get_line_pointers(file_name):
    '''
    returns a list of pointers (offsets) in a file,
    where each pointer points to the start of a new line.
    an empty file will return [0], and if the file doesn't exist,
    the file will be created.
    '''
    ptrs = [0]
    with open(file_name, 'a+') as f:
        f.seek(0)
        line = f.readline()
        while line:
            ptrs.append(f.tell())
            line = f.readline()
    return ptrs

