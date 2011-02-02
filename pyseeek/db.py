# coding: utf-8

'''
    pyseeek.db
    ~~~~~~~~~~

    Database access for PySeeek (using MongoDB backend).
    
    :copyright: (c) 2011 by Marc Schlaich
    :license: MIT, see LICENSE for more details.
'''

from pymongo import Connection

from pyseeek.settings import DB_HOST, DB_PORT
from pyseeek.utils import count_words

class MongoConnector(object):
    ''' Class holding the database connection and providing some
    methods for data manipulation.'''
    def __init__(self):
        conn = Connection(DB_HOST, DB_PORT)
        self.db = conn.pyseeek 

    def insert_page(self, url, title, content):
        ''' Insert the page in the database.
        
        :param url: URL of the page.
        :param title: Page title.
        :param content: Page content.
        '''
        page = {'url': url, 'title': title, 'content': content, 
                'words': [{'word': word, 'counter': counter} 
                           for word, counter 
                           in count_words(content).iteritems()]}
        self.db.pages.save(page)
        
