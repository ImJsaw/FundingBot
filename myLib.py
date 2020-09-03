import time
from bfxapi import Client

# time now
now = int(round(time.time() * 1000))

bfx = Client(
  logLevel='DEBUG'
)
  
async def get_fund_history(user, symbol, size = 10):
  history = await user.rest.get_funding_offer_history(symbol, 0, now, size)
  print ("Funding offer history:")
  [ print (l) for l in history ]
   
async def log_wallets(user):
  wallets = await user.rest.get_wallets()
  print ("Wallets:")
  for w in wallets:
    print(w)
    
async def get_avaliable_money(user,symbol, type = 'funding'):
  wallets = await user.rest.get_wallets()
  for w in wallets:
    if w.type == type and w.currency == symbol:
      #raw balance include lending
      print(symbol,type, 'raw balance:',w.balance)
      balance = w.balance
      #lending
      lending = await active_funds(user,symbol)
      for l in lending:
        balance -= l.amount
      #offers
      offers = await funding_offers(user,symbol)
      for f in offers:
        balance -= f.amount
      print(symbol,type, 'real balance:',balance)
      return balance
    

#新增放貸掛單
async def create_funding(user,symbol, amount, rate, period):
  response = await user.rest.submit_funding_offer('f'+symbol, amount, rate, period)
  print ("Offer: ", response.notify_info)

#取消掛單
async def cancel_funding(user,id):
  response = await user.rest.submit_cancel_funding_offer(id)
  print ("cancel Offer: ", response.notify_info)

#掛單中
async def funding_offers(user,symbol = 'UST'):
  offers = await user.rest.get_funding_offers('f'+symbol)
  return offers

#借出中
async def active_funds(user,symbol = 'UST'):
  active_fund = []
  credits = await user.rest.get_funding_credits('f'+symbol)
  #print ("Funding credits:")
  for c in credits:
    if(c.status == 'ACTIVE'):
      active_fund.append(c)
      #print("id:",c.id,",rate:",c.rate,",amount:",c.amount,",day:",c.period)
  return active_fund 
  #[ print (c) for c in credits ]

async def log_active_funds(user, symbol = 'UST'):
  activeFund = await active_funds(user, symbol)
  for c in activeFund:
    print("id:",c.id,",rate:",c.rate,",amount:",c.amount,",day:",c.period)

####public data##############################

#input symbol to get FRR, ex: USD, UST
async def getFRR(symbol = 'UST'):
  ticker = await bfx.rest.get_public_ticker('f'+symbol)
  #print (symbol + " FRR:")
  #print (ticker)
  return ticker[0]

#掛單表
async def log_book( symbol = 'UST' ,precision = 'R0'):
  books = await bfx.rest.get_public_books('f'+symbol,precision)
  # rate 
  [ print (b) for b in books ]
 
async def lendBook(symbol = 'UST'):
  lend = []
  books = await bfx.rest.get_public_books('f'+symbol,'R0')
  for b in books:
    if b[3] > 0:
      lend.append(b)
  [ print (l) for l in lend ]
  
async def lendBookAvg(symbol = 'UST'):
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
async def trade(symbol ='UST',start = 0,end = now):
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

def calcRemainTime(credit):
  remainMts = credit.mts_opening + credit.period * 24 * 60 * 60 * 1000 - now
  remainSec = remainMts/1000.0
  remainMin = remainSec/60.0
  remainHour = remainMin/60.0
  return '{:4.2f}'.format(remainHour)
