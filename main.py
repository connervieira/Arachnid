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


pages_found = 0
pages_visited = 0


# Define the funtion that will be used to clear the screen
def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')


class AnchorParser(HTMLParser):
    "Basic HTML parser that gathers a set of all href values in a webpage by targetting the anchor tag"

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
                            pages_found = pages_found + 1
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
            # Skip the next URL if it has already been visited
            global pages_visited
            global pages_found
            pages_visited = pages_visited + 1
            clear()
            print("Pages visited: " + str(pages_visited))
            print("Pages found: " + str(pages_found))
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
        """Returns the set of URLs visited
        Note: Will include urls that raised HTTPError and InvalidURL
        Returns:
            set: All URLs visited/parsed
        """
        return self.visited

site_to_test = input("Please enter a site to crawl: ")
max_crawl = input("Please enter a maximum number of pages to crawl: ")

crawler = MyWebCrawler(site_to_test, maxCrawl=int(max_crawl))

print("Crawling site")

crawler.crawl()


while True:
    clear()

    print("Crawl complete. What would you like to do next?")
    print("1. View visited domains")
    print("2. View discovered domains")
    print("3. View statistics")
    selection = int(input("Selection: "))

    clear()
    if (selection == 1):
        print("The following sites were visited:\n{}".format(crawler.getVisited()))
    elif (selection == 2):
        print("Sorry, this feature has not yet been implemented.")
    elif (selection == 3):
        print("Pages visited: " + str(pages_visited))
        print("Pages found: " + str(pages_found))
    else:
        print("Error: Invalid selection")
    
    input("") # Wait for the user to press enter before continuing
