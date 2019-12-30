from stages.stage import Stage

import pandas as pd

'''
Save dataframe to file
Input: Grep results in pandas.DataFrame with headers as ['match', 'context']
Output: Grep results in pandas.DataFrame with headers as ['match', 'context']
'''
class LoadDFFromCSV(Stage):
  def __init__(self, configs):
    self.name = configs['name']

  def run(self, ip):
    df = pd.read_csv(ip)
    return df