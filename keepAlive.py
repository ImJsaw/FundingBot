from flask import *
from threading import Thread
from myLib import *

app = Flask('name')


marketLow = ''
FRR = ''
credits = []
offers = []

@app.route('/')
def alive():
  index = request.args.get("index")
  print('index',index)
  if not index:
    return "add index parameter to get your data"
  index = int(index)
  if index >= len(credits):
    return "index out of bound!"
  s = 'FRR :<br/> {} <br/> 市場低價:<br/> {} <br/> 借出中:<br/> {} <br/> 掛單中:<br/> {}'
  return s.format(FRR, marketLow, credits[index],offers[index])

@app.route('/123/')
def test():
  return '2345'

async def updateWeb(users):
  global marketLow, FRR, credits, offers
  marketLow = ''
  FRR = ''
  credit = []
  offer = []

  marketLow = await lendBookAvg()

  FRR = await getFRR()

  for user in users:
    creditStr = ''
    credit = await active_funds(user)
    for c in credit:
      creditStr = creditStr + c.toStr() + '<br/>remain ' + str(calcRemainTime(c)) + 'hour<br/>'
    credits.append(creditStr)
  
    offerStr = ''
    offer = await funding_offers(user)
    for f in offer:
      offerStr = offerStr + f.toStr() + '<br/>'
    offers.append(offerStr)

def run():
  app.run(host="0.0.0.0", port=8080)

def keep_alive():
  server = Thread(target=run)
  server.start()