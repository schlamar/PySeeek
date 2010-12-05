#!/usr/bin/env python

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
    db.pages.drop()

def crawl():
    start_crawling(['http://web.de/', 'http://www.welt.de/',                    
                    'http://www.bild.de/'])

def set_index():
    db.pages.ensureIndex({ "words.word": 1 });
        
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
                    
                    
# db.pages.find({'words.word': 'test'}).count()
# db.pages.find({"words.word": {$in: ["test", "hallo" , "heute"]}}).count()
