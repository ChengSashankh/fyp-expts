# -*- coding: utf-8 -*-
"""seq_interim_baseline.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1l3PaSQ_mEKZwmWcJJcMA8U5ZVwWJtFgP
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
from keras.models import load_model

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
    path_root = '/home/cksash/Documents/data/pickles'

# Define constants
data_path = os.path.join(path_root, 'tokenized/dataset_with_tokens.csv')

############################ Expt const ############################

batch_size = 20  # Batch size for training.
epochs = 100  # Number of epochs to train for.
latent_dim = 256  # Latent dimensionality of the encoding space.
num_samples = 10000  # Number of samples to train on.

############################ LaTeX const ###########################

# List of constants for LaTeX parsing
latex_math_symbol_macros = set(['Alpha', 'alpha', 'Nu', 'nu', 'Beta', 'beta', 'Xi', 'xi', 'Gamma', 'gamma', 'Omicron', 'omicron', 'Delta', 'delta', 'Pi', 'pi', 'var', 'Epsilon', 'epsilon', 'varepsilon', 'Rho', 'rho', 'varrho', 'Zeta', 'zeta', 'Sigma', 'sigma', 'varsigma', 'Eta', 'eta', 'Tau', 'tau', 'Theta', 'theta', 'vartheta', 'Upsilon', 'upsilon', 'Iota', 'iota', 'Phi', 'phi', 'varphi', 'Kappa', 'kappa', 'varkappa', 'Chi', 'chi', 'Lambda', 'lambda', 'Psi', 'psi', 'Mu', 'mu', 'Omega', 'omega'])
latex_operator_set = set(['+', '-', '=', '*', '/', '^', '_', '(', ')', '[', ']'])

######################### DS Load From File ########################

# Load all the data structures needed for training
# Save everything so far to file 

ip_vocab = pickle.load(open(os.path.join(path_root, 'interim_ip_vocab.pkl'), 'rb'))
ip_word2int = pickle.load(open(os.path.join(path_root, 'interim_ip_word2int.pkl'), 'rb'))
ip_int2word = pickle.load(open(os.path.join(path_root, 'interim_ip_int2word.pkl'), 'rb'))
ip_seq_lengths = pickle.load(open(os.path.join(path_root, 'interim_ip_seq_lengths.pkl'), 'rb'))

op_vocab = pickle.load(open(os.path.join(path_root, 'interim_op_vocab.pkl'), 'rb'))
op_word2int = pickle.load(open(os.path.join(path_root, 'interim_op_word2int.pkl'), 'rb'))
op_int2word = pickle.load(open(os.path.join(path_root, 'interim_op_int2word.pkl'), 'rb'))
op_seq_lengths = pickle.load(open(os.path.join(path_root, 'interim_op_seq_lengths.pkl'), 'rb'))
freq = pickle.load(open(os.path.join(path_root, 'interim_op_freq.pkl'), 'rb'))

sh_ip_wordLists = pickle.load(open(os.path.join(path_root, 'interim_sh_ip_wordLists.pkl'), 'rb'))
sh_op_wordLists = pickle.load(open(os.path.join(path_root, 'interim_sh_op_wordLists.pkl'), 'rb'))

print ('Done loading all datastructures from pickles')

#################### Calculate model dimensions ####################

max_encoder_seq_length = max(ip_seq_lengths)
ip_vocab_size = len(ip_vocab)
print ('Maximum encoder side sequence length = ' + str(max_encoder_seq_length))
print ('Encoder side vocabulary size = ' + str(ip_vocab_size))
print ('Encoder sequence length mean and variance are: ' + str(np.mean(ip_seq_lengths)) + ' , ' + str(np.var(ip_seq_lengths)))
print ('Distribution of encoder side lengths')
print (ip_vocab)
sns.distplot(ip_seq_lengths)

max_decoder_seq_length = max(op_seq_lengths)
op_vocab_size = len(op_vocab)
print ('Maximum decoder side sequence length = ' + str(max_decoder_seq_length))
print ('Decoder side vocabulary size = ' + str(op_vocab_size))
print ('Decoder sequence length mean and variance are: ' + str(np.mean(op_seq_lengths)) + ' , ' + str(np.var(op_seq_lengths)))
print ('Distribution of decoder side lengths')
print (op_vocab)
sns.distplot(op_seq_lengths)

######################### Modelling Tasks ##########################

# Define the encoder
encoder_inputs = Input(shape=(None, ip_vocab_size))
encoder = LSTM(latent_dim, return_state=True)
encoder_outputs, state_h, state_c = encoder(encoder_inputs)
# We discard `encoder_outputs` and only keep the states.
encoder_states = [state_h, state_c]

# Define the decoder
decoder_inputs = Input(shape=(None, op_vocab_size))
# We set up our decoder to return full output sequences,
# and to return internal states as well. We don't use the
# return states in the training model, but we will use them in inference.
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(decoder_inputs,
                                     initial_state=encoder_states)
decoder_dense = Dense(op_vocab_size, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

# Define the model that will turn
# `encoder_input_data` & `decoder_input_data` into `decoder_target_data`
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

print (model.metrics_names)
######################### Model Execution ##########################

# # Start from checkpoint
# model = load_model(os.path.join(path_root, 'final_ds/s2s.h5'))
start_from = 0

logfile = open(os.path.join(path_root, 'traininglog.txt'), 'a')
# Handle input data batch-wise
for e in range(epochs):
  i1 = 0
  if e == 0:
    i1 = start_from
  start = 0
  end = 0
  while i1 * batch_size < len(sh_ip_wordLists):
    start = i1 * batch_size
    end = min(start + batch_size, len(sh_ip_wordLists))
    i1 += 1
    
    n = end - start
    # Prepare encoder decoder feed data
    encoder_input_data = np.zeros(
        (n, max_encoder_seq_length, ip_vocab_size),
        dtype='float32')
    decoder_input_data = np.zeros(
        (n, max_decoder_seq_length, op_vocab_size),
        dtype='float32')
    decoder_target_data = np.zeros(
        (n, max_decoder_seq_length, op_vocab_size),
        dtype='float32')
    
    # Zip the data together
    for i, (input_eqn, target_text) in enumerate(zip(sh_ip_wordLists[start : end], sh_op_wordLists[start : end])):
        for t, char in enumerate(input_eqn):
            encoder_input_data[i, t, ip_word2int[char]] = 1.
        for t, char in enumerate(target_text):
            # decoder_target_data is ahead of decoder_input_data by one timestep
            decoder_input_data[i, t, op_word2int[char]] = 1.
            if t > 0:
                # decoder_target_data will be ahead by one timestep
                # and will not include the start character.
                decoder_target_data[i, t - 1, op_word2int[char]] = 1.

    model.train_on_batch([encoder_input_data[0 : int(0.85 * n)], decoder_input_data[0 : int(0.85 * n)]], decoder_target_data[0 : int(0.85 * n)])
    testloss = model.test_on_batch([encoder_input_data[int(-0.15*n) : -1], decoder_input_data[int(-0.15*n) : -1]], decoder_target_data[int(-0.15*n) : -1])
    # model.fit([encoder_input_data, decoder_input_data], decoder_target_data,
    #     epochs=epochs)
    print ('Test loss at (batch, epoch) = ' + str(i1 - 1) + ' , ' + str(e))
    logfile.write(str(e)+ ',' + str(i1 - 1) + ',' + str(testloss))
    print (str(e)+ ',' + str(i1 - 1) + ',' + str(testloss))

    # Save model
    model.save(os.path.join(path_root, 's2s.h5'))

