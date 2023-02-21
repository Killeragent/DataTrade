import pandas as pd 
import numpy as np 
import datetime,time
import logging
import math
import calendar
from os.path import exists 

###################################
# Log File Create
##################################
def write_log(text):
    '''
    Logging for 30 min positions
    '''
    today = datetime.date.today()
    date=today.strftime("%Y-%m-%d")
    file=open('../Log/'+date+'stockFyers_entry.txt','a')
    text1=("{}: ".format(datetime.datetime.now()))
    file.write(text1+"\t"+text+"\n")
    file.close()
#####################################################
# Get intermediate file & stck lists(Red and EMA)
#####################################################
def get_intermediate_file(stock):
	filename = stock+'_fyers.csv'
	filepath='../Input/'+filename
	df=pd.DataFrame(columns=['SYMBOL','ENTRY_TYPE','ENTRY_PRICE','SL','TP','STRATEGY'])
	if not exists(filepath):
		df.to_csv(filepath,index=False)
		print(" New intermediate file created for: {}".format(stock))
	return filepath


def get_different_stock_list():
	'''
	returns red_candle_stock_list and ema_candle_stock_list
	'''
	df_red=pd.read_csv("../Input/red_candle_short_stocks.csv",header=0)
	
	red_candle_list=df_red['STOCKS'].values
	
	red_candle_list=["NSE:"+item+"-EQ" for item in red_candle_list]

	df_second=pd.read_csv("../Input/second30bolist.csv",header=0)
	
	second_candle_list=df_second['STOCKS'].values
	
	second_candle_list=["NSE:"+item+"-EQ" for item in second_candle_list]
	

	return red_candle_list,second_candle_list







#######################################
# Write orders to intermediate file
#######################################
def write_order_to_file(filepath,symbol,entry_type,entry_price,sl,tp,strategy):
    '''
    Writes the order details to order_details.csv file
    '''
    df=pd.read_csv(filepath,header=0)
    new_row={'SYMBOL':symbol,'ENTRY_TYPE':entry_type,'ENTRY_PRICE':entry_price,'SL':sl,'TP':tp,'STRATEGY':strategy}
    df = df.append(new_row, ignore_index=True)
    df.to_csv(filepath,index=False)

#######################################
# Order management (Place orders)
#######################################
def place_sell_order(symbol,quantity,fyers):
	'''
	Places the sell (entry)order

	'''
	quantity=1
	data = {"symbol":symbol,"qty":quantity,"type":2,"side":-1,"productType":"INTRADAY","limitPrice":0,"stopPrice":0,"validity":"DAY","disclosedQty":0,"offlineOrder":"False","stopLoss":0,"takeProfit":0}
	write_log("INFO:\t(Sell order) Placing the sell order for {}".format(symbol))

	try:

		fyers.place_order(data)
		print(" Order placed")
		write_log("INFO:\tOrder placement successful at {}".format(datetime.datetime.now()))
	except Exception as e:
		write_log("ERROR:\tOrder placement failed at {}".format(datetime.datetime.now()))
		print(" ERROR in (entry)order punching...")
		logging.error("------{}-------".format(datetime.datetime.now()))
		logging.error(e)





def place_sell_order_limit(symbol,quantity,fyers,limit_price):
	'''
	Sell order placing function for limit order
	'''
	quantity=1
	data = {"symbol":symbol,"qty":quantity,"type":1,"side":-1,"productType":"INTRADAY","limitPrice":limit_price,"stopPrice":0,"validity":"DAY","disclosedQty":0,"offlineOrder":"False","stopLoss":0,"takeProfit":0}
	write_log("INFO:\t(Sell order) Placing LIMIT sell order for {}".format(symbol))

	try:

		fyers.place_order(data)
		print(" Order placed")
		write_log("INFO:\tOrder placement successful at {}".format(datetime.datetime.now()))
	except Exception as e:
		write_log("ERROR:\tOrder placement failed at {}".format(datetime.datetime.now()))
		print(" ERROR in (entry)order punching...")
		logging.error("------{}-------".format(datetime.datetime.now()))
		logging.error(e)


    


