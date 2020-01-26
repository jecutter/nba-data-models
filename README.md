# nba-data-models

This repository contains explorations and models of NBA data. 

## NBA Data Scraping

In "Data_Scraping" there are many notebooks which were used to amass datasets from a variety of NBA websites. 

Note that no data used in this project was paid for -- even Synergy data used (advanced player tracking, etc.) is publicly available and scrapable using the tools provided.

Various data scraping tools were used: Scrapy (an open source Python web crawler library built using the Twisted framework), Selenium (a web browser automation tool), GeckoDriver/ChromeDriver for Firefox/Chrome browser launching, and lxml HTML parsing.

To scrape HTML data from simple, static webpages, Scrapy is used. This is done for the following pages:
* https://www.basketball-reference.com (for some basic and advanced stats not obtained from NBA.com)
* http://www.espn.com/nba/statistics/rpm (for ESPN Real Plus-Minus advanced player stats)
* http://insider.espn.com/nba/hollinger (for advanced Hollinger player stats)

For interactive, dynamic pages served using Javascript, web drivers are used with Selenium and lxml to make table selections and parse the HTML:
* https://stats.nba.com/draft/combine-anthro (for draft combine data on drafted players)
* https://stats.nba.com/players (for aggregate player data and player bios)
* https://stats.nba.com/lineups (for aggregate lineup data)
* https://stats.nba.com/game (for play-by-play data for individual games)
