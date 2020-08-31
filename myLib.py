import time
from bfxapi import Client

#set API key & secret
API_KEY=''
API_SECRET=''
# time now
now = int(round(time.time() * 1000))


bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG'
)

#input symbol to get FRR, ex: USD, UST
async def getFRR(symbol):
  ticker = await bfx.rest.get_public_ticker('f'+symbol)
  #print (symbol + " FRR:")
  #print (ticker)
  return ticker[0]
  
async def get_fund_history(symbol, size = 10):
  history = await bfx.rest.get_funding_offer_history(symbol, 0, now, size)
  print ("Funding offer history:")
  [ print (l) for l in history ]
   
async def log_wallets():
  wallets = await bfx.rest.get_wallets()
  print ("Wallets:")
  for w in wallets:
    print(w)
    
async def get_avaliable_money(symbol, type = 'funding'):
  wallets = await bfx.rest.get_wallets()
  for w in wallets:
    if w.type == type and w.currency == symbol:
      #raw balance include lending
      #print(symbol,type, 'raw balance:',w.balance)
      balance = w.balance
      #lending
      lending = await active_funds(symbol)
      for l in lending:
        balance -= l.amount
      #offers
      offers = await funding_offers(symbol)
      for f in offers:
        balance -= f.amount
      #print(symbol,type, 'real balance:',balance)
      return balance
    

#新增放貸掛單
async def create_funding(symbol, amount, rate, period):
  response = await bfx.rest.submit_funding_offer('f'+symbol, amount, rate, period)
  print ("Offer: ", response.notify_info)

#取消掛單
async def cancel_funding(id):
  response = await bfx.rest.submit_cancel_funding_offer(id)
  print ("cancel Offer: ", response.notify_info)

#掛單中
async def funding_offers(symbol = 'UST'):
  offers = await bfx.rest.get_funding_offers('f'+symbol)
  return offers

#借出中
async def active_funds(symbol = 'UST'):
  active_fund = []
  credits = await bfx.rest.get_funding_credits('f'+symbol)
  print ("Funding credits:")
  for c in credits:
    if(c.status == 'ACTIVE'):
      active_fund.append(c)
      #print("id:",c.id,",rate:",c.rate,",amount:",c.amount,",day:",c.period)
  return active_fund 
  #[ print (c) for c in credits ]

async def log_active_funds(symbol = 'UST'):
  activeFund = await active_funds(symbol)
  for c in activeFund:
    print("id:",c.id,",rate:",c.rate,",amount:",c.amount,",day:",c.period)

####public data##############################

#掛單表
async def log_book(symbol ,precision = 'R0'):
  books = await bfx.rest.get_public_books('f'+symbol,precision)
  # rate 
  [ print (b) for b in books ]
 
async def lendBook(symbol):
  lend = []
  books = await bfx.rest.get_public_books('f'+symbol,'R0')
  for b in books:
    if b[3] > 0:
      lend.append(b)
  [ print (l) for l in lend ]
  
async def lendBookAvg(symbol):
  total = 0
  l = 0
  books = await bfx.rest.get_public_books('f'+symbol,'R0')
  for b in books:
    if b[3] > 0:
      total += b[2]
      l = l+1
  #print('avg :', total/l )
  return total/l
    
#成交紀錄
async def trade(symbol,start = 0,end = now):
  his = await bfx.rest.get_public_trades('f'+symbol,start,end)
  # id, time, amount, rate, period
  [ print (b) for b in his ]

##### Utils
def minOffer(symbol):
  if symbol == 'UST':
    return 50.1
  if symbol == 'USD':
    return 50
  return -1
