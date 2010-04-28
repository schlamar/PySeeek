import time
import urllib
import urlparse

from urllib2 import build_opener, URLError, HTTPError

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
    
def tokenizer(text):
    pattern = re.compile(r'[A-Za-z]{3,}')
    for match in pattern.finditer(text):
        yield match.group(0).lower()
    
class Host(object):
    def __init__(self, hostname):
        self.hostname = hostname
        self.last_access = 0
        
        self.delay = 0 
        
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
        
        self.opener = build_opener()
        self.opener.addheaders = [('User-agent', USER_AGENT)]
        
        self.add_urls(urls)

        
    def parse_page(self, url):
        response = self.opener.open(url)
        ctype, encoding = parse_content_type(response)
        
        if not ctype == 'text/html':
            raise URLError('Wrong Content-Type: "%s"' % ctype)
            
        doc = html.parse(response).getroot()
        title = doc.xpath("//title/text()")[0].encode(encoding)
        content = doc.text_content().encode(encoding)
        
        links = set()
        doc.make_links_absolute()
        for _, _, link, _ in doc.iterlinks():
            url = normalize_url(link)
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
            if url in self.handled_urls:
                continue
            
            hostname = urlparse.urlparse(url).hostname
            try:
                host = self.hosts[hostname]
            except KeyError:
                host = Host(hostname)
                self.hosts[hostname] = host
                
            self.urls.add(url)
       
       
    def crawl(self):
        url = self.get_url_to_process()
        while url is not None:
            try:
                title, _, links = self.parse_page(url)
            except (URLError, HTTPError) as e:
                print e.__class__.__name__, e
                url = self.get_url_to_process()
                continue
            print 'Processed:', url, title
            self.handled_urls.add(url)
            self.add_urls(links)
            
            url = self.get_url_to_process()

url = 'http://sitforc.ms4py.org/'
crawler = Crawler([url])
crawler.crawl()