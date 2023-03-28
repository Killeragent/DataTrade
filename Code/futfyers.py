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


'''
FILE FOR TAKING BNF FUT POSITIONS IN FYERS
'''

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
   
    return new_ltp+150

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









####################################
# Check entry criteria
####################################


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
        tp=low-120
        tp=math.ceil(target)
    return quantity,sl,tp



def get_high_low():
    high=0
    low=0
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
    high,low = get_high_low()
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



def position_taken(fyers):

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

        if 'NIFTY' in stock and 'FUT' in stock:
            if (abs(bq-sq)!=0):
                flag = True
                break
    return flag




# Function to trail SL and exit if tp reached
def modify_manage_order(ORDER_DETAILS_FILE_PATH,symbol,ltp,fyers):
    # Fetch open orders from the positions
    df=pd.read_csv(ORDER_DETAILS_FILE_PATH,header=0)
    print(ORDER_DETAILS_FILE_PATH)
    if len(df)>0:
        entry_price=df['ENTRY_PRICE'].values[-1]
        sl_price = df['SL'].values[-1]
        tp_price=df['TP'].values[-1]
        fut_inst=df['FUT_INST'].values[-1]
        opt_inst=df['OPT_INST'].values[-1]

        pos=fyers.positions()
        netPos=pos['netPositions']

        for pos in netPos:
            scrip =pos['symbol']
            quantity=int(pos['sellQty']-pos['buyQty'])

            if 'NIFTY' in scrip and 'FUT' in scrip and quantity>0:
                if entry_price-ltp>90:
                    sl_price=entry_price+10 #Modifying SL almost close to sell price if NIFTY has fallen 
                    write_order_to_file(scrip,fut_inst,opt_inst,'SELL',entry_price,sl_price,tp_price)
                if ltp>=sl_price:
                    exit_fut_sell_order(fut_inst,opt_inst,fyers)
                if ltp<=tp_price:
                    exit_fut_sell_order(fut_inst,opt_inst,fyers)




        

    # Modify (Exit or trail sl)

    #Update back the CSV file







def write_order_to_file(ORDER_DETAILS_FILE_PATH,symbol,fut_inst,opt_inst,entry_type,entry_price,sl,tp):
    '''
    Writes the order details to order_details.csv file
    '''
    df=pd.read_csv(ORDER_DETAILS_FILE_PATH,header=0)
    new_row={'SYMBOL':symbol,'FUT_INST':fut_inst,'OPT_INST':opt_inst,'ENTRY_TYPE':entry_type,'ENTRY_PRICE':entry_price,'SL':sl,'TP':tp}
    df = df.append(new_row, ignore_index=True)
    df.to_csv(ORDER_DETAILS_FILE_PATH,index=False)




#############################################
# Order Management
############################################

def make_fut_sell_order(fut_inst,opt_inst,fyers):
    '''
    Takes SELL position in FUT and corresponding BUY in a call for hedge
    '''
    #Buy the call order first in market

    fut_data = {"symbol":"NSE:"+fut_inst,"qty":50,"type":2,"side":-1,"productType":"MARGIN","limitPrice":0,"stopPrice":0,"validity":"DAY","disclosedQty":0,"offlineOrder":"False","stopLoss":0,"takeProfit":0}
    opt_data={  "symbol":"NSE:"+opt_inst,"qty":50,"type":2,"side":1,"productType":"MARGIN","limitPrice":0,"stopPrice":0,"validity":"DAY","disclosedQty":0,"offlineOrder":"False","stopLoss":0,"takeProfit":0}
    #Place the option buy order first
    try:
        fyers.place_order(opt_data)
        try:
            fyers.place_order(fut_data)
            print(" Both orders are placed...")
        except Exception as e:
            print("ERROR in FUT Order punching")
            print(e)
    except Exception as e:
        print(" ERROR in order punching...")


