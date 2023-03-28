import pandas as pd 
import numpy as np
from fyers_api import fyersModel
from fyers_api import accessToken
import datetime
import time,os
from fyers_api.Websocket import ws

#import entry as et 
#import report as rt
#######################################
# Initialization
######################################
file = open('../../test.txt','a')
client_id="H8O8SRR6U6-100"
# reading access token
f=open('../Input/token.txt','r')
for line in f:
      access_token=line 
fyers = fyersModel.FyersModel(client_id=client_id, token=access_token,log_path="../Log/")
print(" Intialized the app.... Access token read")



df=pd.read_csv('../Data/Intraday/15min/BNF.csv',header=0)
df['SMA(5)'] = df['C'].rolling(5).mean()
print(df.tail())


data = {"symbols":"MCX:CRUDEOILM23APRFUT"}
try:
      quotes=fyers.quotes(data)
      print(quotes)
except Exception as e:
      print(e)



'''
ssh -i att-AlgoTrading.pem ec2-user@1ip

'''