def exit_buy_order(symbol,quantity,fyers):
	'''
	An order (BUY) to exit the already taken sell order
	'''
	data = {"symbol":symbol,"qty":quantity,"type":2,"side":1,"productType":"INTRADAY","limitPrice":0,"stopPrice":0,"validity":"DAY","disclosedQty":0,"offlineOrder":"False","stopLoss":0,"takeProfit":0}
	write_log("INFO:\t(Buy order) Placing the exit BUY order for {}".format(symbol))
	try:
		fyers.place_order(data)
		print(" Exit buy order placed susccessfully")
		write_log("INFO:\tBuy(exit) Order placement successful at {}".format(datetime.datetime.now()))
	except Exception as e:
		print(" ERROR in Buy (exit)order punching...")
		write_log("ERROR:\tError in Buy exit order punching")
		logging.error("------{}-------".format(datetime.datetime.now()))
		logging.error(e)





def place_buy_order_limit(symbol,quantity,fyers,limit_price):
	'''
	Sell order placing function for limit order
	'''
	quantity=1
	data = {"symbol":symbol,"qty":quantity,"type":1,"side":1,"productType":"INTRADAY","limitPrice":limit_price,"stopPrice":0,"validity":"DAY","disclosedQty":0,"offlineOrder":"False","stopLoss":0,"takeProfit":0}
	write_log("INFO:\t(BUY order) Placing LIMIT BUY order for {}".format(symbol))

	try:

		fyers.place_order(data)
		print(" Order placed")
		write_log("INFO:\tOrder placement successful at {}".format(datetime.datetime.now()))
	except Exception as e:
		write_log("ERROR:\tOrder placement failed at {}".format(datetime.datetime.now()))
		print(" ERROR in (entry)order punching...")
		logging.error("------{}-------".format(datetime.datetime.now()))
		logging.error(e)



def exit_sell_order(symbol,quantity,fyers):
	'''
	An order (BUY) to exit the already taken sell order
	'''
	data = {"symbol":symbol,"qty":quantity,"type":2,"side":-1,"productType":"INTRADAY","limitPrice":0,"stopPrice":0,"validity":"DAY","disclosedQty":0,"offlineOrder":"False","stopLoss":0,"takeProfit":0}
	write_log("INFO:\t(Buy order) Placing the exit BUY order for {}".format(symbol))
	try:
		fyers.place_order(data)
		print(" Exit sell order placed susccessfully")
		write_log("INFO:\tSell(exit) Order placement successful at {}".format(datetime.datetime.now()))
	except Exception as e:
		print(" ERROR in Sell(exit)order punching...")
		write_log("ERROR:\tError in Buy exit order punching")
		logging.error("------{}-------".format(datetime.datetime.now()))
		logging.error(e)





