import pandas as pd
import numpy as np
from binance.client import Client
import datetime as dt
import time

def main():
  # global vars
  depth = 5000 # number of bids and asks to inspect (5000 at most)
  friction_percents = [0.25, 0.50, 0.75, 1.0, 1.25, 1.50, 1.75, 2.0] # each item is a friction calculation
  cryptos = ["btc", "eth", "doge"] # cryptos to collect data on

  # client configuration - keys not needed here since using free api
  api_key = "API HERE"
  api_secret = "SECRET API HERE"
  client = Client(api_key, api_secret, tld="us")

  # build on past csv
  file = "raw_data/level2_raw_data.csv"
  try:
    df = pd.read_csv(file, index_col=0)
  except FileNotFoundError:
    print("creating new data file")
    cols = ["time"]
    for crypto in cryptos:
      cols += [f"{crypto}_open", f"{crypto}_high", f"{crypto}_low", f"{crypto}_close", f"{crypto}_volume", f"{crypto}_num_trades"]
      for friction_percent in friction_percents:
        cols += [f"{crypto}_friction_up_{friction_percent}"]
      for friction_percent in friction_percents:
        cols += [f"{crypto}_friction_down_{friction_percent}"]
    df = pd.DataFrame(columns=cols)

  starttime = time.time()
  while True:
    # get data from client
    klines = [[]] * len(cryptos)
    l2_data = [[]] * len(cryptos)
    for i, crypto in enumerate(cryptos):
      klines[i] = client.get_historical_klines(f"{crypto.upper()}USDT", "1m", limit=1)[0]
      l2_data[i] = client.get_order_book(symbol=f"{crypto.upper()}USDT", limit=depth)

    next_row_all_cryptos = [dt.datetime.fromtimestamp(klines[0][0]/1000.0)] # convert to time
    for ci, crypto in enumerate(cryptos):
      # add level 3 data
      # ['open_time','open', 'high', 'low', 'close', 'volume','close_time', 'qav','num_trades','taker_base_vol','taker_quote_vol','ignore']
      next_row = [klines[ci][1], klines[ci][2], klines[ci][3], klines[ci][4], klines[ci][5], klines[ci][8]]

      # add level 2 data
      close = float(klines[ci][4])

      frictions_up = [0] * len(friction_percents)
      for p_str, q_str in l2_data[ci]['asks']:
        price = float(p_str)
        quantity = float(q_str)
        diff = abs((price - close) / close)
        for i, perc_level in enumerate(friction_percents):
          if diff < perc_level:
            frictions_up[i] += price * quantity
      next_row += frictions_up
      
      frictions_down = [0] * len(friction_percents)
      for p_str, q_str in l2_data[ci]['bids']:
        price = float(p_str)
        quantity = float(q_str)
        diff = abs((price - close) / close)
        for i, perc_level in enumerate(friction_percents):
          if diff < perc_level:
            frictions_down[i] += price * quantity
      next_row += frictions_down

      next_row_all_cryptos += next_row
    
    # add next row to dataframe
    df.loc[len(df.index)] = next_row_all_cryptos
    
    # save results in csv
    df.to_csv(file)

    # run exactly every minute
    time.sleep(60.0 - ((time.time() - starttime) % 60.0))

if __name__ == '__main__':
  main()
