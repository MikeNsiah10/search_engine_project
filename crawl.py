import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

# Defined class to parse HTML pages
class Crawler():
    def __init__(self, urls):
        # Initialise start urls and keep track of visited urls
        self.visited_urls = []
        self.url_to_visit = urls

    def crawl(self):
        # Perform a web crawl
        while self.url_to_visit:
            # Pop the start url and add to visited urls
            url = self.url_to_visit.pop(0)
            self.visited_urls.append(url)
            # Extract HTML content and handle exceptions
            try:
                html = requests.get(url, timeout=3).text
            except Exception as e:
                print(f"Unable to fetch HTML content from {url}: {e}")
                continue

            soup = BeautifulSoup(html, 'html.parser')
            # Extract the links
            for link in soup.find_all('a'):
                link_path = link.get('href')
                if link_path and link_path.startswith('/'):
                    link_path = urljoin(url, link_path)
                    # Add URLs to the list if not visited
                    if link_path not in self.visited_urls and link_path not in self.url_to_visit:
                        self.url_to_visit.append(link_path)

    # Create the index with title, content, url, and definition
    def create_index(self):
        schema = Schema(title=TEXT(stored=True), content=TEXT(stored=True), path=ID(stored=True), definition=TEXT(stored=True))
        index_dir = "indexdir"
        # Create index_directory if index_directory does not exist
        if not os.path.exists(index_dir):
            os.makedirs(index_dir)

        index = create_in(index_dir, schema)

        writer = index.writer()

        for url in self.visited_urls:
            # Extract HTML content and handle exceptions
            try:
                html = requests.get(url, timeout=3).text
            except Exception as e:
                print(f"Unable to fetch HTML content from {url}: {e}")
                continue

            soup = BeautifulSoup(html, 'html.parser')
            # Get the title of the page
            title_tag = soup.find('title')
            title_text = title_tag.text if title_tag else "No title was found"
            # Get content_text and remove HTML tags
            content_text = ' '.join(soup.stripped_strings)
            # Add document to search index
            writer.add_document(title=title_text, content=content_text, path=url)

        writer.commit()

    def search(self, words):
    # Perform search using the search index
     index_dir = "indexdir"
     index = open_dir(index_dir)

     with index.searcher() as searcher:
        query = QueryParser("content", index.schema).parse(" ".join(words))
        results = searcher.search(query)
        # Return results of search with title, url, teaser_text, and definition
        for result in results:
            # Extract title, URL, and teaser_text without HTML tags
            title_text = result['title']
            url = result['path']
            teaser_text = ' '.join(BeautifulSoup(result.highlights("content"), 'html.parser').stripped_strings)

            # Print the extracted information
            print("Title:", title_text)
            print("URL:", url)
            print("Teaser_Text:", teaser_text)
            print()

# Testing code
# Create an instance of the crawler class
crawler = Crawler(urls=['https://vm009.rz.uos.de/crawl/index.html'])
crawler.crawl()
crawler.create_index()
crawler.search(["platypus", "welcome"])
