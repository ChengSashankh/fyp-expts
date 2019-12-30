from data_paths import DataPaths

from stages.anonymize_equations_in_dataframe import AnonymizeEquations
from stages.create_seq2seq_datastructures import CreateSeq2SeqDataStructures
from stages.df_to_file import DFToFile
from stages.equation_tokenization_stage import EquationTokenizationStage
from stages.filter_entries_in_df import FilterGrepEntries
from stages.grep_stage import GrepInDocuments
from stages.linguistic_preprocess import LinguisticPreprocessing
from stages.create_graph_datastructures import CreateGraphDatastructures
from stages.load_df_from_csv import LoadDFFromCSV

import json

class Pipeline:

  def __init__(self, name, logfile, ip):
    self.name = name

    # Create log file
    self.logfile = open(logfile, 'w')

    # Get data paths
    # self.data_paths = DataPaths(colab_mode = False)

    # Get run configurations
    run_config_file = open('run_configs_data.json', 'r')
    self.run_configs = json.load(run_config_file)
  
  def get_stage_from_name(self, configs):
    if configs['name'] == 'anonymize_equations_in_dataframe': 
      return AnonymizeEquations(configs)
    
    if configs['name'] == 'create_seq2seq_datastructures': 
      return CreateSeq2SeqDataStructures(configs)
    
    if configs['name'] == 'df_to_file': 
      return DFToFile(configs)
  
    if configs['name'] == 'equation_tokenization_stage': 
      return EquationTokenizationStage(configs)
  
    if configs['name'] == 'filter_entries_in_df': 
      return FilterGrepEntries(configs)

    if configs['name'] == 'grep_stage': 
      return GrepInDocuments(configs)

    if configs['name'] == 'linguistic_preprocess': 
      return LinguisticPreprocessing(configs)

    if configs['name'] == 'create_graph_datastructures':
      return CreateGraphDatastructures(configs)

    if configs['name'] == 'load_df_from_csv':
      return LoadDFFromCSV(configs)
    
    # name2stage = {
    #   'anonymize_equations_in_dataframe' : AnonymizeEquations(configs),
    #   'create_seq2seq_datastructures' : CreateSeq2SeqDataStructures(configs),
    #   'df_to_file' : DFToFile(configs),
    #   'equation_tokenization_stage' : EquationTokenizationStage(configs),
    #   'filter_entries_in_df' : FilterGrepEntries(configs),
    #   'grep_stage' : GrepInDocuments(configs),
    #   'linguistic_preprocess' : LinguisticPreprocessing(configs)
    # }

    # return name2stage.get(configs.name)

  def create_pipeline_from_configs(self):
    self.stages = []
    for cfg in self.run_configs['stage_configs']:
      self.stages.append(self.get_stage_from_name(cfg))
  
  def run(self):
    self.create_pipeline_from_configs()
    print ('At run stage')
    print (self.stages)

    op = ''
    for stage in self.stages:
      # op = stage.run(op)
      print ('Running stage: ' + str(stage.name))
    

pipeline = Pipeline('data_creating_baseline1', './outputs/logfile.txt', '')
pipeline.run()