def modify_manage_order(symbol,filepath,ltp,fyers):
	'''
	For symbols read sl and tp from filepath
	Performs required operations (compare details with current ltp)
	'''
	write_log("\n")
	write_log("INFO:\t(M&M) In Modify and Manage order function")
	write_log("INFO:\t(M&M) Reading the input file for stock:{} filepath:{}".format(symbol,filepath))

	df=pd.read_csv(filepath,header=0)
	if len(df)>0:
		entry_price=df['ENTRY_PRICE'].values[-1]
		entry_type=df['ENTRY_TYPE'].values[-1]
		sl_price = df['SL'].values[-1]
		tp_price=df['TP'].values[-1]
		strategy = df['STRATEGY'].values[-1]
		
		pos=fyers.positions()
		netPos=pos['netPositions']
		#Now iterate through all positions

		for pos in netPos:
			write_log("INFO:\t(M&M) Iterating through all open positions...")
			scrip =pos['symbol']
			quantity=int(pos['sellQty']-pos['buyQty'])
			write_log("INFO:\t(M&M) In position checking... Scrip:{} quantity open:{} Symbol(the passed param in the func):{}".format(scrip,quantity,symbol))

			if scrip == symbol and quantity>0:
				if strategy=='RED':
					write_log("INFO:\t(M&M) Open position detected in RED candle strategy...")
					# If 1:1 is reached then modify the sl to just 0.2% down from the entry price
					if ltp>=sl_price:
						write_log("INFO:\t(M&M) SL Hit in {}".format(symbol))
						exit_buy_order(symbol,quantity,fyers)

					if ltp<=tp_price:
						write_log("INFO:\t(M&M) TP Hit in {}".format(symbol))
						exit_buy_order(symbol,quantity,fyers)

					if (entry_price-ltp)>2*(abs(sl_price-entry_price)):
						sl_price=entry_price+(0.002*entry_price) 
						sl_price  = round(sl_price,1)
						write_log("INFO:\t(M&M) SL price modified {}".format(symbol))
						write_order_to_file(filepath,symbol,'SELL',entry_price,sl_price,tp_price,'RED')				
				
				
				if strategy=='SECONDCANDLE':
					#Check if 2*diff reached then keep SL cost to cost
					if entry_type=='SELL':
						if ltp>=sl_price:
							exit_buy_order(symbol,quantity,fyers)
						if ltp<=tp_price:
							exit_buy_order(symbol,quantity,fyers)
						
					if entry_type=='BUY':
						if ltp<=sl_price:
							exit_sell_order(symbol,quantity,fyers)
						if ltp>=tp_price:
							exit_sell_order(symbol,quantity,fyers)

				


	else:
		print(" Nothing to modify. No record found in the CSV file{}.".format(symbol))
		write_log("INFO:\t(M&M) Nothing to modify. No record found in the CSV file")




def get_clear_balance(fyers):
	'''
	Returns how much balance is free (can be used for trading)
	'''
	balance = fyers.funds()
	limit = balance['fund_limit']
	clear_bal=0
	for item in limit:
		if 'Clear Balance' in item['title']:
			clear_bal=item['equityAmount']
	return clear_bal



###########################################
# Check entry criterias
###########################################
def num_of_open_position(fyers):
	'''
	Returns the number of open positon at any point of time
	'''
	count=0
	pos=fyers.positions() #API call to fyers
	netPos=pos['netPositions']
	for trades in netPos:
		stock = trades['symbol']
		side = trades['side']
		bq = trades['buyQty']
		sq = trades['sellQty']
		if 'EQ' in stock and abs(bq-sq)>0:
			count+=1
	print(" Num open positoons:{}".format(count))
	write_log("INFO:\tNumber of open positoon is: {}".format(count))
	return count


def position_taken(symbol,fyers):
	'''
	Checks if a particular position is already open
	1. Check if the SYMBOL is open in current positions
	2. Check from positions.csv
	3. Decide
	'''
	write_log('INFO:\t(Position taken func) Checking if already position is taken')
	flag = False
	pos=fyers.positions()
	netPos=pos['netPositions']
	for trades in netPos:
		stock = trades['symbol']
		unrelProfit =trades['unrealized_profit']
		relProfit = trades['realized_profit']
		side = trades['side']
		bq = trades['buyQty']
		sq = trades['sellQty']

		if side==1:
			side = 'BUY'
		if side==-1:
			side = 'SELL'

		scrip=symbol
		#write_log("DEBUG:\t(Position taken func) Scrip:{} Symbol:{} BQ:{} SQ:{} Side:{}".format(scrip,stock,bq,sq,side))

		if (abs(bq-sq)!=0) and scrip== stock and side == 'SELL':
			flag = True
			break
	

	return flag

	def position_taken_both_side(symbol,entry_type,fyers):

		'''
		Checks if a particular position is already open for the second 30 min BO candle
		1. Check if the SYMBOL is open in current positions
		2. Check from positions.csv
		3. Decide
		'''
		write_log('INFO:\t(Position taken func) Checking if already position is taken')
		flag = False
		pos=fyers.positions()
		netPos=pos['netPositions']
		for trades in netPos:
			stock = trades['symbol']
			unrelProfit =trades['unrealized_profit']
			relProfit = trades['realized_profit']
			side = trades['side']
			bq = trades['buyQty']
			sq = trades['sellQty']

			if side==1:
				side = 'BUY'
			if side==-1:
				side = 'SELL'

			scrip=symbol
			#write_log("DEBUG:\t(Position taken func) Scrip:{} Symbol:{} BQ:{} SQ:{} Side:{}".format(scrip,stock,bq,sq,side))

			if (abs(bq-sq)!=0) and scrip== stock and side == entry_type:
				flag = True
				break
		

	return flag









