from stages.stage import Stage

'''
Save dataframe to file
Input: Grep results in pandas.DataFrame with headers as ['match', 'context']
Output: Grep results in pandas.DataFrame with headers as ['match', 'context']
'''
class DFToFile(Stage):
  def __init__(self, configs):
    self.name = configs['name']
    self.output_file = configs['output_file']
    self.op = None

  def run(self, ip_DF):
    ip_DF.to_csv(self.output_file)
    self.op = ip_DF
    return ip_DF