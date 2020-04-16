from .util import stem

import re

single_quote = '\''
double_quote = '"'
and_operator = 'AND'

class Query:
    '''
    represents a query, containing two fields: free_text and phrases.
    These represent what is to be queried as a free text search on a vector space model,
    and what is to be searched as a phrase query on a boolean retrieval model.

    free_text: list of tokens to be queried via vector space model.
    phrases: list of phrases to be queried in conjunction via boolean retrieval model.
    '''

    def __init__(self, free_text=[], phrases=[]):
        self.free_text = [t for t in free_text]
        self.phrases = [t for t in phrases]

    @classmethod
    def parse(cls, query):
        '''
        parses a query string into a Query object. If there are any format errors, a ParseError is
        raised along with a message.
        '''

        # for simplicity, queries should not have single quotes.
        if single_quote in query:
            raise ParseError(f'please use ({double_quote}) quotes instead of ({single_quote}) quotes')

        # checks if quotes are matching (every opening quote has a closing quote) and assuming there are no
        # nested quotes
        if query.count(double_quote) % 2 == 1:
            raise ParseError(f'unmatching quotes detected in {query}')

        tokens = [t.strip() for t in query.split(double_quote)] 

        if len(tokens) == 1:
            if and_operator in tokens[0]:
                raise ParseError(f'improper use of {and_operator} operator in query: {tokens[0]}')
            free_text_tokens = [stem(t) for t in tokens[0].split(' ')]
            return Query(free_text=free_text_tokens)

        q = Query()
        for i in range(len(tokens)):
            t = tokens[i]
            if t == '':
                continue
            elif i % 2 != 0:
                stemmed_phrase = ' '.join([stem(term) for term in t.split(' ')])
                q.phrases.append(stemmed_phrase)
            else:
                free_text_tokens = t.split(' ')
                if and_operator in free_text_tokens[1:len(free_text_tokens) - 1]:
                    raise ParseError(f'improper use of {and_operator} operator in query: {t}')
                if i == 0:
                    if free_text_tokens[0] == and_operator:
                        raise ParseError(f'improper use of {and_operator} operator in query: {t}')
                    if free_text_tokens[-1] != and_operator:
                        raise ParseError(f'missing {and_operator} operator in query: {t}')
                    q.free_text.extend(free_text_tokens[:-1])
                elif i == len(tokens) - 1:
                    if free_text_tokens[0] != and_operator:
                        raise ParseError(f'missing {and_operator} operator in query: {t}')
                    if free_text_tokens[-1] == and_operator:
                        raise ParseError(f'improper use of {and_operator} operator in query: {t}')
                    q.free_text.extend(free_text_tokens[1:])
                else:
                    if free_text_tokens[0] != and_operator or free_text_tokens[-1] != and_operator:
                        raise ParseError(f'missing {and_operator} operator in query: {t}')
                    q.free_text.extend(free_text_tokens[1:-1])
        
        print(q)
        q.free_text = [stem(t) for t in q.free_text]
        return q

    def __repr__(self):
        return f'free_text: {self.free_text}\nphrases: {self.phrases}'


class ParseError(Exception):
    '''
    raised when there is a error while parsing a query.
    '''
    pass
