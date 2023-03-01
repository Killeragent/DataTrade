import pandas as pd 
import numpy as np
from fyers_api import fyersModel
from fyers_api import accessToken
import datetime
import time,sys
import entry as et 
import futfyers as ft 
import stockFY as sf
import niftyFY as nf
#######################################
# Initialization
######################################
client_id="H8O8SRR6U6-100"
# reading access token
f=open('../Input/token.txt','r')
for line in f:
	access_token=line 
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,log_path="../Log/")
print(" Intialized the app.... Access token read")

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

def log_write(text):
	'''
	Writes in the Log file
	'''
	today = datetime.date.today()
	date=today.strftime("%Y-%m-%d")
	file=open('../Log/'+date+'_datacollect.txt','a')
	text1=("{}: ".format(datetime.datetime.now()))
	file.write(text1+text+"\n")
	file.close()



def remove_pending_orders(fyers):
      '''
      Removes the LIMIT sell orders which are waiting state for more than 10 minutes
      '''
      orders=fyers.orderbook()
      orderbook = orders['orderBook']

      for order in orderbook:
            date = order["orderDateTime"]
            
            datetime_object = datetime.datetime.strptime(date, '%d-%b-%Y %H:%M:%S')
            current_time = datetime.datetime.now()
            time_difference = current_time - datetime_object
            td=int(time_difference.total_seconds())

            #Check if td> 12600 (fot TZ diff) + 60*10
            if td>(12600+3600) and order['status']==6:
                  oid = order["id"]
                  #Now cancel the order
                  data = {"id":oid}
                  fyers.cancel_order(data)
                  print(" All Pending Orders Cancelled")




def exit_all_pos_and_close_session():
	'''
	At 3:15 close all open orders and exit the session
	'''
	if (datetime.datetime.now().hour==18 and datetime.datetime.now().minute>=46):
		print(" Closing down th trading session for today")
		sys.exit()


##########################################################
# Main Loop (divided into two parts)
	# 1. One time data collection for candle based strategies
	# 2. Keep getting live data feed and historical data for MA strategies
##########################################################

T30_min_data_collected=False

prev_date_delta = 1 # last trading day was how many days ago
prev_date_delta = input("\nPrint last trading day delta. If yesterday type 1. If today is monday then type 3 (as last trading day was friday):")
prev_date_delta = int(prev_date_delta)


#Scrips which will be evaluated for first red candle short
#first_red_scrip_list=['SBIN','TCS','SUNPAHRMA','INDUSINDBK'] # This list holds all the stocks for which First red candle strategy will be evaluated (Input from Keyboard)
print(" Enter 5 stocks for which First red candle strategy will be evaluated...")
print(" Enter stock symbols separated by space. Eg TCS INFY SBIN. Press NA if you don't want to add any...")
first_red_scrip_list= list(map(str,input("\n Enter the stocks: ").split()))



#Along with passed stocks, check these picked stocks
red_scrip_list=['SBIN','INDUSINDBK','UPL']
for item in first_red_scrip_list:
	red_scrip_list.append(item)

for stock in first_red_scrip_list:
	red_scrip_list.append(stock)

first_red_scrip_list=red_scrip_list


if len(red_scrip_list)>1:
	df= pd.DataFrame({'STOCKS':red_scrip_list})
	df.to_csv('../Input/red_candle_short_stocks.csv',index=False)
	print("Red candle short list updated...")
	log_write(" Red candle short stock lists updated...")


# Write code to add MAX_ENTRY as 2 for all the stocks (no stock will have more than 2 positions in a day)
df=pd.read_csv('../Input/red_candle_short_stocks.csv',header=0)
lens=len(df)
max_entry_list=[]
for i in range(0,lens):
	max_entry_list.append(2)
df['MAX_ENTRY']=max_entry_list
df.to_csv('../Input/red_candle_short_stocks.csv',index=False)



# Scrips for second 30 Min BO
second30bolist=['MARUTI','SUNPHARMA','TCS']
df= pd.DataFrame({'STOCKS':second30bolist})
lens=len(df)
max_entry_list=[]
for i in range(0,lens):
	max_entry_list.append(1)
df['MAX_ENTRY']=max_entry_list
df.to_csv('../Input/second30bolist.csv',index=False)





######################################################
# Adding all stocks to quote list
######################################################
scrip_list=[]

# Add red candle stocks to the scrip list
for stock in first_red_scrip_list:
	scrip_list.append(stock)

# Add 30 min  stocks to the scrip list
for stock in second30bolist:
	if stock not in first_red_scrip_list:
		scrip_list.append(stock)


quote_stock_list=["NSE:NIFTY50-INDEX","NSE:NIFTYBANK-INDEX","NSE:RELIANCE-EQ"]
for stock in scrip_list:
	quote_stock_list.append("NSE:"+stock+"-EQ")



##################################################
# Declare and initalize previous LTP
##################################################

# Declare the dict to hold the previous ltp
prev_ltp={}
#initialize prev ltp
for scrip in quote_stock_list:
	prev_ltp[scrip]=None


