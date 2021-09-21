# referee-scraper
For my own scraper of Ohio's referee assignments

## Install

1. Make sure python 3 is installed
    `python3 --version`
2. Install requests
    `pip3 install requests`
3. Install beautiful soup
    `pip3 install beautifulsoup4`
4. Install sendgrid
    `pip3 install sendgrid`
5. Make sure setup tools is installed
    `pip3 install setuptools`
6. Install google apis
    `pip3 install google-api-python-client`
7. Install google oauthlib
    `pip3 install google-auth-oauthlib`

## Running the application

`python3 -m app`

## Functionality

### Downloading and parsing the CSV

The CsvReader is for downloading the generated csv file from the website.

### Parse through beautiful soup

When the csv file is unavailable to download we need to use beautiful soup to actually webscrape for games.