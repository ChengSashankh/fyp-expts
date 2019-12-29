import os

class DataPaths:

  def __init__(self, colab_mode):
    self.colab = colab_mode

    self.path_root = '~/Documents/data'

    self.pickles_path = os.path.join(self.path_root, 'baseline1/pickles')
    self.checkpoints_path = os.path.join(self.path_root, 'baseline1/checkpoints') 
    self.training_log_path = os.path.join(self.path_root, 'baseline1/training_log_path')