def get_sl_tp(symbol,position_type,high,low,max_risk,ltp):
	
	write_log("INFO:\t(get_sl_tp) Getting SL,TP and QTY for First red Candle short")
	sl=0
	tp=0
	quantity=0
	diff= abs(high-low)


	# IF the SL is very low, then adjust the quantity and sl accrodingly
	if diff<(ltp*0.003):
		diff=ltp*0.003
		diff=round(diff,1)
		write_log("DIFF_UPDATE:\t Diff is updated. Since it was very low")

	quantity = math.ceil(int(max_risk)/diff) # Quantity identified


	if position_type=='SELL':
		sl=low+diff
		target=low-(2.5*diff)
		sl=round(sl,1)
		tp = round(target,1)

	if position_type=='BUY':
		sl=high-diff
		target=high+(2.2*diff)
		sl=round(sl,1)
		tp=round(target,1)

	write_log("INFO:\t(Get sl tp) The calculated SL:{} TP:{} Quantity:{}".format(sl,tp,quantity))
	return quantity,sl,tp





def check_red_entry(symbol,df,ltp,pltp):
	'''
	Opens the file for symbol and checks strategy and claculates quantity,sl,tp
	'''
	write_log("INFO:\t(Check Red Entry func)Started...")
	flag=False
	qt = 0
	sl = 0
	tp = 0
	entry_type="NA"
	max_risk = 400
	high=0
	low=0
	if len(df)>0:
		opens=df['O'].values
		closes=df['C'].values
		highs=df['H'].values
		lows=df['L'].values
		high=0 
		low=0
		for i in range(0,len(df)):
			if closes[i]<opens[i]:
				if abs(highs[i]-lows[i])<(ltp*0.007):
					high=highs[i]
					low=lows[i]
					break
	write_log("INFO:\t(Check Red Entry)For {} the first red candle High: {} and Low: {}".format(symbol,high,low))
	if pltp>=low and pltp<=high:
			if ltp<low:
				print("INFO:\t(Check Red Entry) SEll trigger occurred ")
				write_log("INFO:\t(Check red Entry) SEll trigger occurred'''")
				qt,sl,tp=get_sl_tp(symbol,'SELL',high,low,max_risk,ltp)
				flag=True
				entry_type='SELL'
				write_log('INFO:\t(Check Red Entry func) STrategy triggered')
			else:
				print(" Checking.....{}".format(datetime.datetime.now()))
				write_log("INFO:\t(Check Red Entry func) strategy not triggered")

	return flag,entry_type,sl,tp,qt,high,low


def max_entry_reached(symbol):
	'''
	Determines if max entry is reached for a particular symbol
	'''
	pass

