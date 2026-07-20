from urllib.parse import urlparse
import time
import requests
from bs4 import BeautifulSoup
from googlesearch import search

class JobQueue:
    def __init__(self):
        self.queue = []
        self.results = []

    def add_urls(self, urls_text):
        """Parse a block of text containing URLs and add valid ones to the queue."""
        lines = urls_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Basic URL validation
            try:
                result = urlparse(line)
                if all([result.scheme, result.netloc]):
                    self.queue.append(line)
            except ValueError:
                pass

    def get_next_job(self):
        if self.queue:
            return self.queue.pop(0)
        return None

    def add_result(self, url, status, message):
        self.results.append({
            "url": url,
            "status": status,
            "message": message,
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        })

class JobSearcher:
    def __init__(self):
        pass

    def search_greenhouse_jobs(self, keywords, num_results=5):
        """
        Searches for greenhouse jobs using Google.
        Query: site:boards.greenhouse.io {keywords}
        """
        query = f"site:boards.greenhouse.io {keywords}"

        job_urls = []
        try:
            for url in search(query, num_results=num_results):
                if 'boards.greenhouse.io' in url:
                    job_urls.append(url)

            return job_urls
        except Exception as e:
            print(f"Search failed: {e}")
            return []
