# Python AlgoTrader

On August 28, 2024 Nvidia released their third-quarter earnings. Their revenue had topped an all time high of $32.5 billion beating average analyst expectations of $31.9 billion by 1.88%. By September 6, 2024 the stock had fallen 20.36% wiping out over $600 billion of market value within a span of a week, the largest drop of an individual stock in U.S. stock market hsitory.

So why did a stock that outperformed its historical earnings and beat the lofty expectations from analysts fall to such levels? Some say it was because Nvidia's Blackwell chips were delayed. Others claim that it was caused by Nvidia's inability to beat earnings by margins witnessed in previous blowout quarters. I say it is none of the above. A stock grows because there are more people buying than selling (demand > supply) and falls because there are more people selling than buying (supply > demand). Hence, I suggest looking at the moving averages of a security to find its historical trends and analyze the patterns in which it is bought and sold.

Python AlgoTrader analyzes historical stock data and uses the intersection of the 20 day and 200 day moving averages to determine the entry and exit of a position. A table of dates and an accompanying chart are generated, presenting both the date and corresponding entry or exit prices.
