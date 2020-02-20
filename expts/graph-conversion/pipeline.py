from data_paths import DataPaths

from stages.load_df_from_csv import LoadDFFromCSV
from stages.string_to_array import String2Array
from stages.tokenize_equations import EquationTokenizationStage
from stages.store_node_labels import StoreNodeLabels
from stages.create_graph_datastructures import CreateGraphDatastructures
from stages.get_node_vectors import GetNodeVectors

import json

class Pipeline:

  def __init__(self, name, logfile, ip):
    self.name = name

    # Create log file
    self.logfile = open(logfile, 'w')

    # Get data paths
    # self.data_paths = DataPaths(colab_mode = False)

    # Get run configurations
    run_config_file = open('run_configs_graph_conversion.json', 'r')
    self.run_configs = json.load(run_config_file)
  
  def get_stage_from_name(self, configs):
    if configs['name'] == 'create_graph_datastructures':
      return CreateGraphDatastructures(configs)

    if configs['name'] == 'load_df_from_csv':
      return LoadDFFromCSV(configs)

    if configs['name'] == 'string_to_array':
      return String2Array(configs)

    if configs['name'] == 'tokenize_equations':
      return EquationTokenizationStage(configs)
    
    if configs['name'] == 'store_node_labels':
      return StoreNodeLabels(configs)

    if configs['name'] == 'get_node_vectors':
      return GetNodeVectors(configs)

  def create_pipeline_from_configs(self):
    self.stages = []
    for cfg in self.run_configs['stage_configs']:
      self.stages.append(self.get_stage_from_name(cfg))
  
  def run(self):
    self.create_pipeline_from_configs()
    print ('At run stage')
    print (self.stages)

    # op = './test_df.csv'
    op = '/Users/cksash/data/fyp/kdd/equations.csv'
    for stage in self.stages:
      print ('Running stage: ' + str(stage.name))
      op = stage.run(op)
    

pipeline = Pipeline('data_creating_baseline1', './outputs/logfile.txt', '')
pipeline.run()