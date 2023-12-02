import requests
from bs4 import BeautifulSoup
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from urllib.parse import urljoin, urlparse

class Crawler:
    def __init__(self, starting_url):
        # Initialize  crawler with astarting URL
        self.starting_url = starting_url
        # Stack for URLs to be crawled
        self.stack = [starting_url]
        # keep track of visited URLs
        self.visited = set()

        # Define the schema for the Whoosh index
        self.schema = Schema(url=TEXT(stored=True), title=TEXT(stored=True), content=TEXT(stored=True))
        self.index_dir = "indexdir"
        self.index = create_in(self.index_dir, self.schema)

    def crawl(self):
        # Crawl the web 
        while self.stack:
            # Pop  URL from the stack
            url = self.stack.pop(0)
            if url not in self.visited:
                try:
                    # Send an HTTP request to the URL
                    response = requests.get(url, timeout=5)
                    print(f"Current URL: {url}")

                    if response.status_code == 200:
                        # Parse the HTML content of the page
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Extract title text or set a default if not found
                        title_text = soup.find('title').text if soup.title else "No title was found"
                        # Extract content without HTML tags
                        content = ' '.join(soup.stripped_strings)

                        # Add the document to the Whoosh index
                        with self.index.writer() as writer:
                            writer.add_document(url=url, title=title_text, content=content)

                        # Mark the URL as visited
                        self.visited.add(url)

                        # Extract and add new URLs from the page to the stack
                        for link in soup.find_all('a', href=True):
                            absolute_url = urljoin(url, link['href'])
                            if urlparse(absolute_url).netloc == urlparse(self.starting_url).netloc:
                                if absolute_url not in self.visited and absolute_url not in self.stack:
                                    self.stack.append(absolute_url)

                except Exception as e:
                    # Handle exceptions during the crawling process
                    print(f"Error while processing {url}: {e}")

            # Print status information
            print(f"Stack of websites left: {self.stack}")
            print(f"Crawled websites: {self.visited}")

    def search(self, query):
        # Search the Whoosh index given a query
        with self.index.searcher() as searcher:
            # Parse the query and search for matching documents
            query = QueryParser("content", self.index.schema).parse(query)
            # return a list of results with URL, title, and content
            results = [{'url': result['url'], 'title': result['title'], 'content': result['content']}
                       for result in searcher.search(query)]
            return results

# Testing code
#create an instance of the class
crawler = Crawler(starting_url='https://vm009.rz.uos.de/crawl/')
crawler.crawl()
search_word = "plapytus"  # 
crawler.search(search_word)
