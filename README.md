# referee-scraper

For my own scraper of Ohio's referee assignments and adding them to Google Calendar.

## Install

1. Make sure python 3 is installed
   `python3 --version`
2. Install dependencies
   `pip3 install -r requirements.txt`

## Setup

1. copy the `login_info_sample.json` and name the file `login_info.json`. Then edit that file for the credentials for your login to each website.

## Running the application

`python3 -m app`

Arguments:

_SITE_
For scraping one of the different websites. Defaults to `ohiosouth`. Available options are `ohiosouth` and `mvysa`.

## Functionality

### Parse through beautiful soup

We use beautiful soup to webscrape for games matching the configured name and adds games assigned to a linked Google Calendar. It then emails the configured to_email.
