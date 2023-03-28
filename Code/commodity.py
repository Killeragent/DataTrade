import pandas as pd 
import numpy as np
from os.path import exists 

#########################################
# Handle Function
#########################################
def write_log(text):
    '''
    Logging for 30 min positions
    '''
    today = datetime.date.today()
    date=today.strftime("%Y-%m-%d")
    file=open('../Log/'+date+'commodity.txt','a')
    text1=("{}: ".format(datetime.datetime.now()))
    file.write(text1+"\t"+text+"\n")
    file.close()


def get_intermediate_file(stock):
	filename = stock+'_fyers.csv'
	filepath='../Intermediates/'+filename
	df=pd.DataFrame(columns=['SYMBOL','ENTRY_TYPE','ENTRY_PRICE','SL','TP','STRATEGY'])
	if not exists(filepath):
		df.to_csv(filepath,index=False)
		print(" New intermediate file created for: {}".format(stock))
	return filepath


def write_order_to_file(filepath,symbol,entry_type,entry_price,sl,tp,strategy):
    '''
    Writes the order details to order_details.csv file
    '''
    df=pd.read_csv(filepath,header=0)
    new_row={'SYMBOL':symbol,'ENTRY_TYPE':entry_type,'ENTRY_PRICE':entry_price,'SL':sl,'TP':tp,'STRATEGY':strategy}
    df = df.append(new_row, ignore_index=True)
    df.to_csv(filepath,index=False)

def get_fut_symbol():
	'''
	Gets which symbols to trade for different commodities
	Takes input from the file ../Input/commodity_scrip.csv
	'''
	file="../Input/commodity_scrip.csv"
	comdict={}
	if exists(file):
		df=pd.read_csv(file,header=0)
		comlist=df['COMMODITY'].values
		futlist=df['FUT'].values
		for i in range(0,len(comlist)):
			comdict[comlist[i]]=futlist[i]

	else:
		write_log("ERROR:\t COMMODITY SCRIP file doesn't exist")

	return comdict













######################################
# Order management
######################################
def place_buy_order(symbol,quantity,fyers,types,limit_price,product):
	'''
	Input:
	symbol,quantity,types(market/limit),lp,product(MARGIN/INTRADAY)
	'''
	
	if types=='MARKET':
		trade_type=2
		limit_price=0
	if types=="LIMIT":
		trade_type=1

	# If intraday or margin is denoted by product type
	data = {"symbol":symbol,"qty":quantity,"type":trade_type,"side":1,"productType":product,"limitPrice":limit_price,"stopPrice":0,"validity":"DAY","disclosedQty":0,"offlineOrder":"False","stopLoss":0,"takeProfit":0}
	write_log("INFO:\tBUY order placed for {}. prodcut:{}".format(symbol,product))

	try:

		fyers.place_order(data)
		print(" Order placed")
		write_log("INFO:\tOrder placement successful at {}".format(datetime.datetime.now()))
	except Exception as e:
		write_log("ERROR:\tOrder placement failed at {}".format(datetime.datetime.now()))
		print(" ERROR in (entry)order punching...")
		logging.error("------{}-------".format(datetime.datetime.now()))
		logging.error(e)





def place_sell_order(symbol,quantity,fyers,types,limit_price,product):
	'''
	Input:
	symbol,quantity,types(market/limit),lp,product(MARGIN/INTRADAY)
	'''
	
	if types=='MARKET':
		trade_type=2
		limit_price=0
	if types=="LIMIT":
		trade_type=1

	# If intraday or margin is denoted by product type
	data = {"symbol":symbol,"qty":quantity,"type":trade_type,"side":-1,"productType":product,"limitPrice":limit_price,"stopPrice":0,"validity":"DAY","disclosedQty":0,"offlineOrder":"False","stopLoss":0,"takeProfit":0}
	write_log("INFO:\tSell order placed for {}. prodcut:{}".format(symbol,product))

	try:

		fyers.place_order(data)
		print(" Order placed")
		write_log("INFO:\tSell Order placement successful at {}".format(datetime.datetime.now()))
	except Exception as e:
		write_log("ERROR:\tOrder placement failed at {}".format(datetime.datetime.now()))
		print(" ERROR in (entry)order punching...")
		logging.error("------{}-------".format(datetime.datetime.now()))
		logging.error(e)






##################################################
# Strategy
##################################################

# 1. Gold Strategy: 
def get_sl_tp_gold_silver():
	pass



def check_gold_silver_strategy(symbol,df,ltp,pltp):
	'''
	Input: Symbol, dataframe of the datafile,ltp and previous_ltp
	'''
	write_log("INFO:\t(Checking GOLD-silver Startegy...")
	flag=False
	qt = 0
	sl = 0
	tp = 0
	entry_type="NA"
	max_risk = 600
	high=0
	low=0
	buffer=10
	# Calculate the 2 HR Candle 200MA 
	df['200MA']=df['C'].rolling(200).mean()

	if len(df)>1:

	last_dma=df['200MA'].values[-1]
	second_last_dma=df['200MA'].values[-2]

	last_candle_high=df['H'].values[-1]
	last_candle_low=df['L'].values[-1]
	last_candle_close=df['C'].values[-1]
	second_last_close=df['C'].values[-2]

	# Check BUY condition
	# Green candle closes above200MA and next candle price crosses the above of the last candle
	if second_last_close < second_last_dma and last_candle_close > last_dma:
		if pltp<last_candle_high and ltp>last_candle_high:
			print("INFO:\tGOld-silver BUY trigger occurred ")
			write_log("INFO:\tGold-silver BUY trigger occurred'''")
			high=last_candle_high
			low=last_candle_low
			qt,sl,tp=get_sl_tp_gold(symbol,'BUY',high,low,max_risk,ltp)
			flag=True
			entry_type='BUY'
			write_log('INFO:\tGold Strategy triggered')
	# Check sell condition
	if second_last_close > second_last_dma and last_candle_close < last_dma:
		if pltp>last_candle_high and ltp<last_candle_high:
			print("INFO:\tGOld-silver SELL trigger occurred ")
			write_log("INFO:\tGold-silver SELL trigger occurred'''")
			high=last_candle_high
			low=last_candle_low
			qt,sl,tp=get_sl_tp_gold(symbol,'SELL',high,low,max_risk,ltp)
			flag=True
			entry_type='SELL'
			write_log('INFO:\tGold-silver Strategy triggered')
	return flag,entry_type,sl,tp,qt,high,low











#########################################
# Main Function
########################################
def check_commodity_trades(symbol,ltp,pltp,fyers):
	pass

