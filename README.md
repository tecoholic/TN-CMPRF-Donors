# Tamil Nadu Chief Minister's Relief Fund Donors

Scrapped data from https://ereceipt.tn.gov.in/cmprf/Interface/CMPRF/MonthWiseReport

## Scrapper

- `scrapper.py` contains the working scraper using Python Selenium and Pandas.
- `scrapper` folder contains a Scrapy spider which attempted to do the same. The pagination couldn't be handled and will probably scrap the data faster if pagination is figured out.

## Data

All the data is in the `data` folder as CSV files named `<year>_<month>.csv`. These are dumps from Pandas Data Frames and might have inconsistent column ordering. Best used for programmatic manipulation.
