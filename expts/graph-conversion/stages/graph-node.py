class GraphNode:

  def __init__(self, value, node_type):
    self.type = node_type
    self.value = value
    self.neighbors = []
  
  def add_neighbors(self, new_neighbors):
    for n in new_neighbors:
      self.neighbors.append(n)