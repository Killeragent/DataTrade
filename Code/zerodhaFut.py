import pandas as pd 
import numpy as np
from kiteconnect import KiteConnect
import datetime
import time 
import logging
import math
import calendar
from os.path import exists 

####################################
# Declare the variables
####################################
API_KEY="cvnpw76nrxxgskao"
SECRET_KEY="vqvr1bv3ya07zctndtgq7v71c8vxu33t"
ACCESS_TOKEN="00cMVamVIfIcTD2w8Vc6SPcPGb93prWW"
ACCESS_TOKEN=input(" Please Enter the Access Token:")
kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)



###################################
# Log File Create
##################################
def write_log(text):
	'''
	Logging for 30 min positions
	'''
	today = datetime.date.today()
	date=today.strftime("%Y-%m-%d")
	file=open('../Log/'+date+'Zerodhafut_entry.txt','a')
	text1=("{}: ".format(datetime.datetime.now()))
	file.write(text1+"\t"+text+"\n")
	file.close()

###################################
# Option strike price calculation
###################################
def find_nearest_call_strike(ltp):
	'''
	Finds the nearest call price to hedge the short future
	'''
	ltp = math.ceil(ltp)
	ltp = int(ltp/100)
	new_ltp=100*(ltp+1)
	if (new_ltp-ltp)<50:
		new_ltp=new_ltp+100
	return new_ltp+100

def find_nearest_call_instrument(symbol,strike,month):
	'''
	Finds the option instrument
	symbol: 'NSE:NIFTY 50' or something like this
	strike: 18300 or something like this
	month:DEC or something like this
	returns NIFTYDEC18300CE
	'''
	if '50' in symbol:
		ins='NIFTY23'+month+str(strike)+'CE'
	if 'BANK' in symbol:
		ins='BANKNIFTY23'+month+str(strike)+'CE'
	return ins

def get_current_month():
	month=datetime.datetime.now().month
	month_string=calendar.month_name[month]
	mstr=month_string.upper()
	return mstr[0:3]

def find_FUT_instrument(symbol,month):
	if '50' in symbol:
		ins='NIFTY23'+month+'FUT'
	if 'BANK' in symbol:
		ins='BANKNIFTY23'+month+'FUT'
	return ins







###################################
# Check the data first red candle 
###################################
ltp_collect_list=['NSE:NIFTY 50']

FIRST_RED_CANDLE_SEEN_NIFTY = False
FIRST_RED_CANDLE_SEEN_BNF = False


prev_ltp={}
for symbol in ltp_collect_list:
	prev_ltp[symbol]=None

####################################
# Check entry criteria
####################################

ORDER_DETAILS_FILE_PATH="../Input/zerodhaFutSell.csv"
def create_order_details(ORDER_DETAILS_FILE_PATH):
	'''
	Creates the csv file if not already created
	'''
	if not exists(ORDER_DETAILS_FILE_PATH):
		#Create the csv file
		#df=pd.DataFrame(columns=['SYMBOL','FUT_ENTRY_TYPE','FUT_SYMBOL','OPT_SYMBOL','FUT_BUY_PRICE','FUT_SELL_PRICE','FUT_SL','FUT_TP','FUT_ORDER_ID','OPT_ORDER_ID','FUT_POS_STATUS','OPT_POS_STATUS'])
		df=pd.DataFrame(columns=['SYMBOL','FUT_INST','OPT_INST','ENTRY_TYPE','ENTRY_PRICE','SL','TP'])
		df.to_csv(ORDER_DETAILS_FILE_PATH,index=False)
		print(" Order details files created...")
		write_log("")


def get_sl_tp(symbol,position_type,high,low,ltp):
	sl=0
	tp=0
	quantity=0
	#Check ig the symbol is NIFTY or BANK NIFTY
	if 'BANK' in symbol:
		quantity=25
	else:
		quantity=50
	diff= abs(high-low)

	if diff>60:
		diff=50
	
	if diff<20:
		diff=20

	if position_type=='SELL':
		sl=low+diff
		target=low-120
		target=math.ceil(target)
	return quantity,sl,tp



def get_high_low(scrip):
	high=0
	low=0
	if 'BANK' in scrip:
		filename='BNF.csv'
	else:
		filename='NIFTY50.csv'
	try:
		df = pd.read_csv('../Data/Intraday/5min/'+filename,header= 0 )
		opens=df['O'].values
		closes=df['C'].values
		highs=df['H'].values
		lows=df['L'].values
		for i in range(0,len(df)):
			if closes[i]<opens[i]:
				if abs(highs[i]-lows[i])<70:
					FIRST_RED_CANDLE_SEEN_NIFTY=True
					high=highs[i]
					low=lows[i]
					break
		
	except Exception as e:
		print(" ERROR: No data file")
		print(e)
	return high,low




