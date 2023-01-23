import pandas as pd

# global vars
friction_percents = [0.25, 0.50, 0.75, 1.0, 1.25, 1.50, 1.75, 2.0] # each item is a friction calculation
cryptos = ["btc", "eth", "doge"] # cryptos 

def add_percent_change_min(df: pd.DataFrame, col: str, mins: int) -> pd.DataFrame:
  for crypto in cryptos:
    # days = -1 means future min
    if mins < 0:
      df[f"{crypto}_{col}_{abs(mins)}_min_future_percent_change"] = (df[f"{crypto}_{col}"].shift(mins) - df[f"{crypto}_{col}"]) / df[f"{crypto}_{col}"]
    else:
      df[f"{crypto}_{col}_{mins}_min_past_percent_change"] = (df[f"{crypto}_{col}"] - df[f"{crypto}_{col}"].shift(mins)) / df[f"{crypto}_{col}"].shift(mins)
  return df

def process_level2():
  # time, crypto_open, crypto_high, crypto_low, crypto_close, crypto_volume, crypto_num_trades
  # crypto_friction_up_frictionpercent, crypto_friction_down_frictionpercent
  df = pd.read_csv("raw_data/level2_raw_data.csv")

  
  # columns to copy
  cols_to_copy = ["time"]

  # add basic columns
  cols_to_add = ["close", "volume"]
  for col_to_add in cols_to_add:
    for crypto in cryptos:
      cols_to_copy += [f"{crypto}_{col_to_add}"]

  # add friction columns
  # for crypto in cryptos:
  #   for friction_percent in friction_percents:
  #     cols_to_copy +=[f"{crypto}_friction_up_{friction_percent}"]
  #     cols_to_copy +=[f"{crypto}_friction_down_{friction_percent}"]
  
  out = df[cols_to_copy].copy()

  # add friction diffs
  for crypto in cryptos:
    for friction_percent in friction_percents:
      out[f"{crypto}_friction_diff_{friction_percent}"] = df[f"{crypto}_friction_down_{friction_percent}"] - df[f"{crypto}_friction_up_{friction_percent}"]

  # add percent changes
  out = add_percent_change_min(out, 'close', -15)
  out = add_percent_change_min(out, 'close', -10)
  out = add_percent_change_min(out, 'close', -5)
  out = add_percent_change_min(out, 'close', 15)
  out = add_percent_change_min(out, 'close', 10)
  out = add_percent_change_min(out, 'close', 5)
  out = add_percent_change_min(out, 'volume', 1)
  
  # output to csv
  out.to_csv("processed_data/level2_processed_data.csv")

def main():
  process_level2()

if __name__ == '__main__':
  main()
