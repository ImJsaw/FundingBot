import asyncio
import random
from myLib import *
from keepAlive import *
from bfxapi import Client

#sleep time (s)
oneRoundTime = 600;

lastRoundOffer = -1
symbol = 'UST'
minRate = 0.00045
two_threshold = 0.00053
seven_threshold = 0.0007
adjustClock = 0
# adjust every period*10min 
adjustPeriod = 3
#decay every half an hour
#0.99^12 = 0.886
#0.99^6 = 0.94
#0.98^6 = 0.885
#0.98^12 = 0.78
decay_rate = 0.98
#estimate lend it 3 hour at most

async def adjust_offer(user, symbol):
  offers = await funding_offers(user, symbol)
  for offer in offers:
    old_id = offer.id
    old_rate = offer.rate
    old_amount = offer.amount
    await cancel_funding(user, old_id)
    await asyncio.sleep(2)
    #adjust rate 0.98^6 = 0.885
    rate = old_rate * decay_rate
    period = periodCalc(symbol, rate)
    if period < 2:
      print("rate too low. Not to create offer")
      return
    await create_funding(user, symbol, old_amount, rate, period)
  return
  
# get avg of market low & frr +max% ~ -min%
async def floatRate(symbol, min = 0, max = 1):
  frr = await getFRR(symbol)
  market = await lendBookAvg(symbol)
  print("frr : ",frr)
  print("cur market low : ", market)
  floating = random.randint(min*100,max*100)/100
  percent = 1 + floating/100
  return (frr+market) * percent / 2
  
 
async def lend(user, symbol, remain):
  mOffer = minOffer(symbol)
  if mOffer == -1:
    print("min offer of",symbol,'not defined')
    return
  if remain < mOffer:
    print("avaliable money not enough")
    return
  # offer amount  
  amount = mOffer
  if remain < mOffer*2:
    amount = remain
  #rate
  rate = await floatRate(symbol)
  period = periodCalc(symbol, rate)
  if period < 2:
    print("rate too low. Not to create offer")
    return
  await create_funding(user, symbol, amount, rate, period)
  await asyncio.sleep(1)
  return


def periodCalc(symbol, rate):
  if rate < minRate:
    return -1
  if rate < two_threshold:
    return 2
  if rate < seven_threshold:
    return 7
  return 30
  
#########################################

def readAccounts():
  file = open('./data.txt',mode='r')
  data = file.read().splitlines()
  for line in data:
    acc = line.split(';')
    user = Client(API_KEY=acc[0],API_SECRET=acc[1],logLevel='DEBUG')
    users.append(user)
  

    

async def main():
  while True:

    global adjustClock
    adjustClock = adjustClock+1
    adjustClock = adjustClock%adjustPeriod;
    #update market price
    global lastRoundOffer
    lastRoundOffer = await lendBookAvg(symbol)
    #await lendBook(symbol)

    for user in users:
      remain = await get_avaliable_money(user,symbol)
      print('avaliable',symbol,remain)
      if adjustClock == 0:
        print("##adjust offers...##")
        #just adjust every 6 turn (1 hour)
        #adjust offer
        await adjust_offer(user, symbol)
      #lend
      while remain > minOffer(symbol):
        await lend(usymbol, remain)
        remain = await get_avaliable_money(user, symbol)
    
   
    #update web
    await updateWeb(users)

    # sleep a while before do next round
    print("###########################")

    await asyncio.sleep(oneRoundTime)

users = []
readAccounts()
keep_alive()
t = asyncio.ensure_future(main())
asyncio.get_event_loop().run_forever()
