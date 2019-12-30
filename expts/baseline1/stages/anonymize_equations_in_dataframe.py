from stages.stage import Stage

import numpy as np
import pandas as pd
import ast
import multiprocessing

'''
Filter dataframe to get rid of problematic entries
Input: Grep results in pandas.DataFrame with headers as ['match', 'context']
Output: Filtered entries only from DataFrame with headers as ['match', 'context']
'''
class AnonymizeEquations(Stage):

  def __init__(self, configs):
    print (configs)
    self.name = configs['name']
  
    # List of constants for LaTeX parsing
    self.latex_math_symbol_macros = set(['Alpha', 'alpha', 'Nu', 'nu', 'Beta', 'beta', 'Xi', 'xi', 'Gamma', 'gamma', 'Omicron', 'omicron', 'Delta', 'delta', 'Pi', 'pi', 'var', 'Epsilon', 'epsilon', 'varepsilon', 'Rho', 'rho', 'varrho', 'Zeta', 'zeta', 'Sigma', 'sigma', 'varsigma', 'Eta', 'eta', 'Tau', 'tau', 'Theta', 'theta', 'vartheta', 'Upsilon', 'upsilon', 'Iota', 'iota', 'Phi', 'phi', 'varphi', 'Kappa', 'kappa', 'varkappa', 'Chi', 'chi', 'Lambda', 'lambda', 'Psi', 'psi', 'Mu', 'mu', 'Omega', 'omega'])
    self.latex_operator_set = set(['+', '-', '=', '*', '/', '^', '_', '(', ')', '[', ']'])

  # Check if a token is a variable or a relation
  def is_object(self, tk):
    return (tk[0] == 'char') or (tk[0] == 'macro' and tk[1] in self.latex_math_symbol_macros)

  def anonymize_equation(self, equation):
    res = []
    tokens = {}
    count = 1
    
    for tk in equation:
      if not self.is_object(tk) or tk[1] in self.latex_operator_set:
        res.append(tk[1])
      elif tk[1] in tokens:
        res.append(tokens[tk[1]])
      else:
        tokens[tk[1]] = '<var' + str(count) + '>'
        res.append(tokens[tk[1]])
        count += 1

    return res
  
  # Running for all equations
  def anonymize_all_equations(self, equations):
    pool = multiprocessing.Pool()
    anonymized_equations = pool.map(self.anonymize_equation, equations)
    return anonymized_equations
  
  # Run handle for pipeline
  def run(self, df):
    df['equation'] = self.anonymize_all_equations(df['equation'])
    return df
