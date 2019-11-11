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
