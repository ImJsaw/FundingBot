from flask import Flask
from threading import Thread
from myLib import *

app = Flask('name')


marketLow = ''
FRR = ''
credit = ''
offer = ''

@app.route('/')
def alive():
  s = 'FRR :<br/> {} <br/> 市場低價:<br/> {} <br/> 借出中:<br/> {} <br/> 掛單中:<br/> {}'
  return s.format(FRR, marketLow, credit,offer)

@app.route('/123/')
def test():
  return '2345'

async def updateWeb():
  global marketLow, FRR, credit, offer
  marketLow = ''
  FRR = ''
  credit = ''
  offer = ''

  marketLow = await lendBookAvg()

  FRR = await getFRR()

  credits = await active_funds()
  for c in credits:
    credit = credit + c.toStr() + '<br/>'
  
  offers = await funding_offers()
  for f in offers:
    offer = offer + f.toStr() + '<br/>'

def adding():
  global counter
  counter = counter + 1

def run():
  app.run(host="0.0.0.0", port=8080)

def keep_alive():
  server = Thread(target=run)
  server.start()