'''
def check_5ema_short(symbol,df,ltp,pltp):
	
	# At first check the time. Position should be taken till 10 am in the morning
	write_log("INFO:\t(Check eama entry func)Started...")
	flag=False
	qt = 0
	sl = 0
	tp = 0
	entry_type="NA"
	max_risk = 200
	if (datetime.datetime.now().hour<13 or (datetime.datetime.now().hour==13 and datetime.datetime.now().minute<=31)) or ((datetime.datetime.now().hour>=17)):
		write_log("DEBUG:\t(Check ema entry func) Inside the allowed time slots")
		if len(df)>5:
			df['EMA'] = df['C'].ewm(span=5).mean()
			high=df['H'].values[-1]
			low=df['L'].values[-1]
			ema = df['EMA'].values[-1]

			print(" Latest candle High:{} Low:{} Ema value:{}".format(high,low,ema))
			write_log("IMPORTANT:\t (Check EMA) Latest candle High:{} Low:{} Ema value:{} LTP:{} PLTP:{}\n".format(high,low,ema,ltp,pltp))
			if high> ema and low>ema:
				if pltp>low and pltp<=high:
					if ltp<low:
						print(" ***5 EMA sell signal generated in :{} ***".format(symbol))
						print(df.tail(3))
						df.to_csv("../intermediates/"+df+"_entry.csv",index=False)
						qt,sl,tp=get_sl_tp_5ema(symbol,'SELL',high,low,max_risk,ltp)
						qt=1
						flag=True
						entry_type='SELL'
		else:
			print(" Not enough data for 5 EMA calculation")
			write_log('ERROR:\t(Check ema entry func) Not enough data for 5 EMA calculation')


	return flag,entry_type,sl,tp,qt
'''






def second_30_breakout(symbol,df,ltp,pltp):
	write_log("INFO:\t(30 min BO)Started...")
	flag=False
	qt = 0
	sl = 0
	tp = 0
	entry_type="NA"
	max_risk = 360
	high=0
	low=0
	if ((datetime.datetime.now().hour==13 and datetime.datetime.now().minute>=45)) or ((datetime.datetime.now().hour>=14)):
		if len(df)>1:
			high=df['H'].values[1]
			low=df['L'].values[1]
			if abs(highs[i]-lows[i])<(ltp*0.007):
				if pltp>=low and pltp<=high:
					if ltp<low:
						print("INFO:\t(second 30 BO) SEll trigger occurred ")
						write_log("INFO:\t(Second 30 BO) SEll trigger occurred'''")
						qt,sl,tp=get_sl_tp(symbol,'SELL',high,low,max_risk,ltp)
						flag=True
						entry_type='SELL'
						write_log('INFO:\t(CSecond 30 BO) STrategy triggered')
				if pltp>=low and pltp<=high:
					if ltp>high:
						print("INFO:\t(second 30 BO) BUY trigger occurred ")
						write_log("INFO:\t(Second 30 BO) BUY trigger occurred'''")
						qt,sl,tp=get_sl_tp(symbol,'BUY',high,low,max_risk,ltp)
						flag=True
						entry_type='BUY'
						write_log('INFO:\t(Second 30 BO) STrategy triggered')

				else:
					print(" Checking.....{}".format(datetime.datetime.now()))
					write_log("INFO:\t(Second 30 BO) strategy not triggered")
			else:
				print(" Candle is too big")
				write_log("INFO:\t Second 30 min candle is too big")
	return flag,entry_type,sl,tp,qt,high,low




