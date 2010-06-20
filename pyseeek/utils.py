# coding: utf-8

'''
    pyseeek.utils
    ~~~~~~~~~~~~~

    Some utilities for parsing and indexing pages.
    
    :copyright: (c) 2010 by Marc Schlaich
    :license: MIT, see LICENSE for more details.
'''

import re
import urllib
import urlparse

from urllib2 import URLError

def normalize_url(url):
    ''' Modified from `werkzeug.urls.url_fix`. 
    
    Sometimes you get an URL by a user that just isn't a real URL because
    it contains unsafe characters like ' ' and so on.  This function can fix
    some of the problems in a similar way browsers handle data entered by the
    user.

    :param url: the string with the URL to fix.
    '''
    scheme, netloc, path, qs, _ = urlparse.urlsplit(url)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, ''))
    
def parse_content_type(response):
    ''' Reads the content type from a HTTP-Response. '''
    try:
        ctype = response.info()['Content-Type']
    except KeyError:
        raise URLError('No Content-Type defined.')
    try:
        return ctype.split(';')[0]
    except IndexError:
        raise URLError('Could not parse Content-Type: "%s"' % ctype)
        
    
def tokenize(text):
    ''' Returns a generator to iterate over the words 
    of the given text. 
    
    :param text: text to extract tokens from.
    '''
    pattern = re.compile(r'[A-Za-z]{3,}')
    for match in pattern.finditer(text):
        yield match.group(0).lower()