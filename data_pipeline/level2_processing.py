import pandas as pd

def add_percent_change_min(df: pd.DataFrame, col: str, mins: int) -> pd.DataFrame:
  # days = -1 means future min
  if mins < 0:
    df[f"{col}_{abs(mins)}_min_future_percent_change"] = (df[col].shift(mins) - df[col]) / df[col]
  else:
    df[f"{col}_{mins}_min_past_percent_change"] = (df[col] - df[col].shift(mins)) / df[col].shift(mins)
  return df

def process_level2():
  # 'time', 'open', 'high', 'low', 'close', 'volume',
  # 'num_trades', 'bid_price0', 'bid_quantity0' ... 'ask_price99', 'ask_quantity99'
  df = pd.read_csv("../raw_data/level2_raw_data.csv")
  out = df[['time', f"close", f"volume"]].copy()

  # add percent changes
  out = add_percent_change_min(out, 'close', -15)
  out = add_percent_change_min(out, 'close', -10)
  out = add_percent_change_min(out, 'close', -5)
  out = add_percent_change_min(out, 'volume', 1)
  
  # output to csv
  out.to_csv("../processed_data/level2_processed_data.csv")

def main():
  process_level2()

if __name__ == '__main__':
  main()
