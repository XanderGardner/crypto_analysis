import pandas as pd
import numpy as np
from binance.client import Client
import datetime as dt
import time

def main():
  # global vars
  depth = 1000 # number of bids and asks to collect

  # client configuration - keys not needed here since using free api
  api_key = 'API HERE'
  api_secret = 'SECRET API HERE'
  client = Client(api_key, api_secret, tld='us')

  # build on past csv
  file = "raw_data/btc_level2_raw_data.csv"
  try:
    df = pd.read_csv(file, index_col=0)
  except FileNotFoundError: 
    print("creating new data file")
    cols = ['time', 'open','high','low','close','volume','num_trades']
    for i in range(depth):
      cols += [f"bid_price{i}", f"bid_quantity{i}"]
    for i in range(depth):
      cols += [f"ask_price{i}", f"ask_quantity{i}"]
    df = pd.DataFrame(columns=cols)

  starttime = time.time()
  while True:
    # get data from client
    klines = client.get_historical_klines("BTCUSDT", "1m", limit=1)[0]
    l2_data = client.get_order_book(symbol="BTCUSDT", limit=depth)

    # add level 3 data
    next_row = [dt.datetime.fromtimestamp(klines[0]/1000.0)]
    # ['open_time','open', 'high', 'low', 'close', 'volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol','ignore']
    next_row += [klines[1], klines[2], klines[3], klines[4], klines[5], klines[8]]

    # add level 2 data
    for i in range(depth):
      if i < len(l2_data['bids']):
        price, quantity = l2_data['bids'][i]
        next_row += [price, quantity] # bid prices get smaller for greater i
      else:
        next_row += [np.NAN, np.NAN]
    for i in range(depth):
      if i < len(l2_data['asks']):
        price, quantity = l2_data['asks'][i]
        next_row += [price, quantity] # ask prices get greater for greater i
      else:
        next_row += [np.NAN, np.NAN] 

    df.loc[len(df.index)] = next_row
    
    # save results in csv
    df.to_csv(file)

    # run exactly every minute
    time.sleep(60.0 - ((time.time() - starttime) % 60.0))

if __name__ == '__main__':
  main()
