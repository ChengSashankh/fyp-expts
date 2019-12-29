from stages.stage import Stage

import nltk
import multiprocessing
import pickle
import os
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from progressbar import ProgressBar

nltk.download('punkt')

'''
Create the datastructures required for seq2seq model and save as pickles
Input: DataFrame with inputs and targets for training. 
Output: Pickles with datastructures created, saved to file.
'''
class CreateSeq2SeqDataStructures(Stage):
  def __init__(self, configs):
    self.name = configs['name']
    
    # Remove these characters from all contexts
    self.remove = list('.,~/()%:`\'\"#?')
    self.remove.append('<ref>')
    self.remove.append('</ref>')
    self.remove.append('\t')
    
    # Remove terms that contain these characters
    self.ban_syms = ['\\', '$', '{', '}', '&', '+', '=', '_', '^', '*', '[', ']', '|', '<', '>', '@']
  
  def remove_characters_from_context(self, op_wordlist):
    for r in self.remove:
      op_wordlist = [token.replace(r, '') for token in op_wordlist]
    return op_wordlist
  
  def drop_tokens(self, op_wordlist):
    reduced_wordlist = [v for v in op_wordlist if ((not v.isdigit()) and len(v) >= 2)]

    for sym in self.ban_syms:
      reduced_wordlist = [v for v in op_wordlist if sym not in v]
    
    return reduced_wordlist

  def apply_length_threshold_for_op_sequences(self, threshold, ip_wordlists, op_wordlists):
    # Select a threshold value on the length of input sequence
    ip_seq_lengths = [len(eqn) for eqn in ip_wordlists]
    op_seq_lengths = [len(eqn) for eqn in op_wordlists]

    shorter_indices = [i for i, conlen in enumerate(op_seq_lengths) if ((conlen < threshold) and (len(op_wordlists[i]) > 1) and not (op_wordlists[i][0] == 'nan'))]
    print ('Selecting ' + str(len(shorter_indices)) + ' input-output pairs based on ip length threshold')

    sh_ip_wordlists = [ip_wordlists[i] for i in shorter_indices]
    sh_op_wordlists = [op_wordlists[i] for i in shorter_indices]

    ip_seq_lengths = [ip_seq_lengths[i] for i in shorter_indices]
    op_seq_lengths = [op_seq_lengths[i] for i in shorter_indices]

    # Some checks and information
    print ('Check if feature counts = target counts: ' + str(len (sh_op_wordlists) == len (sh_ip_wordlists)))

    return sh_ip_wordlists, sh_op_wordlists, ip_seq_lengths, op_seq_lengths
  
  def build_vocabulary_datastructures_eqn(self, equations):
    var_set = set()
    int2var = {}
    var2int = {}
    
    for wl in equations:
        [var_set.add(w) for w in wl]
    
    for i, var in enumerate(list(var_set)):
        int2var[i] = var
        var2int[var] = i
  
    return var_set, int2var, var2int
  
  # For text: Get vocabulary, int2word and word2int
  def build_vocabulary_datastructures_con(self, wordLists):
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
  
  def save_as_pickle(self, datastructure, picklepath):
    pickle.dump(datastructure, open(picklepath, 'wb'))

  def process_op_wordlists(self, op_wordlists):
    pool = multiprocessing.Pool()
    op_wordlists = pool.map(self.remove_characters_from_context, op_wordlists)
    pool = multiprocessing.Pool()
    op_wordlists = pool.map(self.drop_tokens, op_wordlists)

    return op_wordlists

  def run(self, df):
    df['context'] = self.process_op_wordlists(df['context'])
    sh_ip_wordLists, sh_op_wordLists, ip_seq_lengths, op_seq_lengths = self.apply_length_threshold_for_op_sequences(100, df['equation'], df['context'])
    
    ip_vocab, ip_int2word, ip_word2int = self.build_vocabulary_datastructures_eqn(df['equation'])
    op_vocab, op_int2word, op_word2int, freq = self.build_vocabulary_datastructures_con(df['context'])

    self.save_as_pickle(ip_vocab, os.path.join('~/Documents/baseline1/output/', 'ip_vocab'))
    self.save_as_pickle(ip_int2word, os.path.join('~/Documents/baseline1/output/', 'ip_int2word'))
    self.save_as_pickle(ip_word2int, os.path.join('~/Documents/baseline1/output/', 'ip_word2int'))
    self.save_as_pickle(ip_seq_lengths, os.path.join('~/Documents/baseline1/output/', 'ip_seq_lengths'))

    self.save_as_pickle(op_vocab, os.path.join('~/Documents/baseline1/output/', 'op_vocab'))
    self.save_as_pickle(op_int2word, os.path.join('~/Documents/baseline1/output/', 'op_int2word'))
    self.save_as_pickle(op_word2int, os.path.join('~/Documents/baseline1/output/', 'op_word2int'))
    self.save_as_pickle(op_seq_lengths, os.path.join('~/Documents/baseline1/output/', 'op_seq_lengths'))
    
    self.save_as_pickle(freq, os.path.join('~/Documents/baseline1/output/', 'freq'))
    self.save_as_pickle(ip_seq_lengths, os.path.join('~/Documents/baseline1/output/', 'sh_ip_seq_lengths'))
    self.save_as_pickle(op_seq_lengths, os.path.join('~/Documents/baseline1/output/', 'sh_op_seq_lengths'))

    return df

