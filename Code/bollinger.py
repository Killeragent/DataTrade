import pandas as pd 
import numpy as np
from fyers_api import fyersModel
from fyers_api import accessToken
import datetime
import time
import entry as et 
import futfyers as ft 

import niftyFY as nf





client_id="H8O8SRR6U6-100"
# reading access token
f=open('../Input/token.txt','r')
for line in f:
	access_token=line 
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,log_path="../Log/")
print(" Intialized the app.... Access token read")
prev_date_delta=1




def convert_data_to_df(data):
	'''
	Takes the output data and converts it to dataframe
	'''
	df=pd.DataFrame(columns=['TS','O','H','L','C','VOL'])
	candle_list=data['candles']
	
	for candle in candle_list:
		i=len(df)
		df.loc[i]=candle
	return df


################################################
# Fetch and prepare for all NIFTY 500 stocks
###############################################
df=pd.read_csv('../Data/Intraday/15min/ind_nifty500list.csv',header=0)
stocks=df['Symbol'].values
quote_stock_list=['NSE:'+item+'-EQ' for item in stocks]

curdate=datetime.datetime.today()
curdate=curdate.strftime("%Y-%m-%d")
prevdate=datetime.datetime.today()-datetime.timedelta(days=prev_date_delta)
prevdate=prevdate.strftime("%Y-%m-%d")
'''
for stock in stocks:
	symbol='NSE:'+stock+'-EQ'
	data = {"symbol":symbol,"resolution":"1D","date_format":"1","range_from":"2023-01-01","range_to":curdate,"cont_flag":"1"}
	try:
		dt=fyers.history(data)
	
		df=convert_data_to_df(dt)
		
		df.to_csv('../Data/Intraday/15min/'+stock+'.csv',index=False)
	except Exception as e:
		print(e)

print(" Data collection completed")
'''

print(" Screening the stocks above or below the Bollinger band")
for stock in stocks:
	try:
		df=pd.read_csv("../Data/Intraday/15min/"+stock+".csv",header=0)
		df['SMA20'] = df['C'].rolling(window=20).mean()

		df['UB'] = df['SMA20'] + (1.5 * df['C'].rolling(window=20).std())
		df['LB'] = df['SMA20'] - (1.5 * df['C'].rolling(window=20).std())

		high=df['H'].values[-1]
		low=df['L'].values[-1]

		ub=df['UB'].values[-1]
		lb=df['LB'].values[-1]

		if (high>ub and low>ub) or (high<lb and low<lb):
			print("--  {} --".format(stock))
	except Exception as e:
		print(e)

####################################
# Scanner to find biggest mover in last 5 days and most consecutive red candles
####################################

most_consecutive={}
most_high={}
for stock in stocks:
	try:
		count=0
		df=pd.read_csv("../Data/Intraday/15min/"+stock+".csv",header=0)
		opens=df['O'].values
		closes=df['C'].values
		for i in range(len(opens)-1,0,-1):
			if closes[i]>opens[i] and closes[i]>closes[i-1]:
				count+=1
			else:
				break
		most_consecutive[stock]=count


		diff=closes[len(opens)-1]-closes[len(opens)-6]
		val=(diff/closes[len(opens)-6])*100
		most_high[stock]=val


	except Exception as e:
		print(e)

print(" The List of most conesutive days of stocks are...")
final_dict= sorted(most_consecutive.items(), key=lambda x:x[1],reverse=True)
print(final_dict[0:5])


print(" The List of most conesutive days of stocks are...")
final_dict1= sorted(most_high.items(), key=lambda x:x[1],reverse=True)
print(final_dict1[0:5])
















