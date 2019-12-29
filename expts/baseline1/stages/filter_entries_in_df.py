from stages.stage import Stage

import numpy as np
import pandas as pd
import ast

'''
Filter dataframe to get rid of problematic entries
Input: Grep results in pandas.DataFrame with headers as ['match', 'context']
Output: Filtered entries only from DataFrame with headers as ['match', 'context']

#DONE: discard any row with empty entries. These are written when there are errors in reading files or such.

'''
class FilterGrepEntries(Stage):
  def __init__(self, configs):
    self.name = configs['name']
    self.drop_if_contains = configs['drop_if_contains']
    self.drop_if_equals = configs['drop_if_equals']

  # Remove rows with equations in context
  def filter_data(self, df):
    selected_cons = []
    selected_refs = []
    selected_eqns = []

    discarded = 0

    for i, row in df.iterrows():
      if i % 20000 == 0:
        print ('Filtering progress: ' + str(i))
      
      eqn = row['equation'] 
      con = row['context']
      ref = row['reference']

      if '\\begin{eqnarray}' == str(eqn) or len(ast.literal_eval(eqn)) == 0:
        discarded += 1
        continue

      if '\\begin{eqnarray}' in str(con):
        con = ''

      if '\\begin{eqnarray}' in str(ref):
        ref = ''

      if con == '' and ref == '':
        discarded += 1
        continue
      
      selected_cons.append(con)
      selected_eqns.append(eqn)
      selected_refs.append(ref)

    print ('Number of rows discarded: ' + str(discarded))

    return selected_cons, selected_eqns, selected_refs
  
  def remove_unwanted_symobols_in_contexts(self, contexts):
    op_wordLists = [str(eqn).replace('\n', ' ').lower().split(' ') for eqn in ndf['con']]
  
  def run(self, df):
    cons, eqns, refs = self.filter_data(df)
    filtered_df = pd.DataFrame()

    filtered_df['equation'] = eqns
    filtered_df['context'] = cons
    filtered_df['reference'] = refs

    return filtered_df


