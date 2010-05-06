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
import socket
import time
import urlparse

from robotparser import RobotFileParser
from threading import Thread, Lock
from urllib2 import build_opener, URLError, HTTPError

from lxml import html

from utils import normalize_url, parse_content_type

NUMBER_CRAWLERS = 8
USER_AGENT = 'PySeeek-Bot'

socket.setdefaulttimeout(30)
    
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
        

class CrawlerAdministrator(object):
    ''' Adminstrates the whole crawling process. Stores URLs to process,
    processed URLs and encountered invalid URLs in one ``set`` each.
    
    :param urls: list of URLs which should be crawled.
    '''
    def __init__(self, urls):
        self.crawlers = list()
        self.lock_urls = Lock()
        self.lock_invalid_urls = Lock()
        self.lock_handled_urls = Lock()
        
        self.hosts = dict()
        self.urls = set()
        self.handled_urls = set()
        self.invalid_urls = set()
        
        self.add_urls((normalize_url(url) for url in urls))
        
        self.start = 0.0
        self.stopping = False

    @property
    def runtime(self):
        ''' Returns the time in seconds since the crawling 
        process has started.
        '''
        return time.time() - self.start
        
    @property
    def parse_average(self):
        ''' Returns the average of processed pages per second. '''
        with self.lock_handled_urls:
            return len(self.handled_urls) / self.runtime
        

    def get_url_to_process(self):
        ''' Returns one URL to process or ``None`` if 
        the there isn't any URL to process.
        '''
        if self.stopping:
            return None
        try:
            with self.lock_urls:
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
            with self.lock_handled_urls:
                if url in self.handled_urls:
                    continue

            with self.lock_invalid_urls:
                if url in self.invalid_urls:
                    continue

            hostname = urlparse.urlparse(url).hostname
            with self.lock_urls:
                try:
                    host = self.hosts[hostname]
                except KeyError:
                    self.hosts[hostname] = host = Host(hostname)
            
                if host.url_allowed(url):
                    self.urls.add(url)
       
       
    def crawl(self):
        ''' Starts the crawler threads. '''
        self.start = time.time()
        for _ in range(NUMBER_CRAWLERS):
            crawler = Crawler(self)
            self.crawlers.append(crawler)
            crawler.start()

    def stop(self):
        ''' Stops the crawling process. '''
        self.stopping = True
        for crawler in self.crawlers:
            crawler.join()

class Crawler(Thread):
    ''' Crawler as worker thread to process single pages. '''
    def __init__(self, admin):
        Thread.__init__(self)
        self.admin = admin

        self.opener = build_opener()
        self.opener.addheaders = [('User-agent', USER_AGENT)]
        

    def run(self):
        ''' Fetches URLs from the admin and process them
        until he returns ``None``.
        '''
        url = self.admin.get_url_to_process()
        while url is not None:
            try:
                title, content, links = self.parse_page(url)
            except (URLError, HTTPError, httplib.InvalidURL,
                    UnicodeDecodeError, socket.error, socket.timeout):
                with self.admin.lock_invalid_urls:
                    self.admin.invalid_urls.add(url)
                url = self.admin.get_url_to_process()
                continue
            with self.admin.lock_handled_urls:
                self.admin.handled_urls.add(url)
            if links is not None:
                self.admin.add_urls(links)

            url = self.admin.get_url_to_process()

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

if __name__ == '__main__':
    admin = CrawlerAdministrator(['http://web.de/', 'http://www.welt.de/',
                                  'http://www.bild.de/'])
    try:
        admin.crawl()
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        admin.stop()
        with open('urls.log', 'w') as fobj:
            print >> fobj, '''\
Total runtime: %d min
Pages processed: %d
Average: %.3f Pages/s %.3f Pages/min 
''' % (admin.runtime/60.0, len(admin.handled_urls),
       admin.parse_average, admin.parse_average*60)
            for url in admin.handled_urls:
                print >> fobj, 'Processed:', url