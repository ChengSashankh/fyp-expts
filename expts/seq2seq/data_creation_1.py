import pandas as pd
import os
import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from progressbar import ProgressBar

nltk.download('punkt')


# Linguistic preprocessing of context
def preprocess_context(context):
  porter = PorterStemmer()
  tkn_lem = []
  for w in word_tokenize(s):
      tkn_lem.append(porter.stem(w))
  print (tkn_lem)

# Search within document
def grep_in_document(document_path, query_pair):
  # print ('Grep in document called with')
  # print (document_path)
  # print (query_pair)

  started = False
  startedAt = 0
  snippet = ''
  refsCurr = []

  queryStringStart = query_pair[0]
  queryStringEnd = query_pair[1]
  refString = '\\label{'

  results = []
  contexts = []
  refs = []
  # try:
    # print (document_path)
  lines = open(document_path, 'r').readlines()
  # except:
  #   return results, contexts, refs

  for i, line in enumerate(lines):
    if not started:
      if queryStringStart in line:
        started = True
        startedAt = i
        snippet = snippet + line

    if started:
      if refString in line:
        refsCurr.append(line.split(refString)[1].split('}')[0])

      if startedAt != i:
        snippet = snippet + line

      if queryStringEnd in line:
        started = False
        # snippet = snippet + line
        results = results + [snippet]
        print (len(results))
        pre = '\n'.join(lines[max(0, startedAt - 3) : min(startedAt, len(lines))])
        post = '\n'.join(lines[max(0, i + 1) : min(len(lines), i + 4)])
        contexts = contexts + [pre + '\n' + post]
        refs = refs + [refsCurr]

        snippet = ''
        refsCurr = []

  print (len(results))
  # print ('From document, returning: ' + str(results))
  return results, contexts, refs

# Get referencens to a label
def get_all_references(document_path, label):
  lines = open(document_path, 'r').readlines()

  refs = ''

  i = 0
  while i < len(lines):
    line = lines[i]

    if '\\ref{' + label + '}' in line:
      refs = refs + '\n'.join(lines[max(0, i - 5) : min(len(lines), i + 6)])
      i += 6
    else:
      i+= 1
  
  return refs

# Process a single document
def process_document(document_path, query_pair):
  # Get all equations, with context and labels
  results, contexts, labels = grep_in_document(document_path, query_pair)

  print (results)
  # Get all references with the tag and create dataset row and return
  l = len(results)

  data_points = []
  for i in range(l):
    row = []
    row.append(results[i])
    row.append(contexts[i])
    refs = ''
    for label in labels[i]:
      refs = refs + '\n' + get_all_references(document_path, label)

    row.append(refs)
    row.append(labels)
    data_points.append(row)
  
  return data_points

# Run over document set
def process_all(document_dir, output_file_path, query_pairs):
  file_list = [f for f in os.listdir(document_dir) if os.path.isfile(os.path.join(document_dir, f))]
  print (len(file_list))
  dataset = []
  error_count = 0
  count = 0

  for query_pair in query_pairs:
    pbar = ProgressBar()
    for f in pbar(file_list):
      count += 1
      
      # ######### FOR TESTING! REMOVE BEFORE RUNNING ###########
      # if count == 10:
      #   break
    
      try:
        rows = process_document(os.path.join(document_dir, f), query_pair)
        print ('Added: ' + str(len(rows)))
        # print (rows)
      except:
        error_count += 1
        continue
      dataset += rows
    
  # Create dataset and save to file
  dataset = pd.DataFrame(dataset, columns=['table', 'contexts', 'refs', 'labels'])
  dataset.to_csv(output_file_path)


####################################### Main Execution #######################################

# Scientific document path
document_source_path = '/home/cksash/Documents/data/readonly/unpacked'

# Output dataset path
output_dataset_path = ''

query_pairs = [
  ['\\begin{table}', '\\end{table}']
]

process_all(document_source_path, '~/Documents/data/tables.csv', query_pairs)