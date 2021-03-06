# -*- coding: utf-8 -*-
"""data_preparation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1D3HoylqhKBqqIFKp7WtcurnBS5ws9kkn
"""

# Imports
import keras
import pandas as pd
import numpy as np
import copy
import ast
import os
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from keras.models import Model
from keras.layers import Input, LSTM, Dense
from progressbar import ProgressBar
from pylatexenc.latexwalker import LatexWalker, LatexWalkerEndOfStream

import nltk
from nltk import word_tokenize
from nltk import PorterStemmer
from nltk.corpus import stopwords

nltk.download('stopwords')
stop_words = stopwords.words('english')

# Set appropriately
running_on_colab = False

############################ Disk Paths ############################

# For Google Colab only
if running_on_colab: 
  from google.colab import drive
  drive.mount('/content/gdrive', force_remount=True)

  # Set path root to go from Google drive
  path_root = '/content/gdrive/My Drive/'
else:
  # Set path root to go from HDD
  path_root = '/home/cksash/Documents/data/'

# Define constants
data_path = os.path.join(path_root, 'tokenized/dataset_with_tokens.csv')

############################ Expt const ############################

# batch_size = 20  # Batch size for training.
# epochs = 100  # Number of epochs to train for.
# latent_dim = 256  # Latent dimensionality of the encoding space.
# num_samples = 10000  # Number of samples to train on.

############################ LaTeX const ###########################

# List of constants for LaTeX parsing
latex_math_symbol_macros = set(['Alpha', 'alpha', 'Nu', 'nu', 'Beta', 'beta', 'Xi', 'xi', 'Gamma', 'gamma', 'Omicron', 'omicron', 'Delta', 'delta', 'Pi', 'pi', 'var', 'Epsilon', 'epsilon', 'varepsilon', 'Rho', 'rho', 'varrho', 'Zeta', 'zeta', 'Sigma', 'sigma', 'varsigma', 'Eta', 'eta', 'Tau', 'tau', 'Theta', 'theta', 'vartheta', 'Upsilon', 'upsilon', 'Iota', 'iota', 'Phi', 'phi', 'varphi', 'Kappa', 'kappa', 'varkappa', 'Chi', 'chi', 'Lambda', 'lambda', 'Psi', 'psi', 'Mu', 'mu', 'Omega', 'omega'])
latex_operator_set = set(['+', '-', '=', '*', '/', '^', '_', '(', ')', '[', ']'])

# Check if a token is a variable or a relation
def is_object(tk):
  return (tk[0] == 'char') or (tk[0] == 'macro' and tk[1] in latex_math_symbol_macros)

# Anonymize variables in equations 
def anon_tokenized_eqn(tk_eqn, tokens):
  res = []
  count = 0
  
  for tk in ast.literal_eval(tk_eqn):
    if not is_object(tk) or tk[1] in latex_operator_set:
      res.append(tk[1])
    elif tk[1] in tokens:
      res.append(tokens[tk[1]])
    else:
      tokens[tk[1]] = '<var' + str(count) + '>'
      res.append(tokens[tk[1]])
      count += 1
    
    # print (str(tk[1]) + ' ' + res[-1])
  # print (tokens)
  return res

# Turn equations in string form to array form
def str_to_arr(eqns):
  i = 0

  while i < len(eqns):
    if i % 10000 == 0:
      print ('Progress (str -> arr): ' + str(i))
    try:
      eqns[i] = ast.literal_eval(eqns[i])
    except Exception as e:
      print ('Encountered exception ' + str(e))
      print ('Error while parsing ' + str(eqns[i]) + ' at index ' + str(i))
    i += 1
  
  return eqns

def get_anon_eqns(eqns):
  anons = []

  pbar = ProgressBar()
  for eqn in pbar(eqns):
    anons.append(anon_tokenized_eqn(eqn, {}))
  
  return anons


# For text: Get vocabulary, int2word and word2int
def get_vocab_con(wordLists):
  words = set()
  freq = {}
  int2word = {}
  word2int = {}
  
  for w1 in wordLists:
    for w in w1:
      if w in freq:
        freq[w] = freq[w] + 1
      else:
        freq[w] = 1
  
  for wl in wordLists:
      [words.add(w.lower()) for w in wl]
  
  for i, word in enumerate(list(words)):
      int2word[i] = word
      word2int[word] = i
  
  return words, int2word, word2int, freq

# For eqn: Get vocabulary, int2word and word2int
def get_vocab_eqn(eqns):
  var_set = set()
  int2var = {}
  var2int = {}
  
  for wl in eqns:
      [var_set.add(w) for w in wl]
  
  for i, var in enumerate(list(var_set)):
      int2var[i] = var
      var2int[var] = i
  
  return var_set, int2var, var2int

# Preprocess contexts 
def linguistic_preprocess(contexts):
  porter = PorterStemmer()
  processed = []
  pbar = ProgressBar()
  for context in pbar(contexts):
    # Tokenize the sentence
    tkn_context = word_tokenize(context)

    # Drop the stopwords
    tkn_context = [word for word in tkn_context if word not in stop_words]

    # Stem the tokens
    stemmed = []
    for tkn in tkn_context:
      stemmed.append(porter.stem(tkn))
    
    processed.append(stemmed)
  
  return processed