def check_reliance_entry(symbol,ltp,pltp):
	write_log("INFO:\t(30 min BO)Started...")
	flag=False
	qt = 0
	sl = 0
	tp = 0
	entry_type="NA"
	max_risk = 360
	high=0
	low=0
	daily_df=pd.read_csv("../Data/Daily/RELIANCE.csv",header=0)
	candle_df=pd.read_csv("../Data/Intraday/15min/RELIANCE.csv",header=0)
	if len(candle_df)>=1:
		first_high=candle_df['H'].values[0]
		first_low=candle_df['L'].values[0]

		pdh=daily_df['H'].values[0]
		pdl=daily_df['L'].values[0]

		# Check the BUY condition
		if pltp<=pdh and pltp>=pdl and ltp>pdh:
			if first_high<pdh:
				print("INFO:\tReliance BUY trigger occurred ")
				write_log("INFO:\tReliance BUY trigger occurred'''")
				high=ltp 
				low=ltp-15
				qt,sl,tp=get_sl_tp(symbol,'BUY',high,low,max_risk,ltp)
				flag=True
				entry_type='BUY'
				write_log('INFO:\tReliance Strategy triggered')

		#Check the sell condition
		if pltp<=pdh and pltp>=pdl and ltp<pdl:
			if first_low>pdl:
				print("INFO:\tReliace SEll trigger occurred ")
				write_log("INFO:\tReliance SEll trigger occurred'''")
				low=ltp 
				high=ltp+15
				qt,sl,tp=get_sl_tp(symbol,'SELL',high,low,max_risk,ltp)
				flag=True
				entry_type='SELL'
				write_log('INFO:\tReliance Strategy triggered')
	return flag,entry_type,sl,tp,qt,high,low






