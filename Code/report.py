import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import csv
import datetime
import os
import os
import pandas as pd
import numpy as np
import math








###################################
# Algorithm
###################################
'''
DAILY MODULE
1. Create a folder for today and create a .csv file for recording trade details and create a .txt file for generating report from the csv
2. Iterate through all trades from fyers.trade()
	2.1 Record -> Symbol, quantity, buy_price, sell_price, pnl, estimated_brokerage,actual_pnl,strategy
	2.2 from this data, calculate the following
		2.2.1.Day ACTUAL PNL
		2.2.2.Day Overall PNL:
		2.2.3.Day Brokerage (estimated):
		2.2.4.Number of trades taken:
		2.2.5.Number of Buy trades: TBD
		2.2.6.Number of sell trades: TBD
		2.2.7.Number of winners:
		2.2.8.Number of losers:
		2.2.9.Max profit of the day:
		2.2.10.Max loss of the day:
		2.2.11.Starting equity:
		2.2.12.Ending equity:

MONTHLY MODULE
3. call the Monthly module that will perform the follwoing
	If not already created:
		create a master_trade.csv(holds all aggregated trades)
		master_param.csv(all parameters from 2.2 as columns)
		master_report.pdf(show all report from the master_param.csv in the format of 2.2)
	3.1 Go through all folders of the Daily
	3.2 Go through all trades.csv and add it to master_trade.csv
	3.3 Go through all daily summary and add it to master_report.csv
	3.4 Go through master_report.csv and present in a text format
	3.5 Add sharpe ratio , sortino ration and other plots to master_report.pdf file (It will consist all different types of plots)

'''
####################################
# End of Algorithm
###################################



#########################
# Functions
#########################
'''
1. Write daily reports 
2. Write Cumulative report
3. Calculate and input daily transaction details
'''


#############################
# Daily Reporting
#############################
'''
1. create required files
2. calculate daily statistics and update to the daily summary file
'''
def create_today_folder():
	today=datetime.datetime.now()
	path= "../Reports/"+today.strftime('%Y%m%d')
	if not os.path.exists(path):
		os.mkdir(path)
	return path




def prepare_daily_df(data,fyers):
	'''
	Prepares a daily df from the passed data
	'''
	funds=fyers.funds()
	limit=funds['fund_limit']
	for item in limit:
		if 'Limit at start of the day' in item['title']:
			equity=item['equityAmount']


	df = pd.DataFrame(data)
	df = df[["symbol", "productType", "realized_profit"]]
	pnl_vals = df['realized_profit'].values
	equity_curve=[]
	for item in pnl_vals:
		equity = equity+item
		equity_curve.append(equity)
	df['equity']=equity_curve

	return df



def create_today_trades(paths,fyers):
	try:
		pos = fyers.positions()
		netPos=pos['netPositions']
		df = prepare_daily_df(netPos,fyers)
		print(df.head())
		df = df.loc[df['productType'] != 'MARGIN']
		df.to_csv(paths+'/trades.csv',index=False)
	except Exception as e:
		print(e)


def calculate_largest_drawdown_days(rolling_profit):
	res=0
	curr_count=0
	for i in range(0,len(rolling_profit)-1):

		if rolling_profit[i]>rolling_profit[i+1]:
			curr_count+=1



			res=max(res,curr_count)
		else:
			
			curr_count=0
	return res


def calculate_largest_drawdown_equity(rolling_equity):
	res=0
	curr_amount=0
	for i in range(0,len(rolling_profit)-1):

		if rolling_profit[i]>rolling_profit[i+1]:
			drawdown=rolling_profit[i]-rolling_profit[i+1]
			curr_amount=curr_amount+drawdown

			res=max(res,curr_amount)
		else:
			
			curr_amount=0
			
	return res


def calculate_consecutive_winning_days(rolling_profit):
	res=0
	curr_count=0
	for i in range(0,len(rolling_profit)-1):

		if rolling_profit[i]<=rolling_profit[i+1]:
			curr_count+=1



			res=max(res,curr_count)
		else:
			
			curr_count=0
	return res

def calculate_largest_winning_equity(rolling_equity):
	res=0
	curr_amount=0
	for i in range(0,len(rolling_profit)-1):

		if rolling_profit[i]<=rolling_profit[i+1]:
			drawdown=rolling_profit[i]-rolling_profit[i+1]
			curr_amount=curr_amount+drawdown

			res=max(res,curr_amount)
		else:
			
			curr_amount=0
			
	return res






