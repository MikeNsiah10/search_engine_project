import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

#defined class to parse HTML pages
class Crawler():
    def __init__(self, urls):
        #initialise start urls and keep track of visited urls
        self.visited_urls = []
        self.url_to_visit = urls

    def crawl(self):
        #perform a web crawl
        while self.url_to_visit:
            #pop the start url and add to visited urls
            url = self.url_to_visit.pop(0)
            self.visited_urls.append(url)
            #extract HTML content and handle exceptions
            try:
             html = requests.get(url,timeout=3).text
            except:
             print(f'unable to fetch html content from {url}')
            continue
        soup = BeautifulSoup(html, 'html.parser')
            #extract the links 
        for link in soup.find_all('a'):
                link_path = link.get('href')
                if link_path and link_path.startswith('/'):
                    link_path = urljoin(url, link_path)
                    #add urls to the list if not visited
                    if link_path not in self.visited_urls and link_path not in self.url_to_visit:
                        self.url_to_visit.append(link_path)
    # create the index with title,content,url
    def create_index(self):
        schema = Schema(title=TEXT(stored=True), content=TEXT(stored=True), path=ID(stored=True))
        index_dir = "indexdir"
        #create directory if path does not exist
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)
        
        index = create_in(index_dir, schema)
        
        writer = index.writer()
        
        for url in self.visited_urls:
             #extract HTML content and handle exceptions
            try:
              html = requests.get(url,timeout=3).text
            except:
              print(f'unable to fetch html content from {url}')
              continue
            soup = BeautifulSoup(html, 'html.parser')
            # get the title of the page
            title_tag = soup.find('title')
            title_text = title_tag.text if title_tag else "no title was found"
            # get content_text
            content_text = soup.get_text()
            #add document to search index
            writer.add_document(title=title_text, content=content_text, path=url)
        writer.commit()

    def search(self, words):
        #perform search using the search index
        index_dir = "indexdir"
        index= open_dir(index_dir)
        
        with index.searcher() as searcher:
            query = QueryParser("content", index.schema).parse(" ".join(words))
            results = searcher.search(query)
            
            for result in results:
                print("Title:", result['title'])
                print("URL:", result['path'])
                print("Teaser_Text:", result.highlights("content"))
                print()

# testing code

crawler = Crawler(urls=['https://vm009.rz.uos.de/crawl/index.html'])
crawler.crawl()
crawler.create_index()
crawler.search(["platypus","welcome"])