'''
for symbol in quote_list:
	prev_ltp[symbol]=None
'''


#Timer inti to keep track of 5 min passed/15 min passed/1 hour passed
time_5min=time.time()
time_15min=time.time()
time_1hour=time.time()


##########################
# refetch the LTP
#########################
def refetch_ltp(symbol):
	'''
	refetch the ltp for a symbol
	'''
	data1 = {"symbols":"NSE:"+symbol+"-EQ"}
	new_quote=fyers.quotes(data1)
	for item in new_quote['d']:
		ltp = item['v']['lp']
	return ltp




#Loop
#for i in range (0,2):
while True:
	#print(" Debug: in the loop")
	# Flag to check if BN 12:45 30 min candle details is recorded (see strategy details at:)
	BN_30_MIN_FLAG=False
	# JPYINR second one hour data collecttion flag
	JPY_2ND_CANDLE_FLAG=False
	#GBPINR 3rd one hour candle data collection flags
	GBP_3rd_CANDLE_FLAG=False

	# Getting current time
	hour=datetime.datetime.now().hour
	minute=datetime.datetime.now().minute

	#Getting current date and previous date (for historical data collection purpose)
	curdate=datetime.datetime.today()
	curdate=curdate.strftime("%Y-%m-%d")
	prevdate=datetime.datetime.today()-datetime.timedelta(days=prev_date_delta)
	prevdate=prevdate.strftime("%Y-%m-%d")
	

	'''
	if not JPY_2ND_CANDLE_FLAG:
		if (hour==14 and minute>=30) or (hour>=15):
			data = {"symbol":"NSE:JPYINR22SEPFUT","resolution":"60","date_format":"1","range_from":curdate,"range_to":curdate,"cont_flag":"1"}
			dt=fyers.history(data)
			print("------------")
			print(dt)
			df=convert_data_to_df(dt)
			#print(df)
			df.to_csv('../Data/Intraday/1hour/JPYINR.csv',index=False)
			log_write(" DATACOLLECTION: JPY 2nd candle data collected...")
			JPY_2ND_CANDLE_FLAG=True
	if not GBP_3rd_CANDLE_FLAG:
		if (hour==15 and minute>=30) or (hour>=16):
			data = {"symbol":"NSE:GBPINR22SEPFUT","resolution":"60","date_format":"1","range_from":curdate,"range_to":curdate,"cont_flag":"1"}
			dt=fyers.history(data)
			df=convert_data_to_df(dt)
			#print(df)
			df.to_csv('../Data/Intraday/1hour/GBPINR.csv',index=False)
			log_write("DATACOLLECTION: GBP 3rd candle data connected...")
			GBP_3rd_CANDLE_FLAG=True
	if not BN_30_MIN_FLAG:
		if (hour==16 and minute>=15) or (hour>=17):
			data = {"symbol":"NSE:NIFTYBANK-INDEX","resolution":"60","date_format":"1","range_from":curdate,"range_to":curdate,"cont_flag":"1"}
			dt=fyers.history(data)
			df=convert_data_to_df(dt)
			#print(df)
			df.to_csv('../Data/Intraday/30min/JBNF.csv',index=False)
			log_write(" DATACOLLECTION: BNF 12:45 candle data collected (12:15-12:45)")
			BN_30_MIN_FLAG=True
	'''


	################################################
	# Keep Collecting Data for continious candles
	################################################

	###############################
	# Algorithm
	#	1. START loop
	#	2. START Data Collection module to manage data collection for different strategies
	#		3. Collect BN data for every 5 min until first red candle appears (see: startegy)
	#		4. Collect 5 min data for Gap up opening stocks (First 5) for 5 EMA
	#		5. Keep collecting 15 min Bank nifty data for 5 EMA strategy and Inside candle
	#	5. END Data collection module
	#	6. START Live quote module
	#		7. Check entry and redirect
	#		8. Update the previous ltp dict
	#	9. END live market quote
	#################################

	FIRST_RED_CANDLE_SEEN_FLAG=False

	if time.time()-time_5min>300:
		#Collect BNF dta firsts 5 min red candle
		if not FIRST_RED_CANDLE_SEEN_FLAG:
			
			
			try:
				data = {"symbol":"NSE:NIFTY50-INDEX","resolution":"5","date_format":"1","range_from":curdate,"range_to":curdate,"cont_flag":"1"}
				dt=fyers.history(data)
				df=convert_data_to_df(dt)
			
				df.to_csv('../Data/Intraday/5min/NIFTY50.csv',index=False)
				log_write(" DATACOLLECTION: NIFTY 5 min data collected...")

				data = {"symbol":"NSE:NIFTYBANK-INDEX","resolution":"5","date_format":"1","range_from":curdate,"range_to":curdate,"cont_flag":"1"}
				dt=fyers.history(data)
				df=convert_data_to_df(dt)
			
				df.to_csv('../Data/Intraday/5min/NIFTYBANK.csv',index=False)
				log_write(" DATACOLLECTION: BNF 5 min data collected...")
					
			except Excpetion as e:
				print(e)

		else:
			print("Green candle seen...NIFTYBANK")




		#Collect stocks data (5 min candles)
		for stocks in scrip_list:
			symbol="NSE:"+stocks+"-EQ"
			data = {"symbol":symbol,"resolution":"5","date_format":"1","range_from":curdate,"range_to":curdate,"cont_flag":"1"}
			dt=fyers.history(data)
			df=convert_data_to_df(dt)
			df.to_csv('../Data/Intraday/5min/'+stocks+'.csv',index=False)

			

		#reseting the timer
		time_5min=time.time()
			





	if time.time()-time_15min>900:
		
		#Collect BNF data firsts
		data = {"symbol":"NSE:NIFTYBANK-INDEX","resolution":"15","date_format":"1","range_from":prevdate,"range_to":curdate,"cont_flag":"1"}
		dt=fyers.history(data)
		df=convert_data_to_df(dt)
		df.to_csv('../Data/Intraday/15min/BNF.csv',index=False)
		log_write(" DATACOLLECTION: BNF 15 min candle data collected...")

		#resetting the timer
		time_15min=time.time()








	#####################################
	# Collect data for 30 min candle (Strategy 2)
	#####################################
	if ((datetime.datetime.now().hour==13 and datetime.datetime.now().minute==45) or (datetime.datetime.now().hour==14 and datetime.datetime.now().minute==00)):
		for stocks in second30bolist:
			symbol="NSE:"+stocks+"-EQ"
			data = {"symbol":symbol,"resolution":"30","date_format":"1","range_from":curdate,"range_to":curdate,"cont_flag":"1"}
			dt=fyers.history(data)
			df=convert_data_to_df(dt)
			df.to_csv('../Data/Intraday/30min/'+stocks+'.csv',index=False)


	###################################
	# Collect daily data for reliance (Startegy 3)
	##################################
	if ((datetime.datetime.now().hour==13 and datetime.datetime.now().minute==0) or (datetime.datetime.now().hour==13 and datetime.datetime.now().minute==1)):
		symbol="NSE:RELIANCE-EQ"
		data = {"symbol":symbol,"resolution":"1D","date_format":"1","range_from":prevdate,"range_to":curdate,"cont_flag":"1"}
		dt=fyers.history(data)
		df=convert_data_to_df(dt)
		df.to_csv('../Data/Daily/RELIANCE.csv',index=False)

		# Now collect the 15 min data to make sure that the first 15 min candle has not crossed PDH /PDL
		data = {"symbol":symbol,"resolution":"15","date_format":"1","range_from":curdate,"range_to":curdate,"cont_flag":"1"}
		dt=fyers.history(data)
		df=convert_data_to_df(dt)
		df.to_csv('../Data/Intraday/15min/RELIANCE.csv',index=False)
		print(" Relaince data collected...")
		log_write(' Relaince data collected')






	##############################################
	# Live market quote fetch
	# This part continiously fetches ltp for isntruments
	# Then check for entry conditions
	#############################################



	quote_string=""
	for stock in quote_stock_list:
		quote_string+=","+stock 
	quote_string=quote_string.lstrip(",")
	data = {"symbols":quote_string}
	try:
		quotes=fyers.quotes(data)
		print(" Quote collected")
	except Exception as e:
		print(e)
	print("---------------------------------------------------\n\n\n\n\n\n\n")
	
	for item in quotes['d']:
			
		stock = item['n']
		ltp = item['v']['lp']
		print("Stock:{} LTP:{}".format(stock,ltp))
		pltp=prev_ltp[stock]
		print("Stock:{} LTP:{} pltp{}".format(stock,ltp,pltp))
		#Check if there is a sudden spike or big difference between ltp and pltp


		if pltp is not None:
			if abs(ltp-pltp)>(pltp*0.001):
				time.sleep(5)
				#ltp=refetch_ltp(stock)
				print("CAUTION: LTP is refeteched")

		# Check for any entry/exit signal
		try:
			# FOR NORMAL STOCKS
			
			sf.check_entry_stocks(stock,ltp,pltp,fyers)
			
			#FOR NIFTY FUT
			if 'NIFTYBANK' in stock:
				nf.check_entry_bnf(stock,ltp,pltp,fyers)

				

		except Exception as e:
			print(e)
			log_write(" Error in check entry...")


		#Check the exit and modify startegy

		#Update the dictionary
		prev_ltp[stock]=ltp



	try:
		remove_pending_orders(fyers) #Removes the limit order which are pending more than 10 minutes
		exit_all_pos_and_close_session()

	except Exception as e:
		print(e)

	


	



	######################################
	# NIFTY  FUT (5 min red candle short)
	#####################################


	time.sleep(10)



##############
# TODO
##############
#1. Implement exit all position function at 3:15
#2. make sure NIFTYFY is working properly

		



