def create_overall_stats(STARTING_EQUITY):


	# Set the folder path containing the trades.csv files
	root = '../Reports/'
	all_folders=os.listdir(root)

	# Initialize a list to store all dataframes
	dataframes = []
	rolling_profit=[]
	rolling_equity=[STARTING_EQUITY]

	# Loop through each file in the folder
	for folder in all_folders:
		folder_path=os.path.join(root,folder)
		folder_path=folder_path+"/"
		print("Folder path: {}".format(folder_path))

		if 'Store' not in folder_path:

			try:
				for filename in os.listdir(folder_path):
					if filename.endswith('.csv'):
						file_path = os.path.join(folder_path, filename)

						# Read the trades.csv file into a dataframe
						df = pd.read_csv(file_path)

						#Calculate the daily PNL
						day_pnl=df['realized_profit'].sum()
						rolling_profit.append(day_pnl)


						# Add the dataframe to the list of dataframes
						dataframes.append(df)

			except Exception as e:
				print(e)

	# Calculate the rolling equity from rolling profit and starting capital
	for item in rolling_profit:
		eq=rolling_equity[-1]
		new_eq=eq+item
		rolling_equity.append(new_eq)


	
	print(dataframes)

	# Concatenate all dataframes into a single dataframe
	if len(dataframes)>0:
		aggregated_df = pd.concat(dataframes, axis=0)

		# Calculate various backtesting metrics
		total_realized_profit = aggregated_df['realized_profit'].sum()
		average_realized_profit = aggregated_df['realized_profit'].mean()
		maximum_profit = aggregated_df['realized_profit'].max()
		maximum_loss = aggregated_df['realized_profit'].min()

		# Calculate the total number of winning trades
		winning_trades = aggregated_df[aggregated_df['realized_profit'] > 0].shape[0]

		# Calculate the total number of losing trades
		losing_trades = aggregated_df[aggregated_df['realized_profit'] < 0].shape[0]

		# Calculate the standard deviation of realized profits
		standard_deviation = aggregated_df['realized_profit'].std()

		# Calculate the average daily return
		average_daily_return = average_realized_profit / len(aggregated_df)

		# Calculate the Sharpe ratio
		rf_rate = 0.02 # Assume a risk-free rate of 2%
		sharpe_ratio = (average_daily_return - rf_rate) / standard_deviation

		# Calculate the downside deviation for the Sortino ratio
		downside_deviation = np.sqrt(np.power(aggregated_df[aggregated_df['realized_profit'] < 0]['realized_profit'], 2).mean())

		# Calculate the Sortino ratio
		sortino_ratio = (average_daily_return - rf_rate) / downside_deviation
		positive_profits = aggregated_df[aggregated_df['realized_profit'] > 0]['realized_profit'].sum()
		negative_profits = aggregated_df[aggregated_df['realized_profit'] < 0]['realized_profit'].sum()
		profit_factor = positive_profits / abs(negative_profits)


		# Calculate largest drawdown of Negative days
		consecutive_losing_days=calculate_largest_drawdown_days(rolling_profit)
		largest_drawdown_equity=calculate_largest_drawdown_equity(rolling_equity)
		consecutive_winning_days=calculate_consecutive_winning_days(rolling_profit)
		consecutive_winning_profit=calculate_largest_winning_equity(rolling_equity)
		drawdown_percentage=(largest_drawdown_equity/STARTING_EQUITY)*100










		print('Total Realized Profit:', total_realized_profit)
		print('Average Realized Profit:', average_realized_profit)
		print('Maximum Profit:', maximum_profit)
		print('Maximum Loss:', maximum_loss)
		print('Number of Winning Trades:', winning_trades)
		print('Number of Losing Trades:', losing_trades)
		print('Sharpe Ratio:', sharpe_ratio)
		print('Sortino Ratio:', sortino_ratio)
		print('Profit Fcator:', profit_factor)


		######################################
		# Final Report Writing Block
		######################################
		with open('statistics.txt','w') as f:
			f.write("-----------------------------------------------------------\n")
			f.write("                     OVERALL STATISTICS                    \n")
			f.write("-----------------------------------------------------------\n")
			f.write("\n\n")
			f.write("1. TOTAL REALIZED PROFIT: {}\n".format(total_realized_profit))
			f.write("2. AVERAGE REALIZED PROFIT: {}\n".format(average_realized_profit))
			f.write("3. MAXIMUM PROFIT (in a trade): {}\n".format(maximum_profit))
			f.write("4. MAXIMUM LOSS (in a trade): {}\n".format(maximum_loss))
			f.write("5. TOTAL NUMBER OF WINNING TRADES: {}\n".format(winning_trades))
			f.write("6. TOTAL NUMBER OF LOSING TRADES: {}\n".format(losing_trades))
			f.write("7. AVERAGE DAILY RETURN: {}\n".format(average_daily_return))
			f.write("8. SHARPE RATIO: {}\n".format(sharpe_ratio))
			f.write("9. SORTINO RATIO: {}\n".format(sortino_ratio))
			f.write("10. CONSECUTIVE LOSING DAYS: {}\n".format(consecutive_losing_days))
			f.write("11. CONSECUTIVE WINNING DAYS:{}\n".format(consecutive_winning_days))
			f.write("12. MAX DRAWDOWN: {}\n".format(largest_drawdown_equity))
			f.write("13. Largest Drawup: {}\n".format(consecutive_winning_profit))
			f.write("14. DRAWDOWN PERCENTAGE: {}%\n".format(drawdown_percentage))
			f.write("---------------------END OF REPORT------------------------")
		f.close()
		print(" Report Generation Completed...")
	else:
		print(" No dataframe found")





##################################
# Main Loop
##################################
def generate_daily_report(fyers):
	'''
	Main function that is being called for report generation
	'''
	#Check if all files are created.
	STARTING_EQUITY=150000



	paths = create_today_folder()
	create_today_trades(paths,fyers)
	create_overall_stats(STARTING_EQUITY)




