# Remove rows with equations in context
def filter_data(df):
  changes = np.zeros((df.shape[0], 3))
  cons = []
  tkn_eqn = []
  discarded = 0

  for i, row in df.iterrows():
    if i % 20000 == 0:
      print ('Progress: ' + str(i))
    eqn = row['equation'] 
    con = row['contexts']
    refs = row['refs']

    if '\\begin{eqnarray}' == str(row['equation']):
      discarded += 1
      continue

    if '\\begin{eqnarray}' in str(pre) or '\\begin{equation}' in str(pre):
      pre = ''
      changes[i][0] = 1
    
    if '\\begin{eqnarray}' in str(post) or '\\begin{equation}' in str(pre):
      post = ''
      changes[i][1] = 1

    if '\\begin{eqnarray}' in str(refs) or '\\begin{equation}' in str(pre):
      refs = ''
      changes[i][2] = 1
    
    con = str(pre) + str(post) + str(refs)

    if con == '':
      discarded += 1
      continue
    
    cons.append(con)
    tkn_eqn.append(row['tkn'])

  print ('Number of context pieces trimmed ' + str(np.sum(changes, axis = 0)))
  print ('Number of rows discarded: ' + str(discarded))

  return changes, cons, tkn_eqn

def sequential_tokenization(eqn):
  tokenized = []
  start = 0

  if '\\newcommand' in eqn:
    raise NameError('New command detected')

  while start < len(eqn):
      w = LatexWalker(eqn, tolerant_parsing=True)
      
      try:
        tk = w.get_token(start)
      except LatexWalkerEndOfStream:
        break
      # except Exception as e:
      #   print ('Caught exception ' + str(e))
      #   print ('Offending equation: ' + str(eqn))
      #   tokenized.append([])
      #   continue
      
      tokenized.append([tk.tok, tk.arg])
      start = (tk.pos + tk.len)

  return tokenized

def remove_specials(tk_eqn):
  eqn = []
  
  for tk in tk_eqn:
    if len(tk) < 1 or tk[0] == 'specials' or tk[0] == 'comment':
      continue
    eqn.append(tk)
  
  return eqn

# Tokenize the equations
def get_tokenized_eqn(eqns):
  pbar = ProgressBar()
  
  tk_eqns = []
  count = 0
  skipped = np.zeros(len(eqns))
  dropped = 0

  print ('Total: ' + str(len(eqns)))
  logfile = open('error-log.txt', 'w')

  for eqn in pbar(eqns):
    count += 1
    try:
      tokenized = sequential_tokenization(eqn)
    except Exception as e:
      logfile.write(str(count) + ', ' + str(e))
      print ('Skipping')
      skipped[count - 1] = 1
      dropped += 1
      print ('Dropped ' + str(dropped) + ' / ' + str(count))
    
    tokenized = remove_specials(tokenized)
    tk_eqns.append(tokenized)
    
  return tk_eqns, skipped


############ Acquiring the final features and targets ############
data_available = False

if data_available:
  # If the dataset exists, read it
  print ('data_available set to True => Reading features and targets from file')
  ndf = pd.read_csv(os.path.join(data_path, '/tokenized/eqn_and_targets.csv'))
  print ('Data read from file completed')

  print (type(ndf['tkn'][5]))
  print ('Converting string equations back into data structure')
  arrayform = str_to_arr(list(ndf['tkn']))
  print ('Done converting to arrays')
  print ('Assigning back to dataframe')
  print (len(arrayform))
  print (ndf.shape)
  ndf['tkn'] = arrayform

  print (type(ndf['tkn'][5]))
  print ('Final dataset has been read from file')
else:
  # If the dataset doesn't exist, create it
  print ('data_available set to False => Building features and targets from original dataset')
  # Read the original dataset with tokenization
  data_path = os.path.join(path_root, 'rebuilt_181219.csv')
  
  print ('Reading data from original dataset')
  df = pd.read_csv(data_path)
  print ('Data read completed')
  
  print ('Columns in original dataset')
  print (df.columns)

  print ('Tokenize equations in the dataset')
  df['equation'], df['skipped'] = get_tokenized_eqn(df['equation'])

  print (df.shape)
  # Drop problematic equations
  df = df[df.skipped == 0]
  print (df.shape)

  df.to_csv('/home/cksash/Documents/proj/fyp-main/expts/seq2seq/checkpoint.csv')

  # Join the contexts and filter out problematic contexts
  print ('Sanitizing dataset entried: Removing problematic contexts + Merging pre, post and refs into context string')
  con_trim_flags, cons, tkn  = filter_data(df)

  print ('Proceeding to linguistic preprocessing')
  
  # Preprocess the contexts
  cons = linguistic_preprocess(cons)
  print ('Completed linguistic preprocessing')

  print ('Proceeding to save processed contexts')
  pickle.dump(cons, open('cons_processed.pkl', 'wb'))
  print ('Done saving processed contexts')

  print ('Creating new dataset from entries')
  ndf = pd.DataFrame()
  ndf['con'] = cons
  
  # Drop token type annotation and anonymize the variables 
  ndf['tkn'] = get_anon_eqns(tkn)

  output_path = os.path.join(path_root, 'rebuilt_2612.csv')
  print ('Saving built dataset to csv file at: ' + output_path)
  ndf.to_csv(output_path)

