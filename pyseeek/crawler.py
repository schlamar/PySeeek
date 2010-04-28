import urllib
import urlparse

from urllib2 import build_opener, URLError 

from lxml import html

DEFAULT_ENCODING = 'utf-8'
USER_AGENT = 'PySeeek-Bot'

def normalize_url(url):
    ''' Modified from `werkzeug.utils.url_fix`. '''
    
    scheme, netloc, path, qs, _ = urlparse.urlsplit(url)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, ''))
    
def parse_content_type(response):
    try:
        ctype = response.info()['Content-Type']
    except KeyError:
        raise URLError('No Content-Type defined.')
    try:
        ctype, encoding = ctype.split(';')
        # encoding is now "charset=enc"
        _, encoding = encoding.split('=')
    except ValueError:
        # no or wrong encoding definition, use default
        encoding = DEFAULT_ENCODING
        try:
            ctype = ctype.split(';')[0]
        except IndexError:
            raise URLError('Could not parse Content-Type: "%s"' % ctype)
        
    return ctype, encoding

class Crawler(object):
    def __init__(self):
        self.hosts = dict()        
        self.urls = set()
        
        self.opener = build_opener()
        self.opener.addheaders = [('User-agent', USER_AGENT)]

        
    def parse_page(self, url):
        response = self.opener.open(url)
        ctype, encoding = parse_content_type(response)
        
        if not ctype == 'text/html':
            raise URLError('Wrong Content-Type: "%s"' % ctype)
            
        doc = html.parse(response).getroot()
        title = doc.xpath("//title/text()")[0]
        content = doc.text_content().encode(encoding)
        
        links = set()
        doc.make_links_absolute()
        for _, _, link, _ in doc.iterlinks():
            url = normalize_url(link)
            links.add(url)
                
        return title, content, links 

url = 'http://sitforc.ms4py.org/'
crawler = Crawler()
title, content, links = crawler.parse_page(normalize_url(url))