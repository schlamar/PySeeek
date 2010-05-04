# coding: utf-8

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