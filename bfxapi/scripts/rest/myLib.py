import os
import sys
import asyncio
import time
sys.path.append('../../../')
from bfxapi import Client

#set it in env
API_KEY=os.getenv("BFX_KEY")
API_SECRET=os.getenv("BFX_SECRET")
# time now
now = int(round(time.time() * 1000))


bfx = Client(
  API_KEY=API_KEY,
  API_SECRET=API_SECRET,
  logLevel='DEBUG'
)

#input 'f'+symbol to get FRR, ex: fUSD, fUSDT
async def getFRR(symbol):
  ticker = await bfx.rest.get_public_ticker(symbol)
  print (symbol[1:] + " FRR:")
  print (ticker)
  
async def get_fund_history(symbol, size = 10):
  history = await bfx.rest.get_funding_offer_history(symbol, 0, now, size)
  print ("Funding offer history:")
  [ print (l) for l in history ]
   
async def log_wallets():
  wallets = await bfx.rest.get_wallets()
  print ("Wallets:")
  [ print (w) for w in wallets ]

#放貸掛單
async def create_funding(symbol, amount, rate, period):
  response = await bfx.rest.submit_funding_offer(symbol, amount, rate, period)
  print ("Offer: ", response.notify_info)

#收回掛單
async def cancel_funding(id):
  response = await bfx.rest.submit_cancel_funding_offer(id)
  print ("cancel Offer: ", response.notify_info)

#掛單中
async def log_funding_offers(symbol = 'fUST'):
  offers = await bfx.rest.get_funding_offers(symbol)
  print ("Offers:")
  [ print (o) for o in offers]

#借出中
async def log_active_funds(symbol = 'fUST'):
  credits = await bfx.rest.get_funding_credits(symbol)
  print ("Funding credits:")
  for c in credits:
    if(c.status == 'ACTIVE'):
      print("id:",c.id,",rate:",c.rate,",amount:",c.amount,",day:",c.period)
    
  #[ print (c) for c in credits ]
  
async def main():
  #await log_wallets()
  #await get_fund_history('fUST')
  #await log_funding_offers('fUST')
  await log_active_funds('fUST')
  
t = asyncio.ensure_future(main())
asyncio.get_event_loop().run_until_complete(t)
