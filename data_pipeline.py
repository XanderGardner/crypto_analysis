import pandas as pd

def add_percent_change(df: pd.DataFrame, col: str, days: int) -> pd.DataFrame:
  # days = -1 means future day
  if days < 0:
    df[f"{col} {abs(days)} Day Future Percent Change"] = (df[col].shift(days) - df[col]) / df[col]
  else:
    df[f"{col} {days} Day Past Percent Change"] = (df[col] - df[col].shift(days)) / df[col].shift(days)
  return df

def process_eth_level1():
  # 'Date', 'Price', 'Market Cap', 'Volume', 'Active Addresses',
  # 'Daily Transactions', 'Twitter Followers', 'Weekly Commits Core',
  # 'Weekly Commits Sub', 'Weekly Devs Core', 'Weekly Devs Sub',
  # 'Total Value Locked', 'Price Bitcoin'
  df = pd.read_csv("raw_data/eth_level1_raw_data.csv")

  # add momentum columns for each daily raw data column
  daily_raw_data_columns = ['Price','Market Cap','Volume','Active Addresses','Daily Transactions','Twitter Followers','Total Value Locked','Price Bitcoin']
  for col in daily_raw_data_columns:
    df = add_percent_change(df, col, 1)
    df = add_percent_change(df, col, 7)
    df = add_percent_change(df, col, 14)
    df = add_percent_change(df, col, 30)

  # add momentum columns for each weekly raw data column
  weekly_raw_data_columns = ['Weekly Commits Core','Weekly Commits Sub','Weekly Devs Core','Weekly Devs Sub']
  for col in weekly_raw_data_columns:
    df = add_percent_change(df, col, 7)
    df = add_percent_change(df, col, 14)
    df = add_percent_change(df, col, 30)

  # add y value
  df = add_percent_change(df, "Price", -1)
  df = add_percent_change(df, "Price", -7)

  # output to csv
  df.to_csv("processed_data/eth_level1_processed_data.csv")

def process_btc_level2():
  # 'time', 'open', 'high', 'low', 'close', 'volume',
  # 'num_trades', 'bid_price0', 'bid_quantity0' ... 'ask_price99', 'ask_quantity99'
  df = pd.read_csv("raw_data/btc_level2_raw_data.csv")
  out = df[['time', 'close', 'volume']].copy()

  # calculate friction up and down at each time
  friction_percent = 0.005
  friction_up = []
  friction_down = []
  hit_range = 0
  for i in df.index:
    close = df.loc[i, "close"]

    # up friction (ask)
    up = 0
    ask_i = 0
    while ask_i < 100 and (df.loc[i, f"ask_price{ask_i}"] - close) / close < friction_percent:
      up += df.loc[i, f"ask_price{ask_i}"] * df.loc[i, f"ask_quantity{ask_i}"]
      ask_i += 1
      if ask_i == 100:
        hit_range += 1
    friction_up.append(up)

    # down friction (bid)
    down = 0
    bid_i = 0
    while bid_i < 100 and (close - df.loc[i, f"bid_price{bid_i}"]) / close < friction_percent:
      down += df.loc[i, f"bid_price{bid_i}"] * df.loc[i, f"bid_quantity{bid_i}"]
      bid_i += 1
      if bid_i == 100:
        hit_range += 1
    friction_down.append(down)

  print(f"hit range: {hit_range}")
  out['friction_up'] = friction_up
  out['friction_down'] = friction_down
  
  # output to csv
  out.to_csv("processed_data/btc_level2_processed_data.csv")

def main():
  process_btc_level2()

if __name__ == '__main__':
  main()
