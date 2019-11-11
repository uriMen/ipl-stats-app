# Football Stats Dashboard

An interactive visualization app for displaying [Israeli Premier League](https://www.football.co.il/en/) statistics.  
The plots were designed with a purpose of giving the user a deeper perspective about teams and players performances, thus gaining useful insights.

Some example plots:

![](https://github.com/uriMen/ipl-stats-app/blob/master/examples/app_example%20(3).png) ![](https://github.com/uriMen/ipl-stats-app/blob/master/examples/app_example2.png)

## Motivation

Creating an end-to-end data project with python, which includes collecting (web scraping with [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) and [Selenium](https://selenium-python.readthedocs.io/)), cleaning and manipulating (with [Pandas](https://pandas.pydata.org/pandas-docs/stable/)) and visualizing (with [Bokeh](https://docs.bokeh.org/en/latest/)) the data.

## Usage

After installation (details below), running the app is as easy as typing `bokeh serve --show ipl-stats-app` in your terminal. This will automatically open the interactive dashboard in your browser.

![](https://github.com/uriMen/ipl-stats-app/blob/master/examples/app_example4.gif)

## Getting Started

As mention above, the app is written in Python (3.7), so I'm assuming you have it installed.  
In addition, you'll need to have the following packages installed (can be `pip` installed):
> numpy, pandas, bokeh

Now, download the directory as is, open you terminal and navigate to the directory that contains the downloaded one. From here just type `bokeh serve --show ipl-stats-app` (assuming 'ipl-stat-app' is the name of the downloaded directory).

## Update Data Tables

The app now runs with the downloaded data tables, which are probably not updated. In order to update them you'll need to run `main_data_collector.py` which is found under `data_scraping/scripts`, but before you do that you'll have to do the following:
* pip install additional packages for web scraping:
  >selenium, beautifulsoup4, datetime
* Download [Chrome WebDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) and place it in `data_scraping/scripts`
* Open the file `data_scraping/scripts/stats.py` find the function  
```python
def stats_per_game_wrapper(driver, item_type='player'): 
```
and change the parameter `gws` to include the last played round. For example, if the last played matches were part of game week 13, change as follows:
```python
gws = range(1, 14)
```

That's it, you're ready to trun the data collector.

##### Notes:

1. Stats can be collected for previous seasons as well, by changing the parameter `seasons` in the above mentioned function, for example 
```python
seasons = ['18/19', '19/20']
``` 
However, currently matches results of other seasons are not available in the website, so it might cause errors.
