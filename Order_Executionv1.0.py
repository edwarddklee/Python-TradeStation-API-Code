

import requests, json
import subprocess
import sys
import urllib
import pandas as pd
import csv
import ast
import os 
from datetime import datetime, time
from dateutil import tz
import pytz
import re
import numpy as np
import smtplib


token_path = r"C:\Users\Edward Lee\Desktop\refresh_token.txt"
order_path = r"C:\Users\Edward Lee\Desktop\OrderFile.txt"
meta_path  = r"C:\Users\Edward Lee\Desktop\Order_Metadata.csv"

with open(token_path) as f:
    token_list = f.readlines()
    response_token = token_list[0]


import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")
    


#    
api_key = "your_api_key"
api_secret = "your_api_secret"
stream_url = "https://api.tradestation.com/v2/stream"
authorize_url = "https://api.tradestation.com/v2/authorize/"
v2_url = "https://api.tradestation.com/v2/"
redirect_uri = "https://www.tradestation.com/"
token_url = "https://api.tradestation.com/v2/security/authorize"
user_account = "your_user_account" 
client_auth = requests.auth.HTTPBasicAuth(api_key, api_secret)




#refresh token activator

refresh_data = "grant_type=refresh_token&client_id=" + api_key + "&redirect_uri=" + redirect_uri + "&client_secret=" + api_secret + "&refresh_token=" + response_token +"&response_type=token"
headers = {"Content-Type": "application/x-www-form-urlencoded", "Content-Length": "630"}
response = requests.post(token_url, auth = client_auth, headers = headers, data = refresh_data)
response_access = response.json()['access_token']
if response.status_code != 200:
    print('Status:', response.status_code, 'Problem with the request. Please authenticate again')
    authorization_redirect_url = authorize_url + "?redirect_uri=" + redirect_uri + "&client_id=" + api_key + "&response_type=code"

    print("Please go to url below and log in. Then copy authorization code from url: ")
    print ("---  " + authorization_redirect_url + "  ---")
    authorization_code = input("Put authorization code here:")
#
    client_auth = requests.auth.HTTPBasicAuth(api_key, api_secret)
    data = "grant_type=authorization_code&client_id="+ api_key + "&redirect_uri=" + redirect_uri + "&client_secret=" + api_secret + "&code="+ authorization_code + "&response_type=token"


    headers = {"Content-Type": "application/x-www-form-urlencoded", "Content-Length": "630"}
    response = requests.post(token_url, auth = client_auth, headers = headers, data = data)
    if response.status_code != 200:
        print('Status:', response.status_code, 'Problem with the request. Exiting.')
        exit()
    response_access = response.json()['access_token']
    response_token = response.json()['refresh_token']
    print("Here is your new refresh token, please update file as necessary and re-run program:\n"  )
    print(response_token)



df_accounts = pd.read_csv(meta_path)
metsym_list = df_accounts['Symbol'].tolist()
id_list = df_accounts["Account#"].tolist()
key_list = df_accounts["Account_Key"].tolist()
account_equity = str(id_list[0])
len_met = len(metsym_list)
rangemet_list = list(range(len_met))

equity_key = str(key_list[0])

#check time-constraints

d_hours_s = dict(zip(df_accounts['Symbol'], df_accounts['Session_Start(ET)']))
d_hours_e = dict(zip(df_accounts['Symbol'], df_accounts['Session_End(ET)']))

d = {}
with open(order_path) as f:
    for line in f:
       (key, val) = line.split()
       d[key] = val
symbol_list = list(d.keys())
number_list = list(d.values())


accountkey_data = v2_url + "users/" + user_account + "/accounts?access_token=" + response_access
r_account = requests.get(accountkey_data, stream = True)
account_string = str(r_account.json())
list_of_dicts = list(ast.literal_eval(account_string))
df = pd.DataFrame.from_dict(list_of_dicts)


future_key1 = str(key_list[1])
future_key2 = str(key_list[2])



#account positions 
orders_url = "https://api.tradestation.com/v2/orders?access_token=" + response_access
confirm_url = "https://api.tradestation.com/v2/orders/confirm?access_token=" + response_access
position_data = v2_url + "accounts/" + equity_key + "," + future_key1 + "," + future_key2 + "/positions?access_token=" + response_access
r_position = requests.get(position_data, stream = True)
position_string = str(r_position.json())
list_of_dicts2 = list(ast.literal_eval(position_string))
df2 = pd.DataFrame.from_dict(list_of_dicts2)
df2 = df2[['Symbol', 'AssetType', 'LongShort', 'Quantity']]
old = dict(zip(df2['Symbol'], df2['Quantity']))



#symbol information
d = {}
with open(order_path) as f:
    for line in f:
       (key, val) = line.split()
       d[key] = val
symbol_list = list(d.keys())
number_list = list(d.values())
exist_list  = df2["Symbol"].tolist()
symbol_len  = len(symbol_list)  
type_list   = []

