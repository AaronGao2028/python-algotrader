# Import Python Libraries
import csv
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from datetime import date, timedelta, datetime
import os

# Loop through all csv files in historical data folder
directory = os.fsencode('historical_data')
sp500_returns = []
for file in os.listdir(directory):
    if 'NVDA' in os.fsdecode(file):
        try: 
            # Variables
            filename = os.fsdecode(file)
            ticker = 'NVDA'
            #ticker = filename.split('_')[0]
            start_date = datetime.strptime(filename.split('_')[1], '%Y-%m-%d').date()
            end_date = datetime.strptime(filename.split('_')[2].split('.')[0], '%Y-%m-%d').date()
            file_name = ticker + '_' + str(start_date) + '_' + str(end_date) + '.csv'
            data = []
            dates = []
            price = []
            volume = []
            ma_50_minute_price_buildup = 0
            ma_50_minute_dates = []
            ma_50_minute_price = []
            ma_200_minute_price_buildup = 0
            ma_200_minute_dates = []
            ma_200_minute_price = []
            golden_cross_dates = []
            golden_cross_price = []
            death_cross_dates = []
            death_cross_price = []
            minPrice = 1e9
            minPriceDate = -1
            maxPrice = 0
            maxPriceDate = -1
            minVolume = 1e15
            minVolumeDate = -1
            maxVolume = 0
            maxVolumeDate = -1
            initial_market_value = 1000000
            market_value = initial_market_value
            long_position = 0
            short_position = 0
            transaction_history = []
            interval = '1m'

            # Read historical data stored within csv file and transfer into an array
            with open('historical_data/'+file_name) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    data.append(row)
            for i in range(1, len(data)):
                dates.append(data[i][0])
                price.append(float(data[i][1]))
                volume.append(float(data[i][6]))

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
                    
                # Calculate 50 minute and 200 minute moving averages
                ma_50_minute_price_buildup += price[i]/50
                if i >= 50:
                    ma_50_minute_price_buildup -= price[i-50]/50
                    ma_50_minute_price.append(ma_50_minute_price_buildup) 
                    ma_50_minute_dates.append(dates[i])
                    
                ma_200_minute_price_buildup += price[i]/200
                if i >= 200:
                    ma_200_minute_price_buildup -= price[i-200]/200
                    ma_200_minute_price.append(ma_200_minute_price_buildup)
                    ma_200_minute_dates.append(dates[i])
                    
                    # Golden Cross: 50 minute MA moves above 200 minute MA
                    if ma_50_minute_price[i-50-1] < ma_200_minute_price[i-200-1] and ma_50_minute_price_buildup > ma_200_minute_price_buildup:
                        golden_cross_dates.append(dates[i])
                        golden_cross_price.append(ma_50_minute_price_buildup)
                        # Buy/Cover Signal
                        if short_position == 0:
                            long_position = market_value/price[i]
                            transaction_history.append([dates[i], market_value, "Buy", price[i], long_position])
                            market_value = 0
                        else:
                            market_value -= short_position*price[i]-market_value
                            short_position = 0
                            transaction_history.append([dates[i], market_value, "Cover", price[i], market_value/price[i]])
                                
                    # Death Cross: 50 minute MA moves below 200 minute MA
                    if ma_50_minute_price[i-50-1] > ma_200_minute_price[i-200-1] and ma_50_minute_price_buildup < ma_200_minute_price_buildup:
                        death_cross_dates.append(dates[i])
                        death_cross_price.append(ma_50_minute_price_buildup)
                        # Sell/Short Signal
                        if long_position == 0:
                            short_position = market_value/price[i]
                            transaction_history.append([dates[i], market_value, "Short", price[i], short_position])
                        else:
                            market_value = long_position*price[i]
                            long_position = 0
                            transaction_history.append([dates[i], market_value, "Sell", price[i], market_value/price[i]])

            pdf = PdfPages('trade_reports/'+file_name.split('.')[0]+'.pdf')
            fig = plt.figure(dpi=100)

            # Setup ticks along the x and y axis to maximize chart readability and accuracy
            xticks = [str(start_date+timedelta(days=x))+' 09:30:00-04:00' for x in range(6)]

            # Plot Charts. Grey = Price. Orange = 50 minute MA. Blue = 200 minute MA. 
            plt.title(ticker+" "+str(start_date)+" "+str(end_date)+" "+interval)
            ax1 = plt.subplot()
            ax1.set_xlabel('Date', fontsize=8)
            ax1.set_ylabel('Price', fontsize=8)
            ax1.set_ylim(0.9*minPrice, 1.1*maxPrice)
            ax1.yaxis.set_tick_params(labelsize=6)
            ax1.xaxis.set_tick_params(labelsize=6)
            ax2 = ax1.twinx()
            ax2.set_ylabel('Volume', fontsize=8)
            ax2.set_ylim(0, 5*maxVolume)
            ax2.yaxis.set_tick_params(labelsize=6)

            # Format chart axis and line width
            ax1.plot(dates, price, color='silver', linewidth=0.75) 
            ax1.plot(ma_50_minute_dates, ma_50_minute_price, color='darkorange', linewidth=0.75)
            ax1.plot(ma_200_minute_dates, ma_200_minute_price, color='darkblue', linewidth=0.75)
            ax1.plot(golden_cross_dates, golden_cross_price, 'g^', markersize=3)
            ax1.plot(death_cross_dates, death_cross_price, 'rv', markersize=3)

            ax2.bar(dates, volume, width=1.0, color='cornflowerblue')

            ax1.set_xticks(xticks)
            ax1.set_xticklabels([x.split(' ')[0] for x in xticks])

            pdf.savefig(fig)

            plt.clf()

            plt.title(ticker+" "+str(start_date)+" "+str(end_date)+" "+interval)
            df = pd.DataFrame(transaction_history)
            df.columns = ["Date", 'Market Value', 'Action', 'Price', '# Shares']

            plt.axis('off')
            plt.table(cellText=df.values, colLabels=df.columns, loc='center')

            pdf.savefig(fig)
            pdf.close()
            
            sp500_returns.append([ticker, market_value])
        except:
            print(file + " had an unknown error.")