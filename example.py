from flask import Flask, request, render_template
import os
import heapq
import requests
import multiprocessing
from multiprocessing import Pool, Process, Lock
import sys
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import time
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlparse, urlsplit, urljoin

from waitress import serve

app = Flask(__name__)
internal_link = []

@app.route("/")
def home():
    return render_template("home.html")

def concatenate(fname):
    ret_string = fname+" The method of this string has been tested"
    return ret_string

@app.route('/form', methods=["GET", "POST"])
def gfg():
    if request.method == "POST":
        first_name = concatenate(request.form.get("fname"))
        last_name = request.form.get("lname")
        examples = ['first', 'second', 'third', 'fourth', 'fifth']
        return render_template("form_return.html", f_name=first_name, l_name=last_name, list=examples)
    return render_template("form.html")

@app.route('/scraper', methods=['GET', 'POST'])
def scraper():
    errors =[]
    results = []
    if request.method == "POST":
        try:
            url = request.form['url']
            print(url)
            r = requests.get('https://www.bbc.co.uk/news')
            soup = BeautifulSoup(r.text, "html.parser")
            h2 = str(soup.findAll('h2'))
            results.append(h2)
        except:
            errors.append("Unable to get URL.")
    return render_template("scraper.html", errors=errors,results=results)

def loadSeeds(lines):
    myQueue = PriorityQueue()
    p = Pool(processes=5)
    data = []
    print("LOAD SEEDS: POOL PROCESSES")
    data = downloadClassificationTags(lines)
    print("DATA RETURN FROM DONWLOAD CLASSIFICATION TAGS")
    print(data)
    print("DATA LEN: ", len(data))
    print("data[0], data[1],", data[0], " space ", data[1])
    myQueue.insert([data[0], data[1]])
    print("MYQUEUE: ", myQueue)
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

def downloadClassificationTags(input_url):

    class_tags = {}


    print("before req_url url_used: ", input_url)

    try:
        req_url = requests.get(input_url, timeout=2).content

    except requests.ConnectionError as e:
        print(e)
        return None

    except requests.Response.raise_for_status() as e:
        print(e)
        return None

    print("after req_url")
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

    print("request successful")

    return [score, input_url]

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

def downloadClassTags(ret_urls):
    print("Download Class Tags Method: ret_urls")
    p = Pool(processes=20)
    data = []
    data = p.map(downloadClassificationTags, [i for i in ret_urls[:30]]) #:5 is a slice method that limits the number of URLs to search
    #No printout from pool method
    print("END OF downalodClassTags Pool method: ")
    print(data)
    return data

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

@app.route('/crawler', methods=['GET', 'POST'])
def crawler():
    errors =[]
    urls = []
    results = []
    if request.method == "POST":
        try:
            url = request.form['url']
            print("CRALWER URL = Request.form")
            seed_load_queue = loadSeeds(url)
            print("SEED LOAD QUEUE")
            if seed_load_queue:
                results = queue(seed_load_queue)
                print("TASK COMPLETE")
            # queue(urls)
        except:
            errors.append("Unable to get URL: ")
    return render_template("crawler.html", url=urls, errors=errors, results=results)


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/form")
def form():
    return render_template("form.html")

if __name__ == "__main__":
    app.run(threaded=True, debug=True, host='0.0.0.0')
    serve(app, host='0.0.0.0', port=5000, url_scheme='https')