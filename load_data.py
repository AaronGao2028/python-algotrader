import yfinance as yf
import csv

start_date = '2024-09-09'
end_date = '2024-09-16'
interval = '1m'
data = []

with open("tickers.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        data.append(row)

for row in data:
    ticker = row[0]
    file_name = ticker + '_' + start_date + '_' + end_date + '.csv'
    data = yf.download(tickers=ticker, start=start_date, end=end_date, interval=interval, prepost=False)
    data.to_csv('historical_data/'+file_name)