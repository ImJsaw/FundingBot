from flask import Flask
from threading import Thread
app = Flask('name')

counter = 0

@app.route('/')
def alive():
  adding()
  s = 'Bot Alive'+ str(counter)
  return s

def adding():
  global counter
  counter = counter + 1

def run():
  app.run(host="0.0.0.0", port=8080)

def keep_alive():
  server = Thread(target=run)
  server.start()