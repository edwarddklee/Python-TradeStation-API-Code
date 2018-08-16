# Python-TradeStation-API-Code

# Get_Token.py

What this program does:

A refresh_token is used to request another access_token that grants access to the TradeStation API. Since there is a refresh_token file that remains active indefinitely, it is unlikely that another request needs to be made. But if needed Get_Token.py, if you follow all the steps will lead you to a new refresh_token which will update the refresh_token.txt file that you currently have. 

THIS PROGRAM MUST BE RUN IN TERMINAL!

Output of Program:

A new refresh_token in terminal which must copy and replace the text in refresh_token.txt


# Stream_BarchartData.py 

What this program does:

Through requesting data from TradeStation API and formatting it in a visible way, after some parameters are made (daily data, minute data) along with a symbol_list file, this returns barchart data which can be used for analysis. 

Important Variables:

folder_path: file path to where the barcharts will go after running the program

symbols: file path to the Symbol_List.csv of the symbols that will request its data from the API. 

token_path: file path to the refresh_token.txt file that is needed to authenticate access.



Errors that can Cause the Program to Crash:

If you receive a message: “Status: (any number besides 200)” on the terminal screen then the program most likely needs a new refresh_token which can be done there, or through Get_Token.py


Output of Program:

Symbol_Errors.csv: If there is error receiving data from any of the symbols, those symbols will 
be saved into csv file to show that these symbols were not data retrievable as name

SymbolName_DailyorMinute: example: MSFT_Daily will show up in a folder with data- Date
Time, Open, High, Low, Close, and Volume. 


# Order_Execution.py

What this Program Does:

The main program for the API, this automates buying and selling of equities and futures in live production by taking the account positions and filling orders through an Order File and reading the account numbers through the metadata also created. 

Important Variables:

token_path: file path to where the refresh_token.txt file is

order_path: file path to where the OrderFile.txt is 

meta_path: file path to where the Order_Metadata.csv file is

user_account: the account name of the Tradestation Account that you wish to send orders. 


Errors that can Cause the Program to Crash:

If you receive a message: “Status: (any number besides 200)” on the terminal screen then the program most likely needs a new refresh_token which can be done there, or through Get_Token.py
The order file must look like the following: Symbol Order_Amount i..e.:

	MSFT 10
  
	ADU18 -2
  
	FB 100
  
The metadata file must have an Account_Key column that is updated to match the Account Number.

If the time that the order is executed does not fall within the time range of the stock/future trading hours the entire order will not go through.
The order exceeds the max size given from the meta_data the entire order will no through.

If an order is not filled to the desired quantity an email will go out to #email right here. 
