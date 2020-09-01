import asyncio
import random
from myLib import *
from keepAlive import *

#sleep time (s)
oneRoundTime = 600;

lastRoundOffer = -1
symbol = 'UST'
minRate = 0.00045
two_threshold = 0.00055
seven_threshold = 0.0007
adjustClock = 0
# adjust every period*10min 
adjustPeriod = 6
#decay every hour
#0.99^12 = 0.886
#0.99^6 = 0.94
decay_rate = 0.99

async def adjust_offer(symbol):
  offers = await funding_offers(symbol)
  for offer in offers:
    old_id = offer.id
    old_rate = offer.rate
    old_amount = offer.amount
    #adjust rate 0.99^12 = 0.88
    rate = old_rate * 0.99
    period = periodCalc(symbol, rate)
    await cancel_funding(old_id)
    await asyncio.sleep(2)
    await create_funding(symbol, old_amount, rate, period)
  return
  
# get avg of market low & frr +max% ~ -min%
async def floatRate(symbol, min, max):
  frr = await getFRR(symbol)
  market = await lendBookAvg(symbol)
  print("frr : ",frr)
  print("cur market low : ", market)
  floating = random.randint(min*100,max*100)/100
  percent = 1 + floating/100
  return (frr+market) * percent / 2
  
 
async def lend(symbol, remain):
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
  rate = await floatRate(symbol, -0.5,1.5)
  period = periodCalc(symbol, rate)
  if period < 2:
    print("rate too low. Not to create offer")
    return
  await create_funding(symbol, amount, rate, period)
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
async def main():
  while True:
    ##do something
    remain = await get_avaliable_money(symbol)
    print('avaliable',symbol,remain)
    global adjustClock
    adjustClock = adjustClock+1
    adjustClock = adjustClock%adjustPeriod;
    if adjustClock == 0:
      print("##adjust offers...##")
      #just adjust every 6 turn (1 hour)
      #adjust offer
      await adjust_offer(symbol)
    #lend
    while remain > minOffer(symbol):
      await lend(symbol, remain)
      remain = await get_avaliable_money(symbol)
    
    #update market price
    global lastRoundOffer
    lastRoundOffer = await lendBookAvg(symbol)
    #await lendBook(symbol)
    
    #update web
    await updateWeb()

    # sleep a while before do next round
    print("###########################")

    await asyncio.sleep(oneRoundTime)

keep_alive()
t = asyncio.ensure_future(main())
asyncio.get_event_loop().run_forever()
