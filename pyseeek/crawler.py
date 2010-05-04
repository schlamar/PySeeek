import httplib
import time
import urllib
import urlparse

from robotparser import RobotFileParser
from urllib2 import build_opener, URLError, HTTPError

from lxml import html

HOST_DELAY = 0
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
        ctype = ctype.split(';')[0]
    except IndexError:
        raise URLError('Could not parse Content-Type: "%s"' % ctype)
        
    return ctype
    
def tokenize(text):
    pattern = re.compile(r'[A-Za-z]{3,}')
    for match in pattern.finditer(text):
        yield match.group(0).lower()
    
class Host(object):
    def __init__(self, hostname):
        self.hostname = hostname
        self.last_access = 0
        
        self.rp = RobotFileParser()
        self.rp.set_url('http://%s/robots.txt' % self.hostname)
        
        self.delay = HOST_DELAY
        
    @property
    def visit_allowed(self):
        if (self.last_access + self.delay) < time.time():
            # this host will be visited now, set new timestamp
            self.last_access = time.time()
            return True
        return False

class Crawler(object):
    def __init__(self, urls):
        self.hosts = dict()        
        self.urls = set()
        self.handled_urls = set()
        self.invalid_urls = set()
        
        self.opener = build_opener()
        self.opener.addheaders = [('User-agent', USER_AGENT)]
        
        self.add_urls(urls)
        
        self.start = 0.0

    @property
    def runtime(self):
        return time.time() - self.start
        
    @property
    def parse_average(self):
        return len(self.handled_urls) / self.runtime
        
    def parse_page(self, url):
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
        while True:
            try:
                url = self.urls.pop()
            except KeyError:
                return None
                
            hostname = urlparse.urlparse(url).hostname
            host = self.hosts[hostname]
                
            if host.visit_allowed:
                return url
            else:
                # put url back, not processed yet
                self.urls.add(url)
         
         
    def add_urls(self, urls):
        for url in urls:
            if url in self.handled_urls or url in self.invalid_urls:
                continue
            
            hostname = urlparse.urlparse(url).hostname
            try:
                host = self.hosts[hostname]
            except KeyError:
                self.hosts[hostname] = host = Host(hostname)
            
            if host.rp.can_fetch(USER_AGENT, url):
                self.urls.add(url)
       
       
    def crawl(self):
        self.start = time.time()
        url = self.get_url_to_process()
        while url is not None:
            try:
                title, content, links = self.parse_page(url)
            except (URLError, HTTPError, httplib.InvalidURL, UnicodeDecodeError):
                self.invalid_urls.add(url)
                url = self.get_url_to_process()
                continue
            
            self.handled_urls.add(url)
            if links is not None:
                self.add_urls(links)
            
            url = self.get_url_to_process()

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