def check_entry(symbol,high,low,ltp,prev_ltp):
	'''
	ltp/prev_ltp: Current ltp and previous ltp
	'''
	flag=False
	entry_type=None 
	sl =0
	tp=0
	quantity=0
	high,low = get_high_low(symbol)
	print(ltp,prev_ltp,high,low)
	try:
		if prev_ltp>=low and prev_ltp<=high:
			if ltp<low:
				print(" ***Sell signal generated in {} ***".format(symbol))
				quantiy,sl,tp=get_sl_tp(symbol,'SELL',high,low,ltp)
				flag=True
				entry_type='SELL'

			else:
				print(" Checking.....{}".format(datetime.datetime.now()))
	except Exception as e:
		print(e)
	return flag,entry_type,sl,tp,quantity



def position_taken(symbol,entry_type,fut_symbol,opt_symbol):
	open_pos=kite.positions() # Fetches all open positions 
	net=open_pos['net']
	position_type='NA'
	# Check all open positions
	for pos in net:
		scrip=pos['tradingsymbol']
		quantity=pos['quantity']
		print("Scrip: {} Quantity Now open:{}".format(symbol,quantity))
		if int(quantity)<0 and entry_type=='SELL' :
			if 'NIFTY' in scrip and 'FUT' in scrip:
				return True
	return False



# Function to trail SL and exit if tp reached
def modify_manage_order(symbol,ltp):
	# Fetch open orders from the positions
	df=pd.read_csv(ORDER_DETAILS_FILE_PATH,header=0)
	if len(df)>0:
		entry_price=df['ENTRY_PRICE'].values[-1]
		sl_price = df['SL'].values[-1]
		tp_price=df['TP'].values[-1]
		open_pos=kite.positions() # Fetches all open positions 
		net=open_pos['net']
		fut_inst=df['FUT_INST'].values[-1]
		opt_inst=df['OPT_INST'].values[-1]

		for pos in net:
			scrip =pos['tradingsymbol']
			quantity=pos['quantity']
			if 'NIFTY' in scrip and 'FUT' in scrip and quantity<0:
				if entry_price-ltp>90:
					sl_price=entry_price+10 #Modifying SL almost close to sell price if NIFTY has fallen 
					write_order_to_file(scrip,fut_inst,opt_inst,'SELL',entry_price,sl_price,tp_price)
				if ltp>=sl_price:
					exit_fut_sell_order(fut_inst,opt_inst)
				if ltp<=tp_price:
					exit_fut_sell_order(fut_inst,opt_inst)




		

	# Modify (Exit or trail sl)

	#Update back the CSV file







def write_order_to_file(symbol,fut_inst,opt_inst,entry_type,entry_price,sl,tp):
	'''
	Writes the order details to order_details.csv file
	'''
	df=pd.read_csv(ORDER_DETAILS_FILE_PATH,header=0)
	new_row={'SYMBOL':symbol,'FUT_INST':fut_inst,'OPT_INST':opt_inst,'ENTRY_TYPE':entry_type,'ENTRY_PRICE':ltp,'SL':sl,'TP':tp}
	df = df.append(new_row, ignore_index=True)
	df.to_csv(ORDER_DETAILS_FILE_PATH,index=False)




#############################################
# Order Management
############################################

def make_fut_sell_order(fut_inst,opt_inst):
	'''
	Takes SELL position in FUT and corresponding BUY in a call for hedge
	'''
	#Buy the call order first in market
	order_id=None
	fut_order_id=None
	order_id = kite.place_order(tradingsymbol=opt_inst,exchange=kite.EXCHANGE_NFO,transaction_type=kite.TRANSACTION_TYPE_BUY,variety=kite.VARIETY_REGULAR,quantity=50,order_type=kite.ORDER_TYPE_MARKET,product=kite.PRODUCT_NRML,validity=kite.VALIDITY_DAY)
	if order_id is not None:
		time.sleep(2)
		fut_order_id = kite.place_order(tradingsymbol=fut_inst,exchange=kite.EXCHANGE_NFO,transaction_type=kite.TRANSACTION_TYPE_SELL,variety=kite.VARIETY_REGULAR,quantity=50,order_type=kite.ORDER_TYPE_MARKET,product=kite.PRODUCT_NRML,validity=kite.VALIDITY_DAY)

	if order_id is not None and fut_order_id is not None:
		print("...Order placement successful...")
	else:
		print("Issue happened while placing orders....")
		