for symbol in symbol_list:
    syminfo_url = "https://api.tradestation.com/v2/data/symbol/" + symbol + "?access_token=" + response_access
    r_symbol = requests.get(syminfo_url, stream = True)
    symbol_type = r_symbol.json()['Category']
    if symbol_type == "Stock":
        type_list.append("EQ")
    elif symbol_type == "Future":
        type_list.append("FU")
    else:
        print("Error, please check orderfile for correct stocks")


x = 0
date_list = []
for value in type_list:
    if value == "EQ":
        value = "*"
        date_list.append(value)
        x += 1
    else:
        value = symbol_list[x]
        date_list.append(value)
        x+= 1


e = 0
for value in date_list:
    now = datetime.now()
    now_time = now.time()
    asset = symbol_list[e]
    whole_time_s = d_hours_s[value]
    whole_time_e = d_hours_e[value]
    time_sb = int(whole_time_s[0:1])
    time_se = int(whole_time_s[-2:])
    time_eb = int(whole_time_e[0:2])
    time_ee = int(whole_time_e[-2:])
    if time(time_sb, time_se) <= now_time <= time(time_eb, time_ee):
        print(asset + " is within the time-trade hours, continuing...")
        e += 1
    else:
        print(asset + " is not within the time-trade hours, now terminating program...")
        raise SystemExit(0)
        
#size check
dict_exist = dict(zip(df2['Symbol'], df2['Quantity']))
dict_max = dict(zip(df_accounts['Symbol'], df_accounts['Max_Size']))
f = 0
final_list = []
for symbol in symbol_list:
    if symbol in dict_exist:
        asset_type = type_list[f]
        if asset_type == "EQ":
            equity = "*"
        else:
            equity = symbol
        exist_amount = dict_exist[symbol]
        order_amount = d[symbol]
        max_amount = dict_max[equity]
        total_amount = exist_amount + int(order_amount)
        final_list.append(total_amount)
        if total_amount >= max_amount:
            print(symbol + " exceeds the given max amount: " + str(max_amount) + " with order it would be at: " + str(total_amount) + "now exiting program...")
            raise SystemExit(0)
        else:
            print(symbol + " is within the given max amount, continuing...")
        f += 1
    else:
        asset_type = type_list[f]
        if asset_type == "EQ":
            equity = "*"
        else:
            equity = symbol
        exist_amount = 0
        order_amount = d[symbol]
        max_amount = dict_max[equity]
        total_amount = exist_amount + int(order_amount)
        final_list.append(total_amount)
        if total_amount >= max_amount:
            print(symbol + " exceeds the given max amount: " + str(max_amount) + ", with order it would be at: " + str(total_amount)+ ", now exiting program...") 
            raise SystemExit(0)
        else:
            print(symbol + " is within the given max amount, continuing...")
        f += 1
