from flask import Flask
'''  
app = Flask(__name__)
  
# Pass the required route to the decorator.
@app.route("/hello")
def hello():
    return "Hello, Welcome to GeeksForGeeks"
    
@app.route("/")
def index():
    return "Homepage of GeeksForGeeks"

'''
from flask import Flask,request

import calendar
app = Flask(__name__)
@app.route("/webhook",methods=['POST'])
def webhook():
    # Generating a timestamp.
    timeStamp = int(round(time.time() * 1000))
    webhook_data = json.loads(request.data)
    market = webhook_data['ticker']


@app.route("/prints")
def prints():
    print("Hello world")
  
if __name__ == "__main__":
    app.run(debug=True)