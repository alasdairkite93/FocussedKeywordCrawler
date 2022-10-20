import multiprocessing
from multiprocessing import Pool, Process, Lock

from flask import Flask

import sys
import heapq
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import time
from bs4 import BeautifulSoup, SoupStrainer

import cchardet

from urllib.parse import urlparse, urlsplit, urljoin

internal_link=[]
temp_urls = []
number_urls = 0

def classification(data, url):

    if (data != None):
        main_keywords = ['watch', 'mens watch', 'womens watches', 'watches']
        secondary_keywords = ['analogue', 'digital', 'automatic', 'hand driven', 'quartz', 'faux leather', 'leather',
                              'rubber', 'stainless steel', 'acrylic', 'glass', 'lorus', 'pulsar', 'sekonda','timex', 'rotary', 'fossil', 'diesel', 'tommy hilfiger', 'tommy-hilfiger', 'hugo boss', 'hugo-boss', 'armani']
        score = 0

        url_lambda = list(map(lambda v : v in url, main_keywords))
        score+=15*url_lambda.count(True)
        h1_lambda = list(map(lambda v : v in data.get('h1'), main_keywords))
        score+=10*h1_lambda.count(True)
        h2_lambda = list(map(lambda v : v in data.get('h2'), main_keywords))
        score+=10*h2_lambda.count(True)
        p_lambda = list(map(lambda v : v in data.get('p'), main_keywords))
        score+=5*p_lambda.count(True)
        span_lambda = list(map(lambda v : v in data.get('span'), main_keywords))
        score+=5*span_lambda.count(True)
        li_lambda = list(map(lambda v : v in data.get('li'), main_keywords))
        score+=5*li_lambda.count(True)


        url_lambda = list(map(lambda v : v in url, secondary_keywords))
        score+=11*url_lambda.count(True)
        h1_lambda = list(map(lambda v : v in data.get('h1'), secondary_keywords))
        score+=6*h1_lambda.count(True)
        h2_lambda = list(map(lambda v : v in data.get('h2'), secondary_keywords))
        score+=6*h2_lambda.count(True)
        p_lambda = list(map(lambda v : v in data.get('p'), secondary_keywords))
        score+=1*p_lambda.count(True)
        span_lambda = list(map(lambda v : v in data.get('span'), secondary_keywords))
        score+=1*span_lambda.count(True)
        li_lambda = list(map(lambda v : v in data.get('li'), secondary_keywords))
        score+=1*li_lambda.count(True)

        return score
    else:
        pass

def downloadClassificationTags(input_url):

    class_tags = {}

    try:
        req_url = requests.get(input_url, timeout=2).content

        only_li = SoupStrainer("li")
        only_h1 = SoupStrainer("h1")
        h2 = SoupStrainer("h2")
        h3 = SoupStrainer("h3")
        p = SoupStrainer("p")
        span = SoupStrainer("span")
        li = SoupStrainer("li")

        class_tags.update({'url':input_url})
        class_tags.update({'li':BeautifulSoup(req_url, "html.parser", parse_only=only_li).text})
        class_tags.update({'h1':BeautifulSoup(req_url, "html.parser", parse_only=only_h1).text})
        class_tags.update({'h2':BeautifulSoup(req_url, "html.parser", parse_only=h2).text})
        class_tags.update({'h3':BeautifulSoup(req_url, "html.parser", parse_only=h3).text})
        class_tags.update({'p':BeautifulSoup(req_url, "html.parser", parse_only=p).text})
        class_tags.update({'span':BeautifulSoup(req_url, "html.parser", parse_only=span).text})
        class_tags.update({'li':BeautifulSoup(req_url, "html.parser", parse_only=li).text})

        score = classification(class_tags, input_url)

        return [score, input_url]


    except:
        print("REQUEST ERROR")
        return None

def downloadATags(input_url):

    print("DOWNLOADATAGS INPUT URL: ", input_url)
    try:
        class_tags = {}
        req_url = requests.get(input_url).content
        only_a = SoupStrainer("a")
        class_tags.update({'a': BeautifulSoup(req_url, "html.parser", parse_only=only_a)})
        return class_tags
    except:
        return None

def loadSeeds(lines):
    myQueue = PriorityQueue()
    p = Pool(processes=5)
    data = p.map(downloadClassificationTags, [i for i in lines])
    for entry in data:
        myQueue.insert([entry[0], entry[1]])
    return myQueue

def downloadClassTags(ret_urls):
    p = Pool(processes=20)
    data = []
    data = p.map(downloadClassificationTags, [i for i in ret_urls[:30]]) #:5 is a slice method that limits the number of URLs to search
    return data

def queue(myQueue):
    print("QUEUE METHOD")
    while not myQueue.isEmpty():
        print("QUEUE: ")
        print(myQueue)
        url = myQueue.delete()
        seed_url_anchor = {}
        seed_url_anchors = downloadATags(url[1])
        ret_urls = []
        for url in seed_url_anchors.get('a').find_all(href=True):
            ret_urls.append(url['href'])
        url_data = downloadClassTags(ret_urls)
        for entry in url_data:
            if entry != None:
                if entry[0] > 40:
                    myQueue.insert([entry[0], entry[1]])
                if myQueue.size() > 10:
                    return myQueue

class PriorityQueue(object):
    def __init__(self):
        self.queue = []

    def __str__(self):
        return ' '.join([str(i) for i in self.queue])

    # for checking if the queue is empty
    def isEmpty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)

    # for inserting an element in the queue
    def insert(self, data):
        self.queue.append(data)

    # for popping an element based on Priority
    def delete(self):
        try:
            max_val = 0
            for i in range(len(self.queue)):
                if self.queue[i] > self.queue[max_val]:
                    max_val = i
            item = self.queue[max_val]
            del self.queue[max_val]
            return item
        except IndexError:
            print()
            exit()

if __name__ == '__main__':
    file1 = open("test2.txt", "r")
    lines = file1.readlines()
    seed_load_queue = loadSeeds(lines)
    if seed_load_queue:
        print(queue(seed_load_queue))



    # pool_range = len(lines)
    # print("pool_range: ", pool_range)
    # with Pool(pool_range) as p:
    #     p.map(queue, [lines])
    # # localRepository(internal_link)


# def localRepository(internal_links):
#     with open('output.txt', 'w') as f:
#         for link in internal_links:
#             f.write(str(link))
#             f.write(" ")
#             f.write(str(link))
#             f.write("\n")
