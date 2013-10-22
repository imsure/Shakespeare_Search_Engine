#!/usr/bin/env python

"""
A simple crawler that can extract Shakespeare's whole collection from
http://shakespeare.mit.edu/ and save documents as text files.

After successful running, It will also create a document hierarchy as:

                     whole collection
                /            |             \
           Comedy         Tragedy        History
          /  |  \         /  |  \        /  |  \
           works           works          works
             |               |              |
         Acts_Scenes     Acts_Scenes     Acts_Scenes
"""

import sys
import re
import argparse
from time import sleep
from BeautifulSoup import BeautifulSoup
import urllib2
import urlparse
import string
import cPickle as pickle
from datetime import datetime

punc_reg = re.compile('[%s]' % re.escape(string.punctuation))

def append_url_root(rels, root):
    return map(lambda rel : urlparse.urljoin(root, rel), rels)

def extract_text(element):
    if element.parent.get('href'):
        return False

    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    
    if re.match('<!--.*-->', str(element)):
        return False

    if element.find('|') != -1:
        return False

    return True

del_punc = lambda s : punc_reg.sub('', s)
strip_newline = lambda s : s.replace('\n', '')
add_underline = lambda s : s.replace(' ', '_')

class Crawler(object):

    def __init__(self, root_url):
        self.root_url = root_url
        self.genres = []
        self.genre2works = {}
        self.work2acts = {}

    def get_soup(self, url):
        print '\nStart crawling %s\n' % url
        try:
            request = urllib2.Request(url)
            handler = urllib2.build_opener()

        except IOError:
            print 'Cannot open url %s' % root_url
            raise SystemExit, 1

        content = unicode(handler.open(request).read(),
                          'utf-8', errors='replace')
        return BeautifulSoup(content)


    def fetch_genres(self, soup):
        """
        Fetch four genres from 'h2' tags. They are
        'Comedy', 'History', 'Tragedy', 'Poetry'.
        """
        return [h2tag.text for h2tag in soup('h2')]

    def fetch_acts(self, works):

        for (work, link) in works:
            print '\nStuff under work [%s] and link [%s]' % (work, link)
            acts = []
            links = []
            soup = self.get_soup(link)
            for p in soup('p'):
                if p.text.startswith('Act'):
                    pieces = p.text.split('Act')
                    for pie in pieces:
                        if pie != '':
                            act = 'Act' + pie
                            acts.append(act)
                    for a in p.findAll('a'):
                        links.append(a.get('href'))

            for (act, lk) in zip(acts, links):
                print 'Fetching act [%s] and its link [%s]' % (act, lk)

            links, acts = self.normalize_links_and_names(links, acts, link[:-10])
            self.work2acts[work] = zip(acts, links)

    def normalize_links_and_names(self, links, names, root_url):
        links = append_url_root(links, root_url)
        names = map(del_punc, names)
        names = map(strip_newline, names)
        names = map(add_underline, names)

        return links, names
        
    def fetch_works(self, soup):

        tds = soup.findAll(attrs={'valign' : 'BASELINE'})
        for (genre, td) in zip(['Comedy', 'History', 'Tragedy'], tds):

            links = []
            works = []

            ## First level processing:
            ## Build a dictionary that maps genre to the name list of works.
            print '\nStuff under genre [%s]\n' % genre
            for anchor in td.findAll('a'):
                link = anchor.get('href')
                links.append(link)
                work = anchor.contents[0]
                works.append(work)
                print 'Fetching work: [%s] and its link: [%s]' % (work, link)

            links, works = self.normalize_links_and_names(links, works, self.root_url)

            self.genre2works[genre] = works

            self.fetch_acts(zip(works, links))

    def build_hierarchy(self):
        import os
        root_dir = '../whole_collection'
        try:
            os.mkdir(root_dir)
        except OSError:
            pass

        doc_id = 1
        doc2id = {}
        for genre in self.genre2works.keys():
            try:
                os.mkdir(os.path.join(root_dir, genre))
            except OSError:
                pass
            
            for work in self.genre2works[genre]:
                try:
                    path = os.path.join(root_dir, genre, work)
                    os.mkdir(path)
                except OSError:
                    pass

                for (act, link) in self.work2acts[work]:
                    fp = open(os.path.join(path, act+'.txt'), 'w')
                    soup = self.get_soup(link)
                    contents = soup.findAll({'a' : True, 'i' : True, 'h3' : True}, text=True)
                    texts = filter(extract_text, contents)
                    fp.write(''.join(texts))
                    
                    doc2id[os.path.abspath(os.path.join(path, act+'.txt'))] = doc_id
                    doc_id += 1

        pickle.dump(doc2id, open('doc2id.pkl', 'wb'))


    def crawl(self):
        old_stdout = sys.stdout
        sys.stdout = open('crawler_log', 'w')
        
        soup = self.get_soup(self.root_url)
        
        self.genres = self.fetch_genres(soup)

        self.fetch_works(soup)

        sys.stdout = old_stdout
        self.build_hierarchy()

def parseCmdArgs():
    """
    Parse any command-line arguments given and return
    the parsed options and arguments.
    """
    parser = argparse.ArgumentParser(description='A simple web crawler.')
    
    parser.add_argument('link', metavar='link', type=str,
                        nargs=1, help='link we want to process')
    parser.add_argument('-d', '--depth', default=10, dest='depth',
                        help='Maximum depth to traverse')
    parser.add_argument('-o', '--output', default=sys.stdout, dest='output',
                        help='Destination of the output message')
    
    args = vars(parser.parse_args())
    return args

    
def main():
    args = parseCmdArgs()
    root_url = args['link']
    depth = args['depth']
    output = args['output']

    t_start = datetime.now()
    crawler = Crawler(root_url[0])
    crawler.crawl()
    t_end = datetime.now()

    delta = t_end - t_start
    print 'It takes', delta.seconds, 'seconds to finish crawling.'    

if __name__ == '__main__':
    main()
