#!/usr/bin/env python

import cPickle as pickle
from PorterStemmer import PorterStemmer
from math import log, sqrt
import re
import string
from collections import defaultdict
import os
import sys
import copy

__version__ = "0.3"
__license__ = "MIT"
__author__ = "Shuo Yang"
__author_email__ = "imsure95@gmail.com"

punc_reg = re.compile('[%s]' % re.escape(string.punctuation))
del_punc = lambda s : punc_reg.sub('', s)

class Query(object):

    def __init__(self):
        self.stoplist = open('stopword_list.txt', 'r').read().split()
        self.porter = PorterStemmer()
        doc2id = pickle.load(open('doc2id.pkl', 'rb'))
        self.id2doc = {v:k for k, v in doc2id.items()}
        
        self.index = pickle.load(open('index.pkl', 'rb'))
        self.pos_index = pickle.load(open('pos_index.pkl', 'rb'))

        self.idf_new_term = log(len(doc2id)/0.5, 2)

    def get_terms(self, contents, qtype):
        terms = contents.split()
        terms = map(del_punc, terms)
        terms = map(lambda s : s.lower(), terms)

        if qtype == 'keywords query':
            terms = [t for t in terms if t not in self.stoplist]
            return [self.porter.stem(term, 0, len(term)-1) for term in terms]
        elif qtype == 'phrase query':
            return [self.porter.stem(term, 0, len(term)-1) for term in terms]

    def get_idf(self, term):
        return self.index[term][0]

    def build_vecs(self, terms):
        qvec = [0] * len(terms)
        doc_vecs = defaultdict(lambda : [0]*len(terms))
        
        for term_index, term in enumerate(terms):
            if not self.index.has_key(term):
                print '\nOur collection does not have term', term
                continue

            idf = self.get_idf(term)
            qvec[term_index] = idf
                
            for doc, tf in self.get_postings(term):
                doc_vecs[doc][term_index] = tf * idf

        return qvec, doc_vecs.items()

    def get_postings(self, term):
        return self.index[term][1]

    def dot_product(self, v1, v2):
        return sum([x1*x2 for x1, x2 in zip(v1, v2)])

    def vec_len(self, vec):
        return sqrt(sum([x*x for x in vec]))

    def cos_similarity(self, v1, v2):
        len_v1 = self.vec_len(v1)
        len_v2 = self.vec_len(v2)
        return self.dot_product(v1, v2)/(len_v1 * len_v2)

    def rank(self, qvec, dvecs):
        scores = [(self.cos_similarity(dvec, qvec), doc) for doc, dvec in dvecs]
        return sorted(scores, reverse=True)

    def get_doc_name(self, doc_id):
        return os.path.relpath(self.id2doc[doc_id])

    def show_top3_results(self, ranks):
        print
        print 'RANK'.ljust(4), 'DOCUMENT(SCORE)'.center(100)
        print '-' * 101
        for index, (score, doc_id) in enumerate(ranks):
            print str(index+1).ljust(4),
            print self.get_doc_name(doc_id),
            print "(%0.2f)" % score

    def keywords_query(self, qterms):
        qvec, doc_vecs = self.build_vecs(qterms)
        if doc_vecs == []:
            print '\nCannot find matching documents!'
            return
        
        ranks = self.rank(qvec, doc_vecs)
        self.show_top3_results(ranks[0:3])

    def get_docs(self, term):
        return [x[0] for x in self.pos_index[term]]

    def intersect_lists(self, lists):
        lists.sort(key=len)
        intersect = lambda s1, s2 : set(s1).intersection(set(s2))
        return reduce(intersect, lists)

    def get_positions(self, term, doc):
        for d, positions in self.pos_index[term]:
            if d == doc:
                return positions

    def match_positions(self, doc, phrase):
        """
        Algorithm to find a 'phrase' in 'doc' using postional index:
        1. Get a list of postions for each term in the phrase
        2. Put the postion lists got from step 1 into a list, sort by length of postion list.
        3. 
        """
        ## 'positions' is a list of position list. [[], [], []]
        positions = []
        for term in phrase:
            positions.append(self.get_positions(term, doc))

        ## Must do a deep copy here because we are going to modify position lists.
        positions = copy.deepcopy(positions)
        for i in range(len(positions)):
            positions[i] = [x-i for x in positions[i]]

        res = list(self.intersect_lists(positions))
        if res != []:
            return self.get_doc_name(doc)
        else:
            return None

    def phrase_query(self, phrase):
        matching_docs = []
        for term in phrase:
            ## All terms in the phrase must in the collection.
            if term not in self.pos_index:
                print 'Term', term, 'is not in the collection. Try another one.'
                return

        docs = defaultdict(lambda : [0]*len(phrase))
        for term_index, term in enumerate(phrase):
            docs[(term_index, term)] = self.get_docs(term)

        ## Get all the documents where all query terms appear in.
        phrase_docs = self.intersect_lists(docs.values())
        for doc in phrase_docs:
            dname = self.match_positions(doc, phrase)
            if dname is not None:
                matching_docs.append(dname)

        if matching_docs == []:
            print 'No document matches the phrase \'%s\'' % ' '.join(map(str, phrase))
        else:
            print '\nMatching documents:'
            for doc in matching_docs:
                print doc


    def query(self):
        print 'To do free text query, just type in keywords seqerated by whitespace as you did in Google search.',
        print 'Like [Romeo Juliet love rite]'
        print 'To do phrase text query, type in phrase with in single quote.',
        print 'Like [\'to be or not to be\']'

        while True:
            print '\nEnter a query:(If you want to quit, type \'q\')'
            query = raw_input()
            if query == 'q':
                break

            if(query.startswith('\'') and query.endswith('\'')):
                self.phrase_query( self.get_terms(query.strip('\''), 'phrase query') )
            else:
                self.keywords_query( self.get_terms(query, 'keywords query') )
        

if __name__ == '__main__':
    
    print '\nWelcom to Shakespeare Search Engine.'
    print 'Version:', __version__
    print 'License:', __license__
    print 'Author:', __author__
    print 'Author email:', __author_email__
    print
    
    q = Query()
    q.query()
