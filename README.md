# nba-data-models

This repository contains explorations and models of NBA data. 

## NBA Data Scraping

In "Data_Scraping" there are many notebooks which were used to amass datasets from a variety of basketball data websites. 

Note that only free data was used in this project; even the Synergy data used (advanced player tracking, etc.) is publicly available and scrapable using the custom tools contained in this repository.

Various data scraping tools were used: Scrapy (an open source Python web crawler library built using the Twisted framework), Selenium (a web browser automation tool), GeckoDriver/ChromeDriver for Firefox/Chrome browser launching, and the lxml HTML parsing library.

To scrape HTML data from simple, static webpages, Scrapy is used. This is done for the following sites:

* https://www.basketball-reference.com (for some basic and advanced stats not obtained from NBA.com)
* http://www.espn.com/nba/statistics/rpm (for ESPN Real Plus-Minus advanced player stats)
* http://insider.espn.com/nba/hollinger/statistics/_/qualified/false (for advanced Hollinger player stats)

The data obtained from these webpages are stored in JSON formats as player-season dictionaries, containing per-season stats.


For interactive, dynamic pages served using Javascript, web drivers are used to launch headless browser instances and Selenium and lxml are used to make table selections and parse the HTML:

* https://stats.nba.com/draft/combine-anthro (for draft combine data on drafted players)
* https://stats.nba.com/players (for aggregate player data and player bios)
* https://stats.nba.com/lineups (for aggregate lineup data)
* https://stats.nba.com/game (for play-by-play data for individual games)

The data obtained from these webpages are stored in CSV format. 


Player data is combined using a cleanup script which merges Pandas dataframes into a comprehensive player-season database (this combines draft combine, bio, basic, and advanced stats). Player, lineup, and play-by-play datasets are stored in separate CSV files.


## Exploration of Player, Lineup, and Play-by-Play Data


## Modeling for Player and Lineup Evaluation

The "Data_Modeling" directory contains some NBA models in various stages of development.
