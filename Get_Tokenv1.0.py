
import pandas as pd
from datetime import datetime, time
import requests

api_key = "api_key_here"
api_secret = "api_secret_here"
stream_url = "https://api.tradestation.com/v2/stream"
authorize_url = "https://api.tradestation.com/v2/authorize/"
v2_url = "https://api.tradestation.com/v2/"
redirect_uri = "https://www.tradestation.com/"
token_url = "https://api.tradestation.com/v2/security/authorize"
client_auth = requests.auth.HTTPBasicAuth(api_key, api_secret)
authorization_redirect_url = authorize_url + "?redirect_uri=" + redirect_uri + "&client_id=" + api_key + "&response_type=code"

print("Please go to url below and log in. Then copy authorization code from url: ")
print ("---  " + authorization_redirect_url + "  ---")
authorization_code = input("Put authorization code here:")
#
client_auth = requests.auth.HTTPBasicAuth(api_key, api_secret)
data = "grant_type=authorization_code&client_id="+ api_key + "&redirect_uri=" + redirect_uri + "&client_secret=" + api_secret + "&code="+ authorization_code + "&response_type=token"


headers = {"Content-Type": "application/x-www-form-urlencoded", "Content-Length": "630"}
#response call using requests library
response = requests.post(token_url, auth = client_auth, headers = headers, data = data)
if response.status_code != 200:
    print('Status:', response.status_code, 'Problem with the request. Exiting.')
    exit()
#access token: can expire
response_access = response.json()['access_token']
#refresh token: cannot expire
response_token = response.json()['refresh_token']
print("Here is your new refresh token, please update file as necessary and re-run program:\n"  )
print(response_token)
