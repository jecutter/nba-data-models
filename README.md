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

The "Player_Data_Exploration" notebook breaks down and explores a vast number of player stats. 

In particular, a basic clustering is performed for players of each general position (Guard, Forward, Center).
K-means clustering is used to lump players into categories based on a few key traits:

* Passing/play-making ('AST_PH', 'ASTR', 'ATR')
* Frequency of 3 point shots ('3PR')
* Defensive specialization ('BLK_PH', 'DFGP_3PT_PG', 'DFGP_PG')
* Usage rate ('USG')

The stats used for clustering are chosen for each position through trial-and-error, using silhouette scores to evaluate the best training features. This silhouette analysis also gives the optimal number of clusters to use at each position.

This notebook examines offensive and defensive performance metrics (including the relationship between different efficiency stats), shot selection (including distance from basket, number of dribbles, and defender proximity), and offensive and defensive play types used.


## Modeling for Player and Lineup Evaluation

The "Data_Modeling" directory contains some NBA models in various stages of development.

### Play Style Modeling

The "Player_Comparison_Analysis" notebook contains a simple classification model for finding the best player comp for first-year/rookie players. Veteran players (defined as players to play in all of the last 4 full NBA seasons) are divided into player-seasons, the first 3 seasons being used for model training and the last season being used for testing and validation. 

The classification model is built using key stylistic player stats, specifically:
* 'height' - player height in inches
* 'weight' - player weight in lbs
* 'FG_FREQ_05FT' - percentage of shots from 0-5 ft. from the basket
* 'FG_FREQ_59FT' - percentage of shots from 5-9 ft. from the basket
* 'FG_FREQ_1014FT' - percentage of shots from 10-14 ft. from the basket
* 'FG_FREQ_1519FT' - percentage of shots from 15-19 ft. from the basket
* 'FG_FREQ_2024FT' - percentage of shots from 20-24 ft. from the basket
* 'FG_FREQ_GT24FT' - percentage of shots from > 24 ft. from the basket
* 'FG_FREQ_CANDS' - percentage of shots that are catch-and-shoot (no dribbles)
* 'FTR' - free throw rate
* 'ASTR' - assist rate
* 'TOR' - turnover rate
* 'ORR' - offensive rebounding rate
* 'DRR' - defensive rebounding rate
* 'BLK_PH' - shot blocks (per 100 possessions)
* 'STL_PH' - steals (per 100 possessions)
* 'DFGP_PG' - defensive/opponent field goal percentage

A variety of permutations were attempted to optimize the testing results, however accuracy of player classification (identifying a veteran player by their 4th season using the model) maxed out at ~75%. This is reasonable, given the variance of player stats from season to season.

Predictive results are then shown by classifying rookies/first-year players from the 2018-2019 season. This demonstrates the usefulness of this algorithm as a scouting tool for assessing a player's play style.

### Player Impact Evaluation

The "RAPM_Ridge_Regression" model uses lineup matchup data over 3 full seasons of NBA games to calculate a player's lineup-independent impact. This can be done with ridge regression to calculate a known quantity called "RAPM" (Regularized Adjusted Plus-Minus).

A player's +/- is defined as the team's point differential (relative to the opposing team) while that player is on the floor. A player's offensive and defensive impact both affect their raw +/-, but it is a lineup-dependent quantity since it depends on the player's supporting cast as well as the opposing lineups. 

The way to take into account all players on the floor is to calculate the "APM" (Adjusted Plus-Minus). This is obtained by creating a matchup matrix *M*, where each row is a lineup matchup and each column is a player. A matrix entry is set to "1" if the player is on offensve, "-1" if the player is on defense, and "0" if the player is not involved in the matchup. The point differential per 100 possessions is calculated for each lineup matchup, which forms an array *y*. We may then solve the equation *M* *x* = *y* for player coefficients *x*, which represent the players' adjusted contributions.

The problem with this method is that there is enormous variance in the coefficients due to multicollinearity between players. We therefore perform a modified/perturbed regression, a Bayesian filtering process which introduces bias but greatly reduces the variance by penalizing (regularizing) outliers. The result is a set of player RAPM coefficients, which give a relative ranking of the player's impact. More mathematical details are given in the notebook.

Validation of the RAPM model is difficult, since it incorporates a global dataset to produce relative (but biased) player rankings. This means that it is not particularly useful for predicting true lineup matchup results. However, it is useful for scouting players whose impact may be underrated by their environment or have winning qualities that are intangible.

### Lineup Optimization

Work in progress.
