import pandas as pd

def get_eth_level1_data() -> pd.DataFrame:
  """returns level 1 data as a dataframe, reading from csv 

  Returns:
      pd.DataFrame: eth level1 data
  """
  df = pd.read_csv("data/eth_level1_data.csv")
  assert(len(df.index) == 1461)
  return df

def main():
  print(get_eth_level1_data())
  return

if __name__ == '__main__':
  main()
