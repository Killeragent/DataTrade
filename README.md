# DataTrade
Algo trading for Indian markets

####################################
# Overall Algorithm (stockFY.py)
####################################

1. For each stock in the check entry function	
	1.1 Create a stockFyers.csv file in ../Input/ -> This file will hold all open positions
	1.2 check 5 EMA strategy
	1.3 If not position taken-> Take position
	1.4 Update the stockfyers.csv
	1.5 Check First red candle strategy -> If not position taken then take position
	1.6 Update the stock fyers.csv
	1.7 Check manage_and_exit(stock) function

	2. Check for 30 min candle strategy
	3. Repeat same operations
	4. Check manage and exit (stock) function
2. End (loop the call from each iteration of order.py)

##########################################
# Strategies Employed
##########################################



1. Basic First 5 min Red candle short strategy (1 before 10 AM  and one after 1 PM)
2. Bollinger Band Intraday trading strategy (1 before 10AM and 1  afetr 1 pm -> Open to NIFTY 100 stocks)
3. Bollinger band swing trading strategy (Fyers -> Start at MIS (for getting margin for other intraday trades) Convert at day end and pledge)
4. JPY second candle strategy (With less quantity)