def exit_fut_sell_order(fut_inst,opt_inst):
	'''
	Exits (buy) the fut and exists (Sell) the corresponding call option order.
	'''
	# At first make a check once more to make sure that the positoins are really open and then act accordingly
	order_id=None 
	fut_order_id=None 
	open_pos=kite.positions() # Fetches all open positions 
	net=open_pos['net']

	for pos in net:
		scrip=pos['tradingsymbol']
		quantity=pos['quantity']

		if 'NIFTY' in scrip and 'FUT' in scrip:
			if quantity<0:
				fut_order_id = kite.place_order(tradingsymbol=scrip,exchange=kite.EXCHANGE_NFO,transaction_type=kite.TRANSACTION_TYPE_BUY,variety=kite.VARIETY_REGULAR,quantity=50,order_type=kite.ORDER_TYPE_MARKET,product=kite.PRODUCT_NRML,validity=kite.VALIDITY_DAY)
				if fut_order_id is not None:
					time.sleep(2)
					order_id=kite.place_order(tradingsymbol=opt_inst,exchange=kite.EXCHANGE_NFO,transaction_type=kite.TRANSACTION_TYPE_SELL,variety=kite.VARIETY_REGULAR,quantity=50,order_type=kite.ORDER_TYPE_MARKET,product=kite.PRODUCT_NRML,validity=kite.VALIDITY_DAY)

	if fut_order_id is not None and order_id is not None:
		print('...Positions closed...')











###########################################
# Final Loop
###########################################
try:
	create_order_details(ORDER_DETAILS_FILE_PATH)
	write_log("INFO:\tOrder details file created")
except Exception as e:
	write_log("ERROR:\t Error in order details file creation")
	write_log(e)
#

while True:

	write_log("INF:\tInside the while loop...")
	try:
		quote=kite.ltp(ltp_collect_list)
		for scrips in ltp_collect_list:
			high,low = get_high_low(scrips)
			print(" For {} High:{} Low:{}".format(scrips,high,low))
			write_log(" For {} High:{} Low:{}".format(scrips,high,low))

			ltp=quote[scrips]['last_price']
			pltp = prev_ltp[scrips]
			prev_ltp[scrips]=ltp
			write_log(" Previous LTP read and updated with current ltp")
			# get the current month string
			currr_month = get_current_month()
			#Get the strike price
			strike = find_nearest_call_strike(ltp)
			print("ltp: {} The strike is {}".format(ltp,strike))
			#Get the option instrument
			opt_inst=find_nearest_call_instrument(scrips,strike,currr_month)
			fut_inst=find_FUT_instrument(scrips,currr_month)
			write_log("INFO:\tFut instrument and opt instrument fetched...")
			print(" Fut Instrument:{}".format(fut_inst))
			print(" The nearest call option instrument : {}".format(opt_inst))
			write_log("Fut and opt isntrument {} and {}".format(fut_inst,opt_inst))

			# Check the strategy and  sl tp
			
	
			write_log("INFO:\tChecking etry condition")
			flag,entry_type,sl,tp,qty = check_entry(scrips,high,low,ltp,pltp)
			write_log("INFO:\t NEtry checking done")

			if flag==True:
				print(" Signal generated")
				write_log("INFO:\t Sell signal generated...\n")
				if not position_taken(scrips,entry_type,fut_inst,opt_inst):
					print("\n...Take position...")
					write_log("---------------------------------------------")
					write_log("INFO:\tPreparing to take s sell position")
					write_log("---------------------------------------------")


					make_fut_sell_order(fut_inst,opt_inst)
					write_log("SUCCESS:\t Orders placed successfully...")

					write_order_to_file(symbol,fut_inst,opt_inst,entry_type,ltp,sl,tp)
					write_log("SUCCESS:\tTrade written to the csv file...")
					write_log("----------------------------------------------")


			#Now checking modify order details
			write_log("INFO:\t Chekcing exit conditions and sl update conditions...")
			modify_manage_order(scrips,ltp)
			write_log("SUCCESS:\tChecking done successfully")
		

	except Exception as e:
		write_log("ERROR:\t Error in the main loop. CHeck the print statement")
		time.sleep(20) # Waiting for 20 Seconds befpre the next call. In case it is a Kite issue...
		print(e)




	time.sleep(10)


