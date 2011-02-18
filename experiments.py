#!/usr/bin/env python
# coding: utf-8

'''
    experiments
    ~~~~~~~~~~~

    Experiments for performance measurements etc.
    
    :copyright: (c) 2011 by Marc Schlaich
    :license: MIT, see LICENSE for more details.
'''

import time

import numpy as np
import matplotlib.pyplot as plt

from pyseeek.crawler import CrawlerAdministrator
from seeek import clear_pages, set_index

def performance_number_crawlers():
    wait_time = 15
    urls = ['http://www.python.org/', 'http://www.cnn.com/', 
            'http://www.bbc.com/']
    x = np.arange(2,16,2)
    y = list()
    
    for num_crawler in x:
        print 'Run with %s crawlers' % num_crawler
        
        # clear database
        clear_pages()
        set_index()
        
        admin = CrawlerAdministrator(urls, num_crawler)
        admin.crawl()
        time.sleep(wait_time*60)
        admin.stop()
        
        y.append(admin.num_handled_urls)
        
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(x-0.5, y, width=1)
    
    ax.set_title('Crawled pages in %s minutes' % wait_time)
    ax.set_xticks(x)
    ax.set_xlabel('Number of crawlers')
    ax.set_ylabel('Pages')

    plt.savefig('performance_number_crawlers.png')
    
if __name__ == '__main__':
    performance_number_crawlers()
