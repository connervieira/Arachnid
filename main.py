# Arachnid
# V0.1
# V0LT
# Licensed under the GPLv3

from html.parser import HTMLParser
from urllib.request import urlopen
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError
from http.client import InvalidURL
from ssl import _create_unverified_context
import os
from os import system, name 
import requests


pages_found = 0 # This counts how many pages were discovered in links on crawled pages, including duplicates.
pages_visited = 0 # This counts how many pages were crawled by Arachnid.

discovered_pages_list = [] # This keeps track of all pages discovered in links on crawled pages.
pages_list_404 = [] # This keeps track of all pages that return 404 errors.
pages_list_403 = [] # This keeps track of all pages that return 403 errors.


# Define the funtion that will be used to clear the screen
def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')


# Locates links in pages
class AnchorParser(HTMLParser):
    def __init__(self, baseURL = ""):
        """Constructor for AnchorParser
        Args:
            baseURL (str): Base URL for the HTML content
        Returns:
            None
        """
        # Parent class constructor
        HTMLParser.__init__(self)
        # Set of all hyperlinks in the web page
        self.pageLinks = set()
        # The base url of the webpage to parse
        self.baseURL = baseURL

    def getLinks(self):
        """Return the set of absolute URLs in the HTML content
        Returns:
            set: Absolute URLs found in HTML content
        """
        return self.pageLinks

    def handle_starttag(self, tag, attrs):
        """Override handle_starttag to target anchor tags
        Returns:
            None
        """
        # Identify anchor tags
        if tag == "a":
            for(attribute, value) in attrs:
                # Anchor tags may have more than 1 attribute, but handle_starttag will only target href
                # Attribute examples: href, target, rel, etc
                # Attribute list can be found at: https://www.w3schools.com/tags/tag_a.asp
                if attribute == "href":
                    absoluteUrl = urljoin(self.baseURL, value)
                    if urlparse(absoluteUrl).scheme in ["http", "https"]: # Only follow links that use HTTP or HTTPS
                        if (urlparse(site_to_test).netloc in str(absoluteUrl)): # Only follow links on the same domain as the initial page
                            global pages_found
                            global discovered_pages_list
                            pages_found = pages_found + 1
                            discovered_pages_list += [absoluteUrl]
                            self.pageLinks.add(absoluteUrl)


class MyWebCrawler(object):
    "Basic Web Crawler using only Python Standard Libraries"

    def __init__(self, url, maxCrawl=10):
        self.visited = set() # To track all visited urls
        self.starterUrl = url
        self.max = maxCrawl

    def crawl(self):
        """Tracks URLs visited in a set in order to crawl through different sites
        Will only crawl through as many URLs as declared with 'maxCrawl' when instantiating MyWebCrawler
        Returns:
            None
        """
        urlsToParse = {self.starterUrl}
        # While there are still more URLs to parse and we have not exceeded the crawl limit
        while(len(urlsToParse) > 0 and len(self.visited) < self.max):
            # Get the next URL to visit and remove it from the set
            nextUrl = urlsToParse.pop()
            global pages_visited
            global pages_found
            pages_visited = pages_visited + 1
            clear()
            print("Pages visited: " + str(pages_visited))
            print("Pages found: " + str(pages_found))

            # Skip the next URL if it has already been visited
            if nextUrl not in self.visited:
                # Mark the next URL as visited
                self.visited.add(nextUrl)
                # Call the .parse method to make a web request
                # and parse any new URLs from the HTML content
                # any new URLs found will be appended to the urlsToParse set
                # print("Parsing: {}".format(nextUrl))
                urlsToParse |= self.parse(nextUrl)

    def parse(self, url):
        try:
            # Open the URL, read content, decode content
            htmlContent = urlopen(url, context=_create_unverified_context()).read().decode()
            # Initiate the AnchorParser object
            parser = AnchorParser(url)
            # Feed in the HTML content to our AnchorParser object
            parser.feed(htmlContent)
            # The AnchorParser object has a set of absolute URLs that can be returned
            return parser.getLinks()
        except (HTTPError, InvalidURL, UnicodeDecodeError):
            # In the case we get any HTTP error
            return set()

    def getVisited(self):
        return self.visited


def get_url_status(urls):
    for url in urls:
        try:
            print("Testing: " + url)
            r = requests.head(url)
            print(url + " Status: " + str(r.status_code) + "\n")
            if (r.status_code == 404):
                global pages_list_404
                pages_list_404.append (url)
            elif (r.status_code == 403):
                pages_list_403 += url
        except Exception as e:
            print("Failed to connect: " + str(e))

 

site_to_test = input("Please enter a site to crawl: ")
max_crawl = input("Please enter a maximum number of pages to crawl: ")

crawler = MyWebCrawler(site_to_test, maxCrawl=int(max_crawl))

crawler.crawl()

# Remove duplicates in 'discovered pages' list
discovered_pages_list = list(dict.fromkeys(discovered_pages_list))

clear()
print("Crawl complete")
input("") # Wait for the user to press enter before continuing

while True: # Run forever in a loop until the user exits
    clear()
    print("Please select an option")
    print("0. Exit")
    print("1. View visited pages")
    print("2. View discovered pages")
    print("3. View crawl statistics")
    print("4. Check status codes of discovered pages")
    selection = int(input("Selection: "))

    clear()
    if (selection == 0):
        break # Break the loop and exit
    elif (selection == 1):
        print(format(crawler.getVisited())) # Print visited pages
    elif (selection == 2):
        print(discovered_pages_list) # Print discovered pages
    elif (selection == 3):
        print("Pages visited: " + str(pages_visited))
        print("Pages found: " + str(len(discovered_pages_list)))
    elif (selection == 4):
        get_url_status(discovered_pages_list)
        clear()
        if (len(pages_list_404) > 0):
            print("404 pages: " + str(pages_list_404))
        else:
            print("No pages returned 404 errors!")

        if (len(pages_list_403) > 0):
            print("404 pages: " + str(pages_list_403))
        else:
            print("No pages returned 403 errors!")
    else:
        print("Error: Invalid selection")
    
    input("") # Wait for the user to press enter before continuing
