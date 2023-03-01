import pandas as pd 
import numpy as np
from fyers_api import fyersModel
from fyers_api import accessToken
import datetime
import time,os
#import entry as et 
#import report as rt
#######################################
# Initialization
######################################
file = open('../../test.txt','a')
for i in range(0,100):
      file.write("Test\n")
      time.sleep(10)

'''

client_id="H8O8SRR6U6-100"
# reading access token
f=open('../Input/token.txt','r')
for line in f:
	access_token=line 
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,log_path="../Log/")
print(" Intialized the app.... Access token read")


data = {
      "symbol":"NSE:HINDALCO-EQ",
      "qty":1,
      "type":2,
      "side":-1,
      "productType":"BO",
      "limitPrice":0,
      "stopPrice":0,
      "validity":"DAY",
      "disclosedQty":0,
      "offlineOrder":"False",
      "stopLoss":3,
      "takeProfit":3
    }

#print(fyers.place_order(data))
#print(fyers.funds())
def convert_data_to_df(data):
      
      df=pd.DataFrame(columns=['TS','O','H','L','C','VOL'])
      candle_list=data['candles']
      for candle in candle_list:
            i=len(df)
            df.loc[i]=candle
      return df

curdate=datetime.datetime.today()
curdate=curdate.strftime("%Y-%m-%d")
prevdate=datetime.datetime.today()-datetime.timedelta(days=1)
prevdate=prevdate.strftime("%Y-%m-%d")

#print(df_red.head())



def remove_pending_orders(fyers):
      
      orders=fyers.orderbook()
      orderbook = orders['orderBook']

      for order in orderbook:
            date = order["orderDateTime"]
            
            datetime_object = datetime.datetime.strptime(date, '%d-%b-%Y %H:%M:%S')
            current_time = datetime.datetime.now()
            time_difference = current_time - datetime_object
            td=int(time_difference.total_seconds())

            #Check if td> 12600 (fot TZ diff) + 60*10
            if td>(12600+600) and order['status']==6:
                  oid = order["id"]
                  #Now cancel the order
                  data = {"id":oid}
                  fyers.cancel_order(data)
                  print(" All Pending Orders Cancelled")


def place_sell_order_limit(symbol,qty,fyers,limit_price):
      
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





print(fyers.positions())
'''

