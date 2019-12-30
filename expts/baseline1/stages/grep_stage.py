from stages.stage import Stage

import os
import pandas as pd
from progressbar import ProgressBar

'''
Read documents and create the grep results along with context 
and matches 
Input: Document path
Output: Grep results in pandas.DataFrame with headers as ['match', 'context', 'labels']
'''
class GrepInDocuments(Stage):
  def __init__(self, configs):
    self.name = configs['name']
    self.documents_source_dir = configs['documents_source_dir']
    self.start_patterns = configs['start_patterns']
    self.end_patterns = configs['end_patterns']
    self.context_size_before = configs['context_size_before']
    self.context_size_after = configs['context_size_after']
    self.ref_string = configs['ref_string']
  
  # Search within document
  def grep_in_document(self, document_path, start_pattern, end_pattern):

    started = False
    startedAt = 0
    snippet = ''
    labels = []
    
    refString = self.ref_string

    results = []
    contexts = []
    refs = []

    try:
      lines = open(document_path, 'r').readlines()
    except:
      return results, contexts, refs

    for i, line in enumerate(lines):
      if not started:
        if start_pattern in line:
          started = True
          startedAt = i
          snippet = snippet + line

      if started:
        if refString in line:
          labels.append(line.split(refString)[1].split('}')[0])

        if startedAt != i:
          snippet = snippet + line

        if end_pattern in line:
          started = False
          # snippet = snippet + line
          results = results + [snippet]
          print (len(results))
          pre = '\n'.join(lines[max(0, startedAt - self.context_size_before) : min(startedAt, len(lines))])
          post = '\n'.join(lines[max(0, i + 1) : min(len(lines), i + self.context_size_after + 1)])
          contexts = contexts + [pre + '\n' + post]
          refs = refs + [labels]

          snippet = ''
          labels = []

    print (len(results))
    return results, contexts, refs
  
  # Get referencens to a label
  def get_all_references(self, document_path, label):
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

  # Process a single document and return all data points from document
  def process_document(self, document_path):
    # Get all equations, with context and labels
    results = []
    contexts = []
    labels = []

    for i in range(len(self.start_patterns)):
      r, c, l = self.grep_in_document(document_path, self.start_patterns[i], self.end_patterns[i])
      results = results + r
      contexts = contexts + c
      labels = labels + l

    # Get all references with the tag and create dataset row and return
    l = len(results)
    print ('#Results collected: ' + str(l))

    data_points = []
    for i in range(l):
      row = []
      row.append(results[i])
      row.append(contexts[i])
      refs = ''
      for label in labels[i]:
        refs = refs + '\n' + self.get_all_references(document_path, label)

      row.append(refs)
      row.append(labels)
      data_points.append(row)
    
    return data_points

  # Run over document set
  def process_all(self):
    file_list = [f for f in os.listdir(self.documents_source_dir) if os.path.isfile(os.path.join(self.documents_source_dir, f))]
    print ('Number of files to process : ' + str(len(file_list)))
    
    dataset = []
    error_count = 0
    count = 0

    pbar = ProgressBar()
    for f in pbar(file_list):
      count += 1
      
      # ######### FOR TESTING! REMOVE BEFORE RUNNING ###########
      # if count == 10:
      #   break
    
      try:
        rows = process_document(self, os.path.join(document_dir, f))
        print ('Added: ' + str(len(rows)))
        # print (rows)
      except:
        error_count += 1
        continue
      dataset += rows
      
    # Create dataset and save to file
    dataset = pd.DataFrame(dataset, columns=['equation', 'context', 'reference', 'labels'])
    return dataset

  def run(self, ip):
    return self.process_all()