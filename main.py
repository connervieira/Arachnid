# Arachnid
# V0.2
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
import json
import validators


pages_found = 0 # This counts how many pages were discovered in links on crawled pages, including duplicates.
pages_visited = 0 # This counts how many pages were crawled by Arachnid.

discovered_pages_list = [] # This keeps track of all pages discovered in links on crawled pages.
page_error_list = {} # This will be used to keep track of all pages that return errors (404, 403, etc.)


# Define the funtion that will be used to clear the screen
def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')


# Locates links in pages
class AnchorParser(HTMLParser):
    def __init__(self, baseURL = ""):
        # Parent class constructor
        HTMLParser.__init__(self)

        # Set of all hyperlinks in the web page
        self.pageLinks = set()

        # The base url of the webpage to parse
        self.baseURL = baseURL

    def getLinks(self):
        return self.pageLinks

    def handle_starttag(self, tag, attrs):
        global page_error_list
        if tag == "a":
            for(attribute, value) in attrs:
                if attribute == "href":
                    absoluteUrl = urljoin(self.baseURL, value)
                    if urlparse(absoluteUrl).scheme in ["http", "https"]: # Only follow links that use HTTP or HTTPS
                        if (urlparse(site_to_test).netloc in str(absoluteUrl)): # Only follow links on the same domain as the initial page
                            global pages_found
                            global discovered_pages_list
                            pages_found = pages_found + 1
                            discovered_pages_list += [absoluteUrl]
                            self.pageLinks.add(absoluteUrl)

                            r = requests.head(absoluteUrl, allow_redirects = True)
                            if (r.status_code != 200): # If the returned status code is anything other than 200, log it.
                                global page_error_list

                                # Initialize page error list if it hasn't been already
                                if str(r.status_code) not in page_error_list:
                                    page_error_list[str(r.status_code)] = {}

                                if self.baseURL not in page_error_list[str(r.status_code)]:
                                    page_error_list[str(r.status_code)][self.baseURL] = []
                                
                                # Save the errors to the list if they haven't yet been recorded
                                if absoluteUrl not in page_error_list[str(r.status_code)][self.baseURL]:
                                    page_error_list[str(r.status_code)][self.baseURL].append(absoluteUrl)

        elif tag == "html":
            lang_is_set = False # This is a placeholder variable that will be changed to true if this HTML tag has a 'lang' attribute
            for(attribute, value) in attrs:
                if attribute == "lang":
                    lang_is_set = True
            if lang_is_set == False:

                # Initialize page error list if it hasn't been already
                if "no-lang" not in page_error_list:
                    page_error_list["no-lang"] = {}

                if self.baseURL not in page_error_list["no-lang"]:
                    page_error_list["no-lang"][self.baseURL] = []
                                
                # Save the errors to the list if they haven't yet been recorded
                absoluteUrl = self.baseURL
                if absoluteUrl not in page_error_list["no-lang"][self.baseURL]:
                    page_error_list["no-lang"][self.baseURL] = {}

        elif tag == "img":
            alt_is_set = False # This is a placeholder variable that will be changed to true if this img tag has an 'alt' attribute
            for(attribute, value) in attrs:
                if attribute == "alt":
                    alt_is_set = True
            if alt_is_set == False:
                for(attribute, value) in attrs:
                    if attribute == "src":
                        image_link = value
                    

                        # Initialize page error list if it hasn't been already
                        if "no-alt" not in page_error_list:
                            page_error_list["no-alt"] = {}

                        if self.baseURL not in page_error_list["no-alt"]:
                            page_error_list["no-alt"][self.baseURL] = []
                                
                        # Save the errors to the list if they haven't yet been recorded
                        absoluteUrl = self.baseURL
                        if image_link not in page_error_list["no-alt"][self.baseURL]:
                            page_error_list["no-alt"][self.baseURL].append(image_link)


