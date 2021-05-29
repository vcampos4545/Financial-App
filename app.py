import os, csv
import talib
import yfinance as yf
import pandas
import datetime as dt
from flask import Flask, escape, request, render_template
from talib_patterns import candlestick_patterns
from chartlib import consolidating_stocks, breakout_stocks
from scraper import get_tickers, get_SANDP_tickers, get_sentiment
from algorithms import scalp_live

app = Flask(__name__)

@app.route('/algorithms')
def algorithms():
    path = os.getcwd()
    algos = os.listdir(path+'/algorithms')
    for i,a in enumerate(algos):
        if a[-3:] != '.py':
            del algos[i]

    algo = request.args.get('algo', False)
    print(algo)
    if algo == 'scalp_live.py':
        strat = getattr(scalp_live,'Strategy')
        strat.run()
    
    return render_template('algorithms.html',algos=algos)

@app.route('/updateData')
def updateData():
    tickers = get_SANDP_tickers()
    data = yf.download(tickers, start="2020-01-01", end=str(dt.date.today()))
    for symbol in tickers:
        data[symbol].to_csv(f'datasets/daily/{symbol}.csv')

    return {
        "code": "success"
    }

@app.route('/sentiment', methods=["GET", "POST"])
def sentiment():
    if request.method == 'POST':
        ticker = request.form['ticker']
        sentiment = get_sentiment(ticker)
    else:
        ticker = None
        sentiment = None

    print(ticker, sentiment)
    return render_template('sentiment.html', sentiment=sentiment, ticker = ticker)

@app.route('/breakout')
def breakout():
    pattern = request.args.get('pattern', False)
    if pattern == 'Consolidating':
        stocks = consolidating_stocks()
    elif pattern == 'Breakout':
        stocks = breakout_stocks()
    else:
        stocks = None

    return render_template('breakout.html', pattern = pattern, stocks=stocks)

@app.route('/candle')
def candle():
    pattern  = request.args.get('pattern', False)
    stocks = {}

    tickers = get_tickers()
    for symbol in tickers:
        stocks[symbol] = {'company': symbol}

    if pattern:
        for filename in os.listdir('datasets/daily'):
            df = pandas.read_csv('datasets/daily/{}'.format(filename))
            pattern_function = getattr(talib, pattern)
            symbol = filename.split('.')[0]

            try:
                results = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
                last = results.tail(1).values[0]

                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    stocks[symbol][pattern] = None
            except Exception as e:
                print('failed on filename: ', filename)

    return render_template('candle.html', candlestick_patterns=candlestick_patterns, stocks=stocks, pattern=pattern)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug = True)
