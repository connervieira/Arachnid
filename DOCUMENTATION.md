# Documentation

This file explains how to get Arachnid up and running.


## Setup

To get Arachnid set up and running, follow these instructions:

1. Download Arachnid's source code.
    - Example: `git clone https://github.com/connervieira/Arachnid.git`
2. Change into the Arachnid directory.
    - Example: `cd Arachnid`
3. Install the required Python libraries.
    - Example: `pip3 install requests; pip3 install validators`
4. Run Arachnid.
    - Example: `python3 main.py`

## Usage

Once you've gotten Arachnid up and running, these instructions will help you run your first site scan.

1. Enter the page you'd like to start scanning from. This should probably be your website's index page. Please note that you should include the exact path of your index page, not a location that gets redirected to it.
    - Example: `http://localhost/index.php`
2. Enter a number of how many pages you'd like to crawl. This should not be treated as an exact number, and generally a few more pages will be crawled than you specify due to redirects that may confuse Arachnid.
3. Press enter to start a scan.
4. After the scan completes, press enter to view the main Arachnid menu. Simply select a choice in the menu to analyze your scan results.
