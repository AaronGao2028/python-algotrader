# Import Python Libraries
import csv
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import os
import shutil

# Check if trade_reports folder exists and remove old financial reports 
if os.path.exists('trade_reports'):
    shutil.rmtree('trade_reports')

# Create new trade_reports folder to store new financial reports
os.makedirs('trade_reports')    

# Loop through all csv files in historical data folder
directory = os.fsencode('historical_data')

for file in os.listdir(directory):
    file_name = os.fsdecode(file)
    
    # Ticker, Start Date, End Date, Interval retrieved from .csv file name
    ticker = file_name.split('_')[0]
    start_date = datetime.strptime(file_name.split('_')[1], '%Y-%m-%d').date()
    end_date = datetime.strptime(file_name.split('_')[2], '%Y-%m-%d').date()
    interval = file_name.split('_')[3].split('.')[0]
    
    # Arrays to store data
    data = []
    dates = []
    price = []
    volume = []
    
    # 50 minute moving average
    ma_50_minute_price_buildup = 0
    ma_50_minute_dates = []
    ma_50_minute_price = []
    
    # 200 minute moving average
    ma_200_minute_price_buildup = 0
    ma_200_minute_dates = []
    ma_200_minute_price = []
    
    # Intersection Points
    golden_cross_dates = []
    golden_cross_price = []
    death_cross_dates = []
    death_cross_price = []
    
    # Important Characteristics: Min Price, Max Price, Min Volume, Max Volume
    minPrice = 1e9
    minPriceDate = -1
    maxPrice = 0
    maxPriceDate = -1
    minVolume = 1e15
    minVolumeDate = -1
    maxVolume = 0
    maxVolumeDate = -1
    
    # Market value and percentage change of position throughout trading 
    initial_market_value = 1000000
    market_value = initial_market_value
    long_position = 0
    short_position = 0
    
    # Transaction History to store trades
    transaction_history = []

    # Read historical data stored within csv file and transfer into python arrays
    with open('historical_data/'+file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            # Skip first line in .csv file which is a header that describes each column
            if (row[1] == 'Open'): continue

            # Add data to the respective arrays
            dates.append(row[0])
            price.append(float(row[1]))
            volume.append(float(row[6]))

    for i in range(len(dates)):
        # Calculate maximum and minimum price
        if minPrice > price[i]:
            minPrice = price[i]
            minPriceDate = dates[i]
        if maxPrice < price[i]:
            maxPrice = price[i]
            maxPriceDate = dates[i]
            
        # Calculate maximum and minimum volume
        if minVolume > volume[i]:
            minVolume = volume[i]
            minVolumeDate = dates[i]
        if maxVolume < volume[i]:
            maxVolume = volume[i]
            maxVolumeDate = dates[i]
            
        # Calculate 50 minute moving average
        ma_50_minute_price_buildup += price[i]/50
        # Check that over 50 minutes have elapsed
        if i >= 50:
            ma_50_minute_price_buildup -= price[i-50]/50
            ma_50_minute_price.append(ma_50_minute_price_buildup) 
            ma_50_minute_dates.append(dates[i])
            
        # Calculate 200 minute moving average
        ma_200_minute_price_buildup += price[i]/200
        # Check that over 200 minutes have elapsed
        if i >= 200:
            ma_200_minute_price_buildup -= price[i-200]/200
            ma_200_minute_price.append(ma_200_minute_price_buildup)
            ma_200_minute_dates.append(dates[i])
            
            # Golden Cross: 50 minute MA moves above 200 minute MA
            if ma_50_minute_price[i-50-1] < ma_200_minute_price[i-200-1] and ma_50_minute_price_buildup > ma_200_minute_price_buildup:
                # Record transaction date and price for golden cross event
                golden_cross_dates.append(dates[i])
                golden_cross_price.append(ma_50_minute_price_buildup)
                
                # Buy Signal if there are no short positions
                if short_position == 0:
                    long_position = market_value/price[i]
                    transaction_history.append([dates[i], market_value, "Buy", price[i], long_position, 100*(market_value-initial_market_value)/initial_market_value])
                    market_value = 0
                # Cover Signal if there are short positions
                else:
                    market_value -= short_position*price[i]-market_value
                    short_position = 0
                    transaction_history.append([dates[i], market_value, "Cover", price[i], market_value/price[i], 100*(market_value-initial_market_value)/initial_market_value])
                        
            # Death Cross: 50 minute MA moves below 200 minute MA
            if ma_50_minute_price[i-50-1] > ma_200_minute_price[i-200-1] and ma_50_minute_price_buildup < ma_200_minute_price_buildup:
                # Record transaction date and price for death cross event
                death_cross_dates.append(dates[i])
                death_cross_price.append(ma_50_minute_price_buildup)
                
                # Sell Signal if there is a long positions
                if long_position == 0:
                    short_position = market_value/price[i]
                    transaction_history.append([dates[i], market_value, "Short", price[i], short_position, 100*(market_value-initial_market_value)/initial_market_value])
                # Short Signal if there are no long positions
                else:
                    market_value = long_position*price[i]
                    long_position = 0
                    transaction_history.append([dates[i], market_value, "Sell", price[i], market_value/price[i], 100*(market_value-initial_market_value)/initial_market_value])

    # Clear out all market positions. Convert any short or long positions to cash
    # Sell the long positions 
    if (long_position > 0):
        market_value = long_position*price[len(price)-1]
        long_position = 0
        transaction_history.append([dates[len(dates)-1], market_value, "Sell", price[len(price)-1], market_value/price[i], 100*(market_value-initial_market_value)/initial_market_value])
    # Cover the short positions
    if (short_position > 0):
        market_value -= short_position*price[len(price)-1]-market_value
        short_position = 0
        transaction_history.append([dates[len(dates)-1], market_value, "Cover", price[len(price)-1], market_value/price[i], 100*(market_value-initial_market_value)/initial_market_value])

    pdf = PdfPages('trade_reports/'+file_name.split('.')[0]+'.pdf')
    fig = plt.figure(dpi=100)

    # Plot Charts. Grey = Price. Orange = 50 minute MA. Blue = 200 minute MA. 
    plt.title(ticker + " " + str(start_date) + " " + str(end_date) + " " + interval)
    
    # ax1 subplot will be used to plot all price related graphs
    ax1 = plt.subplot()
    ax1.set_xlabel('Date', fontsize=8)
    ax1.set_ylabel('Price', fontsize=8)
    
    # Give graph some room at the bottom and top to prevent entire chart from being spread too wide
    ax1.set_ylim(0.995*minPrice, 1.005*maxPrice)
    ax1.yaxis.set_tick_params(labelsize=6)
    
    # ax2 subplot will be used to plot all volume related graphs
    ax2 = ax1.twinx()
    ax2.set_ylabel('Volume', fontsize=8)
    ax2.set_ylim(0, 5*maxVolume)
    ax2.yaxis.set_tick_params(labelsize=6)

    # Plot stock price
    ax1.plot(dates, price, color='silver', linewidth=0.75) 
    # Plot 50 minute moving average line
    ax1.plot(ma_50_minute_dates, ma_50_minute_price, color='darkorange', linewidth=0.75)
    # Plot 200 minute moving average line
    ax1.plot(ma_200_minute_dates, ma_200_minute_price, color='darkblue', linewidth=0.75)
    # Plot golden cross intersection points
    ax1.plot(golden_cross_dates, golden_cross_price, 'g^', markersize=3)
    # Plot death cross intersection points
    ax1.plot(death_cross_dates, death_cross_price, 'rv', markersize=3)

    ax2.bar(dates, volume, width=1.0, color='cornflowerblue')

    ax1.xaxis.set_visible(False)
    
    pdf.savefig(fig)
    
    # Check if there are intersections of the moving averages. If there are no intersections, do not
    # add a table in the second page detailing the intersection dates. 
    if (len(transaction_history) > 0):
        plt.clf()
        plt.title(ticker + " " + str(start_date) + " " + str(end_date) + " " + interval)
    
        df = pd.DataFrame(transaction_history)    
        df.columns = ["Date", 'Market Value', 'Action', 'Price', '# Shares', 'Percent Change']

        plt.axis('off')
        plt.table(cellText=df.values, colLabels=df.columns, loc='center')

        pdf.savefig(fig)
        
    pdf.close()