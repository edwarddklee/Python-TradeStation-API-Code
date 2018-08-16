# -*- coding: utf-8 -*-
"""
streams barchart data and returns a csv file in a designated folder. 
"""

import requests, json
import subprocess
import sys
import urllib
import pandas as pd
import csv
import ast
import os 
import sys
from datetime import datetime
from dateutil import tz
import pytz

#path parameters
folder_path = r"C:\Users\Edward Lee\Desktop\Barcharts" #where the barchart csvs will go
symbols = pd.read_csv("C:\\Users\Edward Lee\Desktop\SymbolList.csv") #symbolList path 
token_path = r"C:\Users\Edward Lee\Desktop\refresh_token.txt"


with open(token_path) as f:
    token_list = f.readlines()
    response_token = token_list[0]

#refresh token, update as needed



symbolList = symbols['Ticker'].tolist()

import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")
    


print("This streams barchart data starting on Date")
#    
api_key = "your_api_key"
api_secret = "your_api_secret"
stream_url = "https://api.tradestation.com/v2/stream"
authorize_url = "https://api.tradestation.com/v2/authorize/"
redirect_uri = "https://www.tradestation.com/"
token_url = "https://api.tradestation.com/v2/security/authorize"
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


interval = "/1/"


unit = sys.argv[1]                         
t_startDate = sys.argv[2]                   
t_endDate= sys.argv[3]                   


monthDate = t_startDate 
monthDate = int(t_startDate[:2])
dayDate = int(t_startDate[3:5])
yearDate = int(t_startDate[6:10])
est = pytz.timezone('US/Eastern')
utc = pytz.utc
tempTime = datetime(yearDate, monthDate, dayDate, 13, 30, 0, tzinfo=utc)
eastTime = str(tempTime.astimezone(est))
hour = eastTime[11:13]

if hour == "09":
    startDate = t_startDate + "t13:29:00"
    endDate = t_endDate + "t20:01:00"
elif hour == "08":
    startDate = t_startDate + "t14:29:00"
    endDate = t_endDate + "t21:01:00"
else:
    print("Error please run program again. Exiting...")
    exit()


len_symbol = len(symbolList)
SessionTemplate = "Default"
exception_symbols = []
import datetime
a = 0
b = 0
def barchart_maker(a):
    global b
    while b < len_symbol:
        try:
            symbol = symbolList[b]
            symbol = symbol
            bar_data = stream_url + "/barchart/" + symbol + interval +  unit + "/" + startDate + "/" + endDate + "?SessionTemplate=" + SessionTemplate + "&access_token=" + response_access
            r = requests.get(bar_data, stream = True)
            if r.status_code != 200:
                print('Problem with the request. Exiting.')
                exit()
            r = r.text
            r = r[:-3]
            r = ''.join(r.split())
            r = r.replace("}","},")
            r = r[:-1]
            list_of_dicts = list(ast.literal_eval(r))
            df = pd.DataFrame.from_dict(list_of_dicts)
            df = df.rename(index = str, columns = {'TotalVolume' : 'Volume'})
            list_timestamp = df['TimeStamp'].tolist()
            print(list_timestamp)
            new_timestamp = []
            x = 0
            for value in list_timestamp:
                a = list_timestamp[x]
                a = int(a[7:17])
                new_timestamp.append(a)
                x += 1
            y = 0
            date_list = []
            time_list = []
            for element in new_timestamp:
                z = datetime.datetime.fromtimestamp(new_timestamp[y]).strftime('%m/%d/%Y %H:%M:%S')
                date_converted = z[0:10]
                time_converted = z[-8:]
                date_list.append(date_converted)
                time_list.append(time_converted)
                y += 1
            check = symbol[0]
            rest  = symbol[1:]
            if check == "@":
                name = "_" + rest + "_" + unit + ".csv"
            else:
                name = symbol + "_" + unit + ".csv" 

        
            column_values = pd.Series(date_list)
            df['Date'] = column_values.values
            column_values2 = pd.Series(time_list)
            df['Time'] = column_values2.values
    


            df = df.set_index('Date')
            df = df[['Time', 'Open', 'High', 'Low', 'Close', 'Volume']]
            print("Streaming & Saving Data for " + symbol)
            df.to_csv(os.path.join(folder_path, name))
            b += 1
            barchart_maker(a+1)
            return a
        except ValueError:
            print(bar_data)
            symbol = symbolList[b]
            exception_symbols.append(symbol)
            df2 = pd.DataFrame({'Error Symbols': exception_symbols})
            df2 = df2.set_index('Error Symbols')
            name2 = "Symbol_Errors.csv"
            df2.to_csv(os.path.join(folder_path, name2))
            print("Symbol: " + symbol + " could not be processed, moving onto next symbol." )
            b += 1
            barchart_maker(a+1)
barchart_maker(a)