############ Prepare the features and targets to feed to the sequence model ############
# For input variables
ip_wordLists = ndf['tkn']
op_wordLists = [str(eqn).replace('\n', ' ').lower().split(' ') for eqn in ndf['con']]

# Filter the op_wordLists
remove = list('.,~/()%:`\'\"#?')
remove.append('<ref>')
remove.append('</ref>')
remove.append('\t')

ban_syms = ['\\', '$', '{', '}', '&', '+', '=', '_', '^', '*', '[', ']', '|', '<', '>', '@']

i = 0
while i < len(op_wordLists):
  if i % 10000 == 0:
    print ('Context pre-processing progress: ' + str(i))
  newarr = []
  # Remove some characters from every word
  for r in remove:
    op_wordLists[i] = [v.replace(r, '') for v in op_wordLists[i]]
  
  # Remove terms that contains certain characters / meet certain criteria
  op_wordLists[i] = [v for v in op_wordLists[i] if not v.isdigit()]
  op_wordLists[i] = [v for v in op_wordLists[i] if len(v) >= 2]

  for s in ban_syms:
    op_wordLists[i] = [v for v in op_wordLists[i] if s not in v]

  i += 1
# Select a threshold value on the length of input sequence
ip_seq_lengths = [len(eqn) for eqn in ip_wordLists]
op_seq_lengths = [len(eqn) for eqn in op_wordLists]

# # Selecting a threshold
# thresholds = range(100, 250, 25)
# for threshold in thresholds:
#   print (threshold)
#   print (sum([1 for i, conlen in enumerate(op_seq_lengths) if conlen < threshold]))

# Drop input-output pairs where the output sequence length > 200
threshold = 100
ip_thresh = 450
shorter_indices = [i for i, conlen in enumerate(op_seq_lengths) if ((conlen < threshold) and (len(op_wordLists[i]) > 0) and not (len(op_wordLists[i]) == 1 and op_wordLists[i][0] == 'nan'))]
print ('Selecting ' + str(len(shorter_indices)) + ' input-output pairs based on op length threshold')

# Drop input-output pairs where the input sequence length > 200
shorter_indices = [i for i in shorter_indices if ip_seq_lengths[i] < ip_thresh]
print ('Selecting ' + str(len(shorter_indices)) + ' input-output pairs based on ip length threshold')

sh_ip_wordLists = [ip_wordLists[i] for i in shorter_indices]
sh_op_wordLists = [op_wordLists[i] for i in shorter_indices]

ip_seq_lengths = [ip_seq_lengths[i] for i in shorter_indices]
op_seq_lengths = [op_seq_lengths[i] for i in shorter_indices]

# Some checks and information
print ('Check if feature counts = target counts: ' + str(len (sh_op_wordLists) == len (sh_ip_wordLists)))

# Build the vocabulary
ip_vocab, ip_int2word, ip_word2int = get_vocab_eqn(sh_ip_wordLists)
op_vocab, op_int2word, op_word2int, freq = get_vocab_con(sh_op_wordLists)

print ('Size of input vocabulary = ' + str(len(ip_vocab)))
print ('Size of output vocabulary = ' + str(len(op_vocab)))

# Save everything so far to file 

pickle.dump(ip_vocab, open(os.path.join(path_root, 'final_ds/interim_ip_vocab.pkl'), 'wb'))
pickle.dump(ip_word2int, open(os.path.join(path_root, 'final_ds/interim_ip_word2int.pkl'), 'wb'))
pickle.dump(ip_int2word, open(os.path.join(path_root, 'final_ds/interim_ip_int2word.pkl'), 'wb'))
pickle.dump(ip_seq_lengths, open(os.path.join(path_root, 'final_ds/interim_ip_seq_lengths.pkl'), 'wb'))

pickle.dump(op_vocab, open(os.path.join(path_root, 'final_ds/interim_op_vocab.pkl'), 'wb'))
pickle.dump(op_word2int, open(os.path.join(path_root, 'final_ds/interim_op_word2int.pkl'), 'wb'))
pickle.dump(op_int2word, open(os.path.join(path_root, 'final_ds/interim_op_int2word.pkl'), 'wb'))
pickle.dump(freq, open(os.path.join(path_root, 'final_ds/interim_op_freq.pkl'), 'wb'))
pickle.dump(op_seq_lengths, open(os.path.join(path_root, 'final_ds/interim_op_seq_lengths.pkl'), 'wb'))

pickle.dump(sh_ip_wordLists, open(os.path.join(path_root, 'final_ds/interim_sh_ip_wordLists.pkl'), 'wb'))
pickle.dump(sh_op_wordLists, open(os.path.join(path_root, 'final_ds/interim_sh_op_wordLists.pkl'), 'wb'))

"""## All the code after this has been reproduced for clarity in the training notebook"""
