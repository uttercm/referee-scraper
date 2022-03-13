# referee-scraper
For my own scraper of Ohio's referee assignments

## Install

1. Make sure python 3 is installed
    `python3 --version`
2. Install dependencies
    `pip3 install -r requirements.txt`

## Running the application

`python3 -m app`

Arguments:

*LEAGUE*
For scraping one of the different websites either `mv` or `ohiosouth`.

*FORMAT*
For choosing a way to scrape the website either with beautiful soup, `scraper`, or by downloading the linked spreadsheet csv, `csv`.

## Functionality

### Downloading and parsing the CSV

The CsvReader is for downloading the generated csv file from the website.

### Parse through beautiful soup

When the csv file is unavailable to download we need to use beautiful soup to actually webscrape for games.