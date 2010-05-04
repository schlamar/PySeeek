# coding: utf-8

'''
    pyseeek.crawler
    ~~~~~~~~~~~~~~~

    This module is responsible for crawling pages.
    See the __main__ section for basic usage.
    
    :copyright: (c) 2010 by Marc Schlaich
    :license: MIT, see LICENSE for more details.
'''

import httplib
import time
import urlparse

from robotparser import RobotFileParser
from urllib2 import build_opener, URLError, HTTPError

from lxml import html

from utils import normalize_url, parse_content_type

USER_AGENT = 'PySeeek-Bot'
    
class Host(object):
    ''' Represents one host. Responsible for parsing and analyzing
    ``robots.txt``.
    
    :param hostname: the name of the host extracted from an URL.
    '''
    def __init__(self, hostname):
        self.hostname = hostname
        
        self.rp = RobotFileParser()
        self.rp.set_url('http://%s/robots.txt' % self.hostname)
        
    def url_allowed(self, url):
        ''' Checks if the given url is allowed to crawl.
        
        :param url: URL to check.
        '''
        return self.rp.can_fetch(USER_AGENT, url)
        

class Crawler(object):
    ''' Adminstrates the whole crawling process. Stores URLs to process,
    processed URLs and encountered invalid URLs in one ``set`` each.
    
    :param urls: list of URLs which should be crawled.
    '''
    def __init__(self, urls):
        self.hosts = dict()        
        self.urls = set()
        self.handled_urls = set()
        self.invalid_urls = set()
        
        self.opener = build_opener()
        self.opener.addheaders = [('User-agent', USER_AGENT)]
        
        self.add_urls((normalize_url(url) for url in urls))
        
        self.start = 0.0

    @property
    def runtime(self):
        ''' Returns the time in seconds since the crawling 
        process has started.
        '''
        return time.time() - self.start
        
    @property
    def parse_average(self):
        ''' Returns the average of processed pages per second. '''
        return len(self.handled_urls) / self.runtime
        
    def parse_page(self, url):
        ''' Opens and parses the given URL with ``lxml``.
        
        :returns: a tuple with 3 elements:
                  1. the page title
                  2. content of the page
                  3. located URLs on this page 
                     (absolute and normalized)
        '''
        response = self.opener.open(url)
        ctype = parse_content_type(response)
        
        if not ctype == 'text/html':
            raise URLError('Wrong Content-Type: "%s"' % ctype)
            
        doc = html.parse(response).getroot()
        if doc is None:
            return None, None, None
        try:
            title = doc.xpath("//title/text()")[0].encode('utf-8')
        except IndexError:
            title = None
            
        content = doc.text_content().encode('utf-8')
        
        links = set()
        doc.make_links_absolute()
        for _, _, link, _ in doc.iterlinks():
            url = normalize_url(link.encode('utf-8'))
            if url:
                links.add(url)
                
        return title, content, links
      
      
    def get_url_to_process(self):
        ''' Returns one URL to process or ``None`` if 
        the there isn't any URL to process.
        '''
        try:
           return self.urls.pop()
        except KeyError:
            return None
         
         
    def add_urls(self, urls):
        ''' Adds a list of URLs to the queue list. Checks if any URL 
        was processed before and if the page is allowed to crawl with
        regard to the ``robots.txt``.
        
        :param urls: iterable of URLs to add.
        '''
        for url in urls:
            if url in self.handled_urls or url in self.invalid_urls:
                continue
            
            hostname = urlparse.urlparse(url).hostname
            try:
                host = self.hosts[hostname]
            except KeyError:
                self.hosts[hostname] = host = Host(hostname)
            
            if host.url_allowed(url):
                self.urls.add(url)
       
       
    def crawl(self):
        ''' Starts the crawling process and stops if there 
        aren't anymore URLs to crawl.
        '''
        self.start = time.time()
        url = self.get_url_to_process()
        while url is not None:
            try:
                title, content, links = self.parse_page(url)
            except (URLError, HTTPError, httplib.InvalidURL, 
                    UnicodeDecodeError):
                self.invalid_urls.add(url)
                url = self.get_url_to_process()
                continue
            
            self.handled_urls.add(url)
            if links is not None:
                self.add_urls(links)
            
            url = self.get_url_to_process()

if __name__ == '__main__':
    crawler = Crawler(['http://web.de/', 'http://www.welt.de/', 
                       'http://www.bild.de/'])
    try:
        crawler.crawl()
    except KeyboardInterrupt:
        with open('urls.log', 'w') as fobj:
            print >> fobj, '''\
Total runtime: %d min
Pages processed: %d
Average: %.3f Pages/s %.3f Pages/min 
''' % (crawler.runtime/60.0, len(crawler.handled_urls), 
       crawler.parse_average, crawler.parse_average*60)
            for url in crawler.handled_urls:
                print >> fobj, 'Processed:', url