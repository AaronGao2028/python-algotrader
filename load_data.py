# Import Python Libraries
import yfinance as yf
import csv
import os
import shutil

# Start Date
start_date = '2024-09-23'
# End Date
end_date = '2024-09-27'
# Time Interval
interval = '1m'

# Remove existing stock data if it exists
if os.path.exists('historical_data'):
    shutil.rmtree('historical_data')

# Creates historical_data folder to store stock data
os.makedirs('historical_data')

# Read tickers of S&P 500 holdings from tickers.csv file and store the stock data
# retrieved from Yahoo Finance into .csv files in historical data folder
with open("tickers.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        ticker = row[0]
        
        # Format the file name to contain all the relevant information on a stock's historical data including
        # the ticker, the start date of data, the end date of data, and the interval of which the data is being
        # retrieved. This way the relevant data can easily be accessed in the generate_trades.py file
        file_name = ticker + '_' + start_date + '_' + end_date + '_' + interval + '.csv'
        
        stock_data = yf.download(ticker, start_date, end_date, interval=interval, prepost=False)
        stock_data.to_csv('historical_data/' + file_name)