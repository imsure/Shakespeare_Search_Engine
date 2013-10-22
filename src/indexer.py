#!/usr/bin/env python

import cPickle as pickle
import re
import string
from PorterStemmer import PorterStemmer
from collections import Counter
import os
from math import log
import sys
from collections import defaultdict
from operator import itemgetter
from datetime import datetime

punc_reg = re.compile('[%s]' % re.escape(string.punctuation))
del_punc = lambda s : punc_reg.sub('', s)

class Indexer(object):

    def __init__(self):
        self.dname2id = pickle.load(open('doc2id.pkl', 'rb'))
        try:
            f = open('stopword_list.txt', 'r')
        except IOError:
            raise 'Failed to open stopword_list.txt.'

        self.stoplist = f.read().split()
        self.porter = PorterStemmer()
        ## term to its posting list.
        self.index = {}
        self.pos_index = defaultdict(list)
        self.doc_num = len(self.dname2id)

    def terms_for_keywords_query(self, terms):
        ## Filter out stop words.
        return [t for t in terms if t not in self.stoplist]

    def get_terms(self, contents):
        terms = contents.split()
        terms = map(del_punc, terms)
        terms = map(lambda s : s.lower(), terms)

        ## Terms for keywords based query(aka: free text query).
        terms_for_kq = [self.porter.stem(term, 0, len(term)-1) for term in self.terms_for_keywords_query(terms)]

        ## Terms for phrase query.
        terms_for_pq = [self.porter.stem(term, 0, len(term)-1) for term in terms]

        return terms_for_kq, terms_for_pq

    def get_doc_id(self, dname):
        return self.dname2id[dname]

    def build_posting_list_for_pq(self, terms, doc_id):
        """
        Build posting list(term : [doc, [positions]]) for phrase query.
        """
        term2doc_pos = {}
        for pos, term in enumerate(terms):
            try:
                term2doc_pos[term][1].append(pos)
            except:
                term2doc_pos[term] = [doc_id, [pos]]

        for term, posting in term2doc_pos.iteritems():
            self.pos_index[term].append(posting)

    def build_posting_list_for_kq(self, terms, doc_id):
        """
        Build posting list(term : [idf, [(doc1, tf), (doc2, tf), ...]]) for keywords based query.
        """
        tf_counter = Counter(terms)
        max_elem = tf_counter.most_common(1)
        most_common_term = max_elem[0][0]
        max_tf = max_elem[0][1]
        # print 'Most common term is:', most_common_term, '\tMax tf is:', max_tf

        for term, tf in tf_counter.iteritems():
            if not self.index.has_key(term):
                df = 1
                self.index[term] = [df, [(doc_id, float(tf)/max_tf)]]
            else:
                df = self.index[term][0]
                df += 1
                self.index[term][0] = df
                self.index[term][1].append((doc_id, float(tf)/max_tf))

    def write_index_to_file(self):
        pickle.dump(self.index, open('index.pkl', 'wb'))
        pickle.dump(self.pos_index, open('pos_index.pkl', 'wb'))

    def compute_idf(self):
        for term, postings in self.index.iteritems():
            postings[0] = log(float(self.doc_num)/postings[0], 2)

    def parse_collection(self):

        stdout_old = sys.stdout
        sys.stdout = open('indexer_log', 'w')
        print 'Total %d documents need to be processed.' % self.doc_num

        for index, (doc_name, doc_id) in enumerate(sorted(self.dname2id.iteritems(), key=itemgetter(1))):
            try:
                print 'Building index for:', os.path.basename(doc_name),
                print '\tDocument ID:', doc_id
                f = open(doc_name, 'r')
            except IOError:
                raise 'Unable to open document [%s]' % doc_name

            ## Get terms for keywords based query and phrase based query.
            terms_for_kq, terms_for_pq = self.get_terms(f.read())
            
            self.build_posting_list_for_kq(terms_for_kq, doc_id)
            self.build_posting_list_for_pq(terms_for_pq, doc_id)

        self.compute_idf()
        self.write_index_to_file()

        sys.stdout = stdout_old


if __name__ == '__main__':
    t_start = datetime.now()
    indexer = Indexer()
    indexer.parse_collection()
    t_end = datetime.now()
    
    delta = t_end - t_start
    print 'It takes', delta.seconds, 'seconds to finish indexing.'
    
        
