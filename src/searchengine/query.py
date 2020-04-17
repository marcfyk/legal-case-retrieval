from .util import stem

import re

single_quote = '\''
double_quote = '"'
and_operator = 'AND'

class Query:
    '''
    represents a query.
    terms -> list of terms/phrases
    is_boolean_query -> indicates if query requires an exact match or not.
    '''

    def __init__(self, terms=[], is_boolean_query=False):
        self.terms = [t for t in terms]
        self.is_boolean_query = is_boolean_query

    @classmethod
    def parse_free_text_query(cls, line):
        '''
        parses a line into a query object for vector space retrieval.
        '''
        terms = [stem(t) for t in line.strip().split(' ')] # stems each term in the line.
        return Query(terms=terms)

    @classmethod
    def parse_boolean_query(cls, line):
        '''
        parses a line into a query object for boolean retrieval.
        any invalid format in line will throw a ParseError.
        checks for:
        1. "AND" must be inbetween terms/phrases
        2. phrases must be start and end with double quotes
        3. terms should only contain one word (multiple terms should be chained with "AND")
        '''
        terms = []
        tokens = [t.strip() for t in line.split(and_operator)]

        # checks for invalid use of AND, ie: " AND <term>" or "<term> AND" or "AND"
        if not all(tokens):
            raise ParseError(f'"{and_operator}" not used properly')

        for token in tokens:
            if not token.startswith(double_quote) and not token.endswith(double_quote):
                if len(token.split(' ')) > 1:
                    raise ParseError(f'multiple terms should be in a phrase wrapped in quotes: {token}')
                terms.append(token)
            elif token.startswith(double_quote) and token.endswith(double_quote):
                terms.append(token[1:-1].strip())
            else:
                raise ParseError(f'mismatched quotes found in {token}')

        return Query(terms=terms, is_boolean_query=True)

    @classmethod
    def parse(cls, line):
        '''
        parses line and determines the type of query the line contains.
        if there is "AND" or double quotes in the line, 
        it indicates that the query contains a phrase / and operator.
        therefore it would mean that the query requires exact match.
        if not, then it is a free text query.
        '''
        if and_operator in line or double_quote in line:
            return cls.parse_boolean_query(line)
        else:
            return cls.parse_free_text_query(line)

                        
    def __repr__(self):
        return f'terms: {self.terms}\nboolean_query: {self.is_boolean_query}'


class ParseError(Exception):
    '''
    raised when there is a error while parsing a query.
    '''
    pass