def exit_fut_sell_order(fut_inst,opt_inst,fyers):
    '''
    Exits (buy) the fut and exists (Sell) the corresponding call option order.
    '''
    # At first make a check once more to make sure that the positoins are really open and then act accordingly
    # Fetch the positions
    pos=fyers.positions()
    netPos=pos['netPositions']
    for pos in netPos:
        scrip =pos['symbol']
        quantity=int(pos['sellQty']-pos['buyQty'])

        if 'NIFTY' in scrip and 'FUT' in scrip:
            fut_data = {"symbol":"NSE:"+fut_inst,"qty":quantity,"type":2,"side":1,"productType":"MARGIN","limitPrice":0,"stopPrice":0,"validity":"DAY","disclosedQty":0,"offlineOrder":"False","stopLoss":0,"takeProfit":0}
            opt_data = {"symbol":"NSE:"+opt_inst,"qty":quantity,"type":2,"side":-1,"productType":"MARGIN","limitPrice":0,"stopPrice":0,"validity":"DAY","disclosedQty":0,"offlineOrder":"False","stopLoss":0,"takeProfit":0}

            try:
                fyers.place_order(fut_data)
                print(" FUT ORDER EXITED..")
            except Exception as e:
                print(e)
            try:
                fyers.place_order(opt_data)
                print(" OPT ORDER EXITED...")
            except Exception as e:
                print(e)



###########################################
# Final Loop
###########################################
def check_entry_nifty(scrips,ltp,pltp,fyers):


    ORDER_DETAILS_FILE_PATH="../Input/fyersFutSell.csv"
    try:
        create_order_details(ORDER_DETAILS_FILE_PATH)
    except Exception as e:
        write_log("ERROR:\t Error in order details file creation")
        write_log(e)

    write_log("INFO:\tInside NIFTY CHECKING loop...")
    try:
     
        high,low = get_high_low() # Fetching High Low for NIFTY 50
        print(" For {} High:{} Low:{}".format(scrips,high,low))
        write_log(" For {} High:{} Low:{}".format(scrips,high,low))
        print(" NIFTY LTP:{} pltp:{}".format(ltp,pltp))
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
        

        write_log("INFO:\tChecking FIRST RED entry condition")
        flag,entry_type,sl,tp,qty = check_entry(scrips,high,low,ltp,pltp)
        write_log("INFO:\t Entry checking done")

        if flag==True:
            print(" Signal generated")
            write_log("INFO:\t Sell signal generated...\n")
            if not position_taken(fyers):
                print("\n...Take position...")
                write_log("---------------------------------------------")
                write_log("INFO:\tPreparing to take s sell position")
                write_log("---------------------------------------------")
                print("---------------------------------------------")
                print("INFO:\tPreparing to take s sell position")
                print("---------------------------------------------")

                make_fut_sell_order(fut_inst,opt_inst,fyers)
             
                write_log("SUCCESS:\t Orders placed successfully...")

                write_order_to_file(ORDER_DETAILS_FILE_PATH,scrips,fut_inst,opt_inst,entry_type,ltp,sl,tp)
                write_log("SUCCESS:\tTrade written to the csv file...")
                write_log("----------------------------------------------")
                print("-------------------------------------------------")

        # Now checking the second strategy (5 ema strategy)
        #write_log("INFO:\tChecking 5 EMA entry condition")
        #flag,entry_type,sl,tp,qty = check_5ema_entry(scrips,ltp,pltp)
        #write_log("INFO:\t Entry checking done")



        #Now checking modify order details
        write_log("INFO:\t Chekcing exit conditions and sl update conditions...")
        print("INFO:\t Chekcing exit conditions and sl update conditions...")
        modify_manage_order(ORDER_DETAILS_FILE_PATH,scrips,ltp,fyers)
        write_log("SUCCESS:\tChecking done successfully")
        print("SUCCESS:\tChecking done successfully...")
        

    except Exception as e:
        write_log("ERROR:\t Error in the main loop. CHeck the print statement")
        # Waiting for 20 Seconds befpre the next call. In case it is a Kite issue...
        print(e)




  


