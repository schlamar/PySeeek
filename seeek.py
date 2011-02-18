#!/usr/bin/env python
# coding: utf-8

'''
    seeek
    ~~~~~

    Simple CLI for pyseeek.
    
    :copyright: (c) 2011 by Marc Schlaich
    :license: MIT, see LICENSE for more details.
'''

import sys

from pymongo import Connection

from pyseeek.crawler import start_crawling

def search(search_strings):
    conn = Connection()
    db = conn.pyseeek
    print db.pages.find({'words.word': {'$in': search_strings}}).count()

def clear_pages():
    conn = Connection()
    db = conn.pyseeek
    db.drop_collection('pages')

def crawl():
    start_crawling(['http://web.de/', 'http://www.welt.de/',                    
                    'http://www.bild.de/'])

def set_index():
    conn = Connection()
    db = conn.pyseeek
    db.pages.ensure_index("words.word");
        
if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'crawl':
            crawl()
        elif sys.argv[1] == 'search':
            search(sys.argv[2:])
        elif sys.argv[1] == 'clear':
            clear_pages()
        elif sys.argv[1] == 'index':
            set_index()
                   
        else:
            print 'Unknown argument "%s"' % sys.argv[1]
                    
# db.pages.find({'words.word': 'test'}).count()
# db.pages.find({"words.word": {$in: ["test", "hallo" , "heute"]}}).count()