##########################################
# Final Loop
#########################################
def check_entry_stocks(symbol,ltp,pltp,fyers):
	'''
	This is the main loop
	'''
	#Initialize the deepLogger.log(only for errors and exceptions from catch)
	import logging
	logging.basicConfig(filename='../Log/deepLogger.log',)


	# At first fetch the data files for the stock
	write_log("\n\n\n")
	write_log("INFO:\t--------------Starting to check details for :{}-----------------".format(symbol))
	write_log("DEBUG:\tCurrent LTP:{} Previous LTP:{}".format(ltp,pltp))
	red_candle_list,second_candle_list= get_different_stock_list()
	print(second_candle_list)


	try:
		file_string=symbol.split("-")[0][4:]
		print("---Start of the Iteration---")
		write_log("DEBUG:\tThe file string for {} is {}".format(symbol,file_string))

		if symbol in red_candle_list:
			#1. fetch the data file for first red candle short (This data file is purged daily)
			df_red=pd.read_csv("../Data/Intraday/5min/"+file_string+".csv",header=0)
			write_log("DEBUG:\tData file for First red candle short (df_red) is fetched...")

		#1. fetch the data file for first red candle short (This data file is purged daily)
		if symbol in second_candle_list:
			print("YES HERE")
			df_second=pd.read_csv("../Data/Intraday/30min/"+file_string+".csv",header=0)
			write_log("DEBUG:\tData file for second 30 candle short (df_second) is fetched...")




		'''
		#2. fetch the file details for checking 5 EMA of stocks
		df_ema=pd.read_csv("../Data/Intraday/5min/"+file_string+"_ema.csv",header=0)
		write_log("DEBUG:\tData file for EMA short (df_ema) is fetched...")
		'''

		#3. Now fetch/create the intermediate file for the stock
		ORDER_DETAILS_FILE_PATH = get_intermediate_file(symbol)
		print("Input file path for {} is: {}".format(symbol,ORDER_DETAILS_FILE_PATH))
		write_log("DEBUG:\tInput file path for {} is: {}".format(symbol,ORDER_DETAILS_FILE_PATH))



		#Check How many positions are open... No more than 10 position should be open at one point of time
		# Get the list of stocks allowed to be entered using the different strategies
		open_position = num_of_open_position(fyers)
		


		if open_position<10:

			
			

			# Strategy 1: Second 30 minute Canlde Breakout Strategy
			write_log("INFO:\tChecking second 30 BO strategy")
			if symbol in second_candle_list:
				write_log("INFO:\t{} exists in the second candle lists".format(symbol))
				# Check for strategy
				write_log("INFO:\tChecking second 30 strategy")
				flag,entry_type,sl,tp,qty,high,low = second_30_breakout(symbol,df_second,ltp,pltp)
				write_log("INFO:\t5 second 30 condition checked for {}. Results are Flag:{} SL:{} TP:{} QTY:{}".format(symbol,flag,sl,tp,qty))
				

				if flag==True:
					print(" Signal generated")
					write_log("INFO:\t***Sell signal generated in {} ***".format(symbol))

					if not position_taken_both_side(symbol,entry_type,fyers):
						#Check and place order only if FUNDS are available
						avail_fund = get_clear_balance(fyers)
						margin_req = round(((ltp*qty)/5)+1,1) #1 is used as a buffer 
						write_log("INFO:\tAvailable margin to take trade: {}. Margin required to take trade: {}".format(avail_fund,margin_req))

						if avail_fund>=margin_req:
							write_log("---------------------------------------------------------")
							write_log("INFO:\tPreparing to take  Second 30 min candle Psotion")
							write_log("---------------------------------------------------------")
							print("INFO:\tPreparing to take  position")
					
							try:
								if entry_type=='SELL':
									limit_price = round((low-(low*0.0003)),1)
									write_log("INFO:\tLimit price: {}".format(limit_price))
									place_sell_order_limit(symbol,qty,fyers,limit_price)
									write_log("INFO:\tSell order function executed")
								if entry_type=='BUY':
									limit_price = round((high+(high*0.0003)),1)
									write_log("INFO:\tLimit price: {}".format(limit_price))
									place_buy_order_limit(symbol,qty,fyers,limit_price)
									write_log("INFO:\tBUY order function executed")

							except Exception as e:
								print(e)
								write_log("ERROR:\tError occurred while executing Place sell order function(From 5 EMA short). Check the deepLogger.log for more details.")

							write_log("INFO:\tWriting order details to the input file...")
							write_order_to_file(ORDER_DETAILS_FILE_PATH,symbol,entry_type,ltp,sl,tp,'SECONDCANDLE')
							write_log("INFO:\tWriting order function completed")
							write_log("----------------------------------------------")
						else:
							print(" Enough margin is not available. Check log for details")
							write_log("ERROR:\tMargin not available. Require margin: {} , Funds available: {}".format(margin_req,avail_fund))
			


			

			# Strategy 2; First Red Candle Breakout Strategy
			write_log("INFO:\tChecking if stock exists in the Red candle stock list")
			if symbol in red_candle_list:
				write_log("INFO:\t{} exists in the Red candle stock list".format(symbol))
				write_log("INFO:\tChecking FIRST RED Short entry condition")
				flag,entry_type,sl,tp,qty,high,low = check_red_entry(symbol,df_red,ltp,pltp)

				write_log("INFO:\tFirst Red short condition checked for {}. Results are Flag:{} SL:{} TP:{} QTY:{}".format(symbol,flag,sl,tp,qty))
				if flag==True:
					print(" Signal generated")
					write_log("INFO:\t***Sell signal generated in {} ***".format(symbol))

					if not position_taken(symbol,fyers):
						#Check and place order only if FUNDS are available
						avail_fund = get_clear_balance(fyers)-30000 # 30K is set aside for BNF trades
						margin_req = round(((ltp*qty)/5)+1,1)#1 is used as a buffer 
						write_log("INFO:\tAvailable margin to take trade: {}. Margin required to take trade: {}".format(avail_fund,margin_req))

						if avail_fund>=margin_req:
							write_log("---------------------------------------------")
							write_log("INFO:\tPreparing to take s sell position (Red short)")
							write_log("---------------------------------------------")
							print("INFO:\tPreparing to take s sell position")
					
							try:
								#place_sell_order(symbol,qty,fyers)
								limit_price = round((low-(low*0.0003)),1)
								write_log("INFO:\tLimit price: {}".format(limit_price))
								place_sell_order_limit(symbol,qty,fyers,limit_price)
								write_log("INFO:\tSell order function executed")
							except Exception as e:
								print(e)
								write_log("ERROR:\tError occurred while executing Place sell order function (From First Red short). Check the deepLogger.log for more details")

							write_log("INFO:\tWriting order details to the input file...")
							write_order_to_file(ORDER_DETAILS_FILE_PATH,symbol,entry_type,ltp,sl,tp,'RED')
							write_log("INFO:\tWriting order function completed")
							write_log("----------------------------------------------")
						else:
							print(" Enough margin is not available. Check log for details")
							write_log("ERROR:\tMargin not available. Require margin: {} , Funds available: {}".format(margin_req,avail_fund))

			



			# Strategy 3: Reliance PDH, PDL BO Strategy
			'''
			if 'RELIANCE' in symbol:
				write_log("INFO:\t{} exists in the Red candle stock list".format(symbol))
				write_log("INFO:\tChecking FIRST RED Short entry condition")
				flag,entry_type,sl,tp,qty,high,low = check_reliance_entry(symbol,ltp,pltp)
				if flag==True:
					print(" Signal generated")
					write_log("INFO:\t*** {} signal generated in RELIANCE ***".format(entry_type))

					if not position_taken_both_side(symbol,entry_type,fyers):
						#Check and place order only if FUNDS are available
						avail_fund = get_clear_balance(fyers)
						margin_req = round(((ltp*qty)/5)+1,1) #1 is used as a buffer 
						write_log("INFO:\tAvailable margin to take trade: {}. Margin required to take trade: {}".format(avail_fund,margin_req))

						if avail_fund>=margin_req:
							write_log("---------------------------------------------------------")
							write_log("INFO:\tPreparing to take position in Reliance")
							write_log("---------------------------------------------------------")
							print("INFO:\tPreparing to take  position")
					
							try:
								if entry_type=='SELL':
									limit_price = round((low-(low*0.0003)),1)
									write_log("INFO:\tLimit price: {}".format(limit_price))
									place_sell_order_limit(symbol,qty,fyers,limit_price)
									write_log("INFO:\tSell order function executed")
								if entry_type=='BUY':
									limit_price = round((high+(high*0.0003)),1)
									write_log("INFO:\tLimit price: {}".format(limit_price))
									place_buy_order_limit(symbol,qty,fyers,limit_price)
									write_log("INFO:\tBUY order function executed")

							except Exception as e:
								print(e)
								write_log("ERROR:\tError occurred while executing Place sell order function(RELIANCE). Check the deepLogger.log for more details.")

							write_log("INFO:\tWriting order details to the input file...")
							write_order_to_file(ORDER_DETAILS_FILE_PATH,symbol,entry_type,ltp,sl,tp,'RELIANCE')
							write_log("INFO:\tWriting order function completed")
							write_log("----------------------------------------------")
						else:
							print(" Enough margin is not available. Check log for details")
							write_log("ERROR:\tMargin not available. Require margin: {} , Funds available: {}".format(margin_req,avail_fund))
			'''


		if open_position>=10:
			print(" Already taken i 10 positions")
			write_log("INFO (EXPOSURE):\tAlready positioned in 10 or kore stocks. Can't taken another entry")


					


		#Now checking modify order details
		write_log("INFO:\tChecking exit conditions and sl update conditions...")
		print("INFO:\t Checking exit conditions and sl update conditions...")
		modify_manage_order(symbol,ORDER_DETAILS_FILE_PATH,ltp,fyers)
		write_log("INFO:\tChecking done successfully")
		print("INFO:\tChecking done successfully...")
		print("----------------------------End of Iteration--------------------------------")
		write_log("INFO:\t--------------End of details checking for :{}-----------------".format(symbol))


            	


	except Exception as e:
		print(e)
		print("Main error")
		write_log("ERROR:\t** Error in the stockFY.py. Check the deepLogger.log for more details.")
		logging.error("------{}-------".format(datetime.datetime.now()))
		logging.error("From the Main catch loop")
		logging.error(e)



########################
# For debugging quantities are set to 1.
# Change it accordingly
#########################









