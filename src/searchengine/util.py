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

def inverse_accumulate(numbers):
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

def interleave(iterables, stop_early=False):
    '''
    generates the result of interleaving a list of iterables, 
    stop_early determines if generator stops when the first iterable is exhausted or
    when all iterables are exhausted.
    stop_early: True -> stop when first iterable is exhausted
    stop_early: False -> stop when all iterables are exhausted
    '''
    if stop_early:
        return _interleave_min(iterables)
    else:
        return _interleave_max(iterables)

def _interleave_min(iterables):
    '''
    interleaves and generates a list of iterables, 
    and stops when the first iterable has been exhausted.
    '''
    if not len(iterables):
        return
    iterators = [iter(i) for i in iterables]
    while 1:
        for i in iterators:
            try:
                yield next(i)
            except StopIteration:
                return

def _interleave_max(iterables):
    '''
    interleaves and generates a list of iterables, 
    stops only when all iterables have been exhausted.
    '''
    if not len(iterables):
        return
    iterators = [iter(i) for i in iterables]
    status = [1 for i in iterators]
    counter = len(status)
    while 1:
        if counter == 0:
            return
        for i in range(len(iterators)):
            try:
                yield next(iterators[i])
            except StopIteration:
                if status[i] == 1:
                    counter -= 1
                    status[i] = 0
                continue

def union(l1, l2):
    '''
    returns a list containing all elements from l1 and l2.
    l1 and l2 must be sorted before calling this function.
    '''
    output = []
    iter1, iter2 = iter(l1), iter(l2)
    try:
        n1, n2 = next(iter1), next(iter2)
        while 1:
            if n1 < n2:
                n1 = next(iter1)
            elif n1 > n2:
                n2 = next(iter2)
            else:
                output.append(n2)
                n1, n2 = next(iter1), next(iter2)
    except StopIteration:
        return output
    return output

def within_proximity(l1, l2, distance=0):
    '''
    checks if there are any elements in l1 and l2, i and j,
    where difference between |i - j| = distance.
    '''
    shifted_l1 = [i + distance for i in l1]
    match = union(shifted_l1, l2)
    return match

