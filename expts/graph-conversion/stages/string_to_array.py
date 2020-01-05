from stages.stage import Stage

import pandas as pd
import ast
import multiprocessing

'''
Save dataframe to file
Input: Grep results in pandas.DataFrame with headers as ['match', 'context']
Output: Grep results in pandas.DataFrame with headers as ['match', 'context']
'''
class String2Array(Stage):
  def __init__(self, configs):
    self.name = configs['name']

  def string_to_array_helper(self, equation):
    return ast.literal_eval(equation)

  def string_to_array(self, equations):
    pool = multiprocessing.Pool()
    equations = pool.map(self.string_to_array_helper, equations)

    return equations

  def run(self, df):
    equations = df['equation']
    return equations
