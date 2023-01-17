import pandas as pd

def add_percent_change(df: pd.DataFrame, col: str, days: int) -> pd.DataFrame:
  # days = -1 means future day
  if days < 0:
    df[f"{col}_{abs(days)}_Day_Future_Percent_Change"] = (df[col].shift(days) - df[col]) / df[col]
  else:
    df[f"{col}_{days}_Day_Past_Percent_Change"] = (df[col] - df[col].shift(days)) / df[col].shift(days)
  return df

def main():
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
  return 0

if __name__ == '__main__':
  main()
