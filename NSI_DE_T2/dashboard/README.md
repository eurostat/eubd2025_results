# The dashboard of EU Quokka - the quality of life tracker

This implementation consists of a very thin Python-Flask server, which delivers the HTML pages. The interactive maps use the [gridviz JavaScript library by Eurostat](https://github.com/eurostat/gridviz). The data folder contains the preprocessed data as parquet files. 

## Prerequisites

You need Python 3 with Flask and Pandas to run the server.py script.

## Getting Started

Run

``` python3 server.py ```

Then access http://127.0.0.1:5000 in your browser.
