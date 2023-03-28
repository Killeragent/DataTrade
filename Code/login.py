from fyers_api import fyersModel
from fyers_api import accessToken
import time
import webbrowser


from kiteconnect import KiteConnect
def login():
	'''
	Logs in the user and finally writes the access token in the file
	'''
	client_id="H8O8SRR6U6-100"
	secret_key="WA58YUMWLM"
	session=accessToken.SessionModel(client_id=client_id, secret_key=secret_key,redirect_uri="https://trade.fyers.in/api-login/redirect-uri/index.html",grant_type="authorization_code",response_type="code")
	print(" Open the Login screen in the browser...")
	print(session.generate_authcode() )
	value=input("Please enter your auth code:")
	value=str(value)
	auth_code=value
	session.set_token(auth_code)
	response = session.generate_token()
	print(response)
	access_token=response["access_token"]
	file=open('../Input/token.txt','w')
	file.write(str(access_token))
	file.close()
	print("\n accessToken written to the file ...")
	



	
	#############################
	# Zerodha client login
	############################
	api_key='cvnpw76nrxxgskao'
	api_secret='vqvr1bv3ya07zctndtgq7v71c8vxu33t'
	kite = KiteConnect(api_key=api_key)
	print(kite.login_url())
	req_token=input(" Enter the request token")
	data = kite.generate_session(req_token, api_secret=api_secret)
	access_token_zerodha = data['access_token']
	file=open('../Input/token_zerodha.txt','w')
	file.write(str(access_token_zerodha))
	file.close()
	print("\n accessToken written to the file for zerodha  ...")



login()