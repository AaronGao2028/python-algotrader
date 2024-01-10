# Imports from library
import pandas as pd 
import matplotlib.pyplot as plt 
import yfinance as yf
import matplotlib.pyplot as plt
from prettytable import PrettyTable

# Variables
long_MA_duration = 200
short_MA_duration = 20
long_MA = 0
short_MA = 0
long_MA_arr = []
short_MA_arr = []
long_MA_dates = []
short_MA_dates = []
crossover_dates = []
crossover_price = []
crossover_action = []
wealth = 1000
num_stock = 0
stock = 'PYPL'
start_date =  '2015-01-01'
end_date = '2023-01-01'
interval = '1d'
profit = 0
day = 0
previous = "below"
table = PrettyTable(["Date", "# of Shares", "Wealth ($)", "Action"])

# Get stock data from Yahoo Finance API
yf.pdr_override()
df = yf.download(tickers=stock, start=start_date, end=end_date, interval=interval)
df.reset_index(inplace=True) 
df['date'] = df['Date'].dt.date

for i in range (len (df)):
    price = df.loc[i, "Open"]
    date = df.loc[i, "Date"]
    
    long_MA += price/long_MA_duration
    short_MA += price/short_MA_duration
    
    day += 1
    
    if (day > long_MA_duration):
        long_MA -= df.loc[i-long_MA_duration, "Open"]/long_MA_duration
    if (day > short_MA_duration):
        short_MA -= df.loc[i-short_MA_duration, "Open"]/short_MA_duration
    
    if (day > short_MA_duration):
        short_MA_dates.append(date)   
        short_MA_arr.append(short_MA)   

    if (day > long_MA_duration): 
        long_MA_arr.append(long_MA)
        long_MA_dates.append(date)    
             
        # If the 20 day moving average crosses below the 200 day moving average,
        # the stocks will be sold
        if (short_MA < long_MA and previous == "above"):
            crossover_dates.append(date)
            crossover_price.append(price)
            crossover_action.append("Sell")
            wealth = num_stock * price
            num_stock = 0                
            table.add_row([date, round(num_stock, 2), round(wealth, 2), "Sell"])
            previous = "below"
            
        # If the 20 day moving average crosses above the 200 day moving average,
        # the stocks will be bought
        if (short_MA > long_MA and previous == "below"):
            crossover_dates.append(date)
            crossover_price.append(price)
            crossover_action.append("Buy")
            num_stock = wealth / price
            wealth = 0              
            table.add_row([df.loc[i, "Date"], round(num_stock, 2), round(wealth, 2), "Buy"])
            previous = "above"

# Empty Portfolio
if (wealth == 0):
    wealth = num_stock * df.loc[len(df)-1, "Close"]
    table.add_row(df.loc[i, "Date"], round(num_stock, 2), round(wealth, 2), "Sell")

# Print Final Information
profit = wealth - 1000

print (table)
print ("TOTAL")
print ("FROM", start_date, end_date)
print ("WEALTH =", round(wealth, 2))
print ("PROFIT =", round(profit, 2))

# Plot Information Onto Graph
plt.title("Chart of Price + Moving Averages")
plt.plot(df["Date"], df["Open"], label = "Stock Price")
plt.plot(long_MA_dates, long_MA_arr, label = "200 Day Moving Average")
plt.plot(short_MA_dates, short_MA_arr, label = "20 Day Moving Average")
plt.plot(crossover_dates, crossover_price, "ro")
for i in range (len (crossover_dates)):
    plt.annotate(crossover_action[i], 
                 (crossover_dates[i],crossover_price[i]), 
                 textcoords="offset points",
                 xytext=(0,20),
                 ha='center') 
plt.xlabel("Date")
plt.ylabel("Price ($)") 
plt.legend(["Price", "200 Day MA", "20 Day MA"], loc ="lower right") 
plt.plot()

plt.show()