x = 0
y = 0
order_amount = []
order_type = []
resymbol_list= []
asset_list = []
def order_path(x):
    global y
    while y < symbol_len:
        qe_list = df2["Quantity"].tolist()
        exist_list = df2["Symbol"].tolist()
        dictionary = dict(zip(exist_list, qe_list))
        symbol = symbol_list[y] #0 = AMZN
        number = int(number_list[y])#0 = 15
        number2 = int(number_list[y])
        pos_number = abs(number2)
        asset = type_list[y]   #0 = EQ
        if symbol in exist_list:
            number3 = dictionary[symbol]
            number4 = dictionary[symbol]
            number_exist = abs(number3)
            if np.sign(number4) == np.sign(number):
                if asset == "EQ":
                    if number > 0:
                        command = "BUY"
                        order_type.append(command)
                        resymbol_list.append(symbol)
                        order_amount.append(pos_number)
                        asset_list.append("EQ")
                    else:
                        command = "SELLSHORT"
                        order_type.append(command)
                        resymbol_list.append(symbol)
                        order_amount.append(pos_number)
                        asset_list.append("EQ")
                else:
                    if number > 0:
                        command = "BUY"
                        order_type.append(command)
                        resymbol_list.append(symbol)
                        order_amount.append(pos_number)
                        asset_list.append("FU")
                    else:
                        command = "SELL"
                        order_type.append(command)
                        resymbol_list.append(symbol)
                        order_amount.append(pos_number)
                        asset_list.append("FU")
            else:
                if number_exist > pos_number:
                    if asset == "EQ":
                        if number > 0:
                            command = "BUYTOCOVER"
                            order_type.append(command)
                            resymbol_list.append(symbol)
                            order_amount.append(pos_number)
                            asset_list.append("EQ")
                        else:
                            command = "SELL"
                            order_type.append(command)
                            resymbol_list.append(symbol)
                            order_amount.append(pos_number)
                            asset_list.append("EQ")
                    else:
                        if number > 0:
                            command = "BUY"
                            order_type.append(command)
                            resymbol_list.append(symbol)
                            order_amount.append(pos_number)
                            asset_list.append("FU")
                        else:
                            command = "SELL"
                            order_type.append(command)
                            resymbol_list.append(symbol)
                            order_amount.append(pos_number)
                            asset_list.append("FU")
                else:
                    deducted_number = pos_number - number_exist
                    first_number = pos_number - deducted_number
                    if asset == "EQ":
                        if number > 0:
                            command = "BUYTOCOVER"
                            resymbol_list.append(symbol)
                            order_type.append(command)
                            order_amount.append(first_number)
                            asset_list.append("EQ")
                            command = "BUY"
                            resymbol_list.append(symbol)
                            order_type.append(command)
                            order_amount.append(deducted_number)
                            asset_list.append("EQ")
                        else:
                            command = "SELL"
                            resymbol_list.append(symbol)
                            order_amount.append(first_number)
                            order_type.append(command)
                            asset_list.append("EQ")
                            command = "SELLSHORT"
                            resymbol_list.append(symbol)
                            order_amount.append(deducted_number)
                            order_type.append(command)
                            asset_list.append("EQ")
                    else:
                        if number > 0:
                            command = "BUY"
                            resymbol_list.append(symbol)
                            order_type.append(command)
                            order_amount.append(first_number)
                            asset_list.append("FU")
                            command = "BUY"
                            resymbol_list.append(symbol)
                            order_type.append(command)
                            order_amount.append(deducted_number)
                            asset_list.append("FU")
                        else:
                            command = "SELL"
                            resymbol_list.append(symbol)
                            order_type.append(command)
                            order_amount.append(first_number)
                            asset_list.append("FU")
                            command = "SELL"
                            resymbol_list.append(symbol)
                            order_type.append(command)
                            order_amount.append(deducted_number)
                            asset_list.append("FU")
                            
                                      
        else:
            if asset == "EQ":
                if number > 0:
                    command = "BUY"
                    order_type.append(command)
                    resymbol_list.append(symbol)
                    order_amount.append(pos_number)
                    asset_list.append("EQ")
                else:
                    command = "SELLSHORT"
                    order_type.append(command)
                    resymbol_list.append(symbol)
                    order_amount.append(pos_number)
                    asset_list.append("EQ")
            else:
                if number > 0:
                    command = "BUY"
                    order_type.append(command)
                    resymbol_list.append(symbol)
                    order_amount.append(pos_number)
                    asset_list.append("FU")
                else:
                    command = "SELL"
                    order_type.append(command)
                    resymbol_list.append(symbol)
                    order_amount.append(pos_number)
                    asset_list.append("FU")
        y += 1
        order_path(x+1)
order_path(x)
resymbol_len = len(resymbol_list)
range_list = list(range(resymbol_len))

for number in range_list:
    asset_type = asset_list[number]
    quantity = order_amount[number]
    symbol = resymbol_list[number]
    x = 0
    y = 0

    if asset_type == "EQ":
        account_key = equity_key
        account_id = account_equity
    else:         
        for digits in rangemet_list:
            new_symbol = metsym_list[digits]
            if new_symbol == symbol:
                future_key = key_list[digits]
                account_future = id_list[digits]
            else:
                a = 0
        account_key = future_key
        account_id = account_future    


#    if asset_type == "EQ":
#        account_key = equity_key
#        account_id = account_equity
#    else:
#        account_key = future_key
#        account_id = account_future            
    trade_action = order_type[number]
    payload = {"AccountID": account_id,
           'AccountKey': account_key,
           'AssetType': asset_type,
           'Duration': "DAY",
           'OrderType': "Market",
           'Quantity': quantity, 
           'Route': "Intelligent",
           'Symbol': symbol,
           'TradeAction': trade_action}
    print(response)
    
#error handling
r_position = requests.get(position_data, stream = True)
position_string = str(r_position.json())
list_of_dicts2 = list(ast.literal_eval(position_string))
df3 = pd.DataFrame.from_dict(list_of_dicts2)
df3 = df3[['Symbol', 'AssetType', 'LongShort', 'Quantity']]


def sendemail(from_addr, to_addr_list,
              subject, message,
              login, password,
              smtpserver='smtp.gmail.com:587'):
    header  = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message
 
    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login,password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems
new = dict(zip(df3['Symbol'], df3['Quantity']))
q = 0
for symbol in symbol_list:
    try:
        final = new[symbol]
        theoretical = final_list[q]
    except KeyError:
        final = 0
        theoretical = final_list[q]
    if final != theoretical:
        sendemail(from_addr    = 'your email', 
                  to_addr_list = ['their email'], 
                  subject      = 'PROBLEM WITH FILLING ORDER', 
                  message      = "There was an error filling " + symbol +  ". The desired total amount was " + str(theoretical) + " but the actual filled total quantity was " + str(final) + ".",
                  login        = 'userlogin', 
                  password     = 'userpassword')


        
    