class MyWebCrawler(object):
    def __init__(self, url, maxCrawl=10):
        self.visited = set() # To track all visited urls
        self.starterUrl = url
        self.max = maxCrawl

    def crawl(self):
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
                if (self.parse(nextUrl) is not None and urlsToParse is not None):
                    urlsToParse |= self.parse(nextUrl)

    def parse(self, url):
        try:
            # Open the URL, read content, decode content
            url_response = urlopen(url, context=_create_unverified_context())
            htmlContent = url_response.read().decode()
            
            if (url_response.geturl() == url):
                # Initiate the AnchorParser object
                parser = AnchorParser(url)
                # Feed in the HTML content to our AnchorParser object
                parser.feed(htmlContent)
                # The AnchorParser object has a set of absolute URLs that can be returned
                return parser.getLinks()
            else:
                print("Redirect detected, not logging page")
            
        except (HTTPError, InvalidURL, UnicodeDecodeError):
            # In the case we get any HTTP error
            return set()

    def getVisited(self):
        return self.visited
 

while True:
    site_to_test = input("Please enter a page to crawl: ")
    if validators.url(site_to_test) == True:
        break
    else:
        print("Error: The page you entered isn't a valid URL")


max_crawl = int(input("Please enter a maximum number of pages to crawl: "))

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
    print("4. Check raw status codes of discovered pages")
    print("5. Check human-readable website issues")

    while True: # Run forever until the user enters something
        selection = input("Selection: ")
        if selection != None and selection != "":
            selection = int(selection)
            break
        else:
            print("Error: Please enter a number to select which menu you'd like to open")

    clear()
    if (selection == 0):
        break # Break the loop and exit
    elif (selection == 1):
        print(format(crawler.getVisited())) # Print visited pages
        input("") # Wait for the user to press enter before continuing
    elif (selection == 2):
        print(discovered_pages_list) # Print discovered pages
        input("") # Wait for the user to press enter before continuing
    elif (selection == 3):
        print("Pages visited: " + str(pages_visited))
        print("Pages found: " + str(len(discovered_pages_list)))
        input("") # Wait for the user to press enter before continuing
    elif (selection == 4):
        print("Please enter an error code to check for. Enter 0 to show all.")
        selection = input("Selection: ")
        
        if (selection == "0"):
            print(json.dumps(page_error_list, sort_keys=True, indent=4)) # Print the array in a visually appealing, easy to understand way.
        else:
            if (str(selection) in page_error_list):
                print(json.dumps(page_error_list[str(selection)], sort_keys=True, indent=4)) # Print the array in a visually appealing, easy to understand way.
            else:
                print("No pages returned this error!")
        input("") # Wait for the user to press enter before continuing

    elif (selection == 5):
        while True:
            clear()
            print("0. Exit")
            print("1. View 'Page Not Found' errors")
            print("2. View 'Permission Denied' errors")
            print("3. View 'No Language Defined' errors")
            print("4. View 'No Image Alt Text' errors")
            selection = input("Selection: ")
        
            if (selection == "0"):
                break
            elif (selection == "1"):
                clear()
                print("Pages with 404 errors")
                if "404" in page_error_list:
                    for page in page_error_list["404"]:
                        print(page + ":")
                        for errors in page_error_list["404"][page]:
                           print("\t" + errors)
                else:
                    print("No pages returned 404 errors!")
                input("") # Wait for the user to press enter before continuing
            elif (selection == "2"):
                clear()
                print("Pages with 403 errors:")
                if "403" in page_error_list:
                    for page in page_error_list["403"]:
                        print(page + ":")
                        for errors in page_error_list["403"][page]:
                            print("\t" + errors)
                else:
                    print("No files returned 403 errors!")
                input("") # Wait for the user to press enter before continuing
    
            elif (selection == "3"):
                clear()
                print("Pages missing HTML language data:")
                if "no-lang" in page_error_list:
                    for page in page_error_list["no-lang"]:
                        print(page)
                else:
                    print("All scanned pages had properly configured HTML language data!")
                input("") # Wait for the user to press enter before continuing

            elif (selection == "4"):
                clear()
                print("Missing alt text instances:")
                if "no-alt" in page_error_list:
                    for page in page_error_list["no-alt"]:
                        print(page)
                        print("\t" + str(len(page_error_list["no-alt"][page])) + "\n")
                else:
                    print("All scanned images had properly configured alt-text!")
                input("") # Wait for the user to press enter before continuing

            else:
                clear()
                print("Error: Invalid selection")
                input("") # Wait for the user to press enter before continuing
        

    else:
        clear()
        print("Error: Invalid selection")
        input("") # Wait for the user to press enter before continuing
