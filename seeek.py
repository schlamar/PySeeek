#!/usr/bin/env python

from pymongo import Connection

from pyseeek.crawler import start_crawling

def clear_pages():
    conn = Connection()
    db = conn.pyseeek
    for page in db.pages.find():
        db.pages.remove(page)
        
if __name__ == '__main__':
    start_crawling(['http://web.de/', 'http://www.welt.de/',
                    'http://www.bild.de/'])
                    
                    
# db.pages.find({'words.word': 'test'}).count()
# db.pages.find({"words.word": {$in: ["test", "hallo" , "heute"]}}).count()
# db.pages.ensureIndex( { "words.word": 1 } );
