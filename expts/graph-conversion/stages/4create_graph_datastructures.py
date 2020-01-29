from stages.stage import Stage

import multiprocessing
import ast 
import pickle
import numpy as np
from progressbar import ProgressBar 

RELATION_NODE = 'relation'
VARIABLE_NODE = 'variable'
PARSE_NODE    = 'parse'

class GraphNode:

  def __init__(self, value, node_type, op_type=(-1, -1)):
    self.id = 0
    self.type = node_type
    self.op_type = op_type
    self.value = value
    self.neighbors = []
  
  def add_neighbors(self, new_neighbors):
    for n in new_neighbors:
      self.neighbors.append(n)

'''
Open DataFrame from CSV file.
Input: Path to CSV file
Output: DataFrame object containing data in CSV file
DONE: Intermidiate nodes and bracket encapsulation not considered
'''
class CreateGraphDatastructures(Stage):

  def __init__(self, configs):
    self.name = configs['name']
    self.output_file = configs['output_file']

  # IMPORTANT: Update any changes in node vector stage as well.

  ####################### Helper methods #####################

  def is_operator(self, token):
    character_operators = set(list('=^-+/_'))
    macro_operators = {
      'frac' : ['macro', 'frac', 0, 2, '({[', ']})'],
      'tanh' : ['macro', 'tanh', 0, 1, '({[', ']})'],
      'coth' : ['macro', 'coth', 0, 1, '({[', ']})'],
      'cosh' : ['macro', 'cosh', 0, 1, '({[', ']})'],
      'sinh' : ['macro', 'sinh', 0, 1, '({[', ']})'],
      'cos'  : ['macro', 'cos', 0, 1, '({[', ']})'],
      'sin'  : ['macro', 'sin', 0, 1, '({[', ']})'],
      'tan'  : ['macro', 'tan', 0, 1, '({[', ']})'],
      'cot'  : ['macro', 'cot', 0, 1, '({[', ']})'],
      'csc'  : ['macro', 'csc', 0, 1, '({[', ']})'],
      'sec'  : ['macro', 'sec', 0, 1, '({[', ']})']
    }

    if token[1] in character_operators or token[1] in macro_operators:
      return True
    else:
      return False

  def get_operator_type(self, token):
    character_operators = set(list('=^-+/_'))
    macro_operators = {
      'frac' : ['macro', 'frac', 0, 2, '({[', ']})'],
      'tanh' : ['macro', 'tanh', 0, 1, '({[', ']})'],
      'coth' : ['macro', 'coth', 0, 1, '({[', ']})'],
      'cosh' : ['macro', 'cosh', 0, 1, '({[', ']})'],
      'sinh' : ['macro', 'sinh', 0, 1, '({[', ']})'],
      'cos'  : ['macro', 'cos', 0, 1, '({[', ']})'],
      'sin'  : ['macro', 'sin', 0, 1, '({[', ']})'],
      'tan'  : ['macro', 'tan', 0, 1, '({[', ']})'],
      'cot'  : ['macro', 'cot', 0, 1, '({[', ']})'],
      'csc'  : ['macro', 'csc', 0, 1, '({[', ']})'],
      'sec'  : ['macro', 'sec', 0, 1, '({[', ']})']
    }

    if token[1] in character_operators:
      return ['character', token[1], 1, 1, '([{', '}])']
    
    if token[1] in macro_operators:
      return macro_operators[token[1]]

  def create_graph_node(self, token, node_type, op_type=(-1, -1)):
    return GraphNode(token, node_type, op_type)
  
  def get_node_classification(self, tokens):
    pool = multiprocessing.Pool(processes=8)
    is_operator = pool.map(self.is_operator, tokens)

    return is_operator
  
  def create_all_graph_nodes(self, tokens, is_operator):
    nodes = []
    for i, token in enumerate(tokens):
      if is_operator[i]:
        op_type = self.get_operator_type(tokens[i])
        nodes.append(self.create_graph_node(token, RELATION_NODE, op_type=(op_type[2], op_type[3])))
      else:
        nodes.append(self.create_graph_node(token, VARIABLE_NODE))
    
    return nodes
  
  def add_proximity_edges(self, nodes):
    for i in range(len(nodes)):
      # Add bidirectional edge
      if i > 0: 
        nodes[i - 1].neigbours.append(nodes[i])
        nodes[i].neigbours.append(nodes[i - 1])
    
    return nodes

  def get_brace_limits(self, tokens):
    braces_open = '{[('
    braces_close = '}])'
    brackets = []
    stack = []
    
    ## Identify the braces for intermediate nodes
    for i in range(len(tokens)):
      # Brace open node
      if tokens[i][1] in braces_open:
        stack.append([i, tokens[i][1]])
      
      # Brace close node
      if tokens[i][1] in braces_close:
        # TODO: Do we need the type of brace?
        brace_type_index = braces_close.index(tokens[i][1])
        start = brackets.pop()
        end = i

        # brackets.append((braces_open[brace_type_index], braces_close[brace_type_index], start, end))
        brackets.append((start, end))
    
    # TODO: Implements checks on whether stack is empty
    return brackets

  def add_intermediate_nodes(self, brackets, nodes):
    # Create the intermediate nodes
    intermediate_nodes = []
    for bracket in brackets:
      start = bracket[0]
      end = bracket[1]
      node_value = 'INT_' + str(start) + '_' + str(end)

      # Create the intermediate node
      new_node = GraphNode(['braces', node_value], PARSE_NODE)

      # Add all relations to this node
      for i in range(start, end + 1):
        # Add bidirectional edge from intermediate node to everything inside
        # TODO: Need to change this graph edge model
        new_node.neighbors.append(nodes[i])
        nodes[i].neigbours.append(new_node)
      
      # Store reference to the newly added intermediate node
      intermediate_nodes.append(new_node)

      nodes.insert(start, new_node)
    
    return intermediate_nodes, nodes

  def add_relation_edges(self, nodes):

    for i, node in enumerate(nodes):
      if nodes[i].type == RELATION_NODE:
        before_neighbors = nodes[i].op_type[0]
        after_neighbors = nodes[i].op_type[1]

        if before_neighbors > 0 and (i - before_neighbors) >= 0:
          # Add relation edge from node to each previous 
          for k in range(i - before_neighbors, i):
            nodes[k].neigbors.append(i)
            nodes[i].neigbors.append(i)
        
        if after_neighbors > 0 and (i + after_neighbors) < len(nodes):
          # Add relation edge from node to each after 
          for k in range(i + 1, i + after_neighbors):
            nodes[i].neigbors.append(i)
            nodes[k].neigbors.append(i)
        
    return nodes
  
  def get_adjlist_from_nodes(self, nodes):
    # Create empty ds
    adjlist = {}
    for i, node in enumerate(nodes):
      node.id = i
      adjlist[node.id] = []
    
    # Add all neighbors of node in adjlist
    for i, node in enumerate(nodes):
      for n in node.neigbors:
        adjlist[node.id].append(n.id)
    
    return adjlist
  
  def get_adjmatrix_from_nodes(self, nodes):
    # Create empty ds
    adjmatrix = np.zeros([nodes.length, nodes.length])
    
    # Add all neighbors of node in adjlist
    for node in nodes:
      for n in node.neigbors:
        adjmatrix[node.id][n.id] = 1
    
    return adjmatrix
  

  def get_graph_ds_from_nodes(self, nodes):
    # Get adjmatrix
    adjmatrix = self.get_adjmatrix_from_nodes(nodes)
    # Get adjlist
    adjlist = self.get_adjlist_from_nodes(nodes)

    return adjmatrix, adjlist, nodes


  ####################### Main methods #####################

  def _get_graph_from_tokenized_equation(self, tokens):
    # Classify tokens as operator and variable nodes
    is_operator = self.get_node_classification(tokens)

    # Create nodes for each token
    nodes = self.create_all_graph_nodes(tokens, is_operator)

    # Add all proximity edge
    nodes = self.add_proximity_edges(nodes)

    # Create the intermediate nodes

    ## Use braces to identify sub-parts of equations and represent using intermediate state nodes
    brackets = self.get_brace_limits(tokens)
    
    # Create the intermediate nodes - ALL NODES ARE IN nodes - intermediate is not necessary
    intermediate_nodes, nodes = self.add_intermediate_nodes(brackets, nodes)

    # Add relation edges
    nodes = self.add_relation_edges(nodes)

    # Get the adjlist and adjmatrix from this
    adjmatrix, adjlist, nodes = self.get_graph_ds_from_nodes(nodes)

    return adjmatrix, adjlist, nodes
    
  # Main: Convert equations into graph
  def get_graph_from_tokenized_equation(self, equations):
    # Get graph ds corresponding to each equation
    adjmatrices = []
    adjlists = []
    node_lists = []

    error_ctr = 0
    # pbar = ProgressBar()
    for equation in equations:
      try:
        adjmatrix, adjlist, nodes = self._get_graph_from_tokenized_equation(equation)
      except Exception as e:
        error_ctr += 1
        print ('Error: ' + str(error_ctr))
        print (e)
      
      adjmatrices.append(adjmatrix)
      adjlists.append(adjlist)
      node_lists.append(nodes)
    
    # Save all graph ds to file
    fptr = open('./outputs/pickles/adjmatrices.pkl', 'wb')
    pickle.dump(adjmatrices, fptr)

    fptr = open('./outputs/pickles/adjlists.pkl', 'wb')
    pickle.dump(adjlists, fptr)

    return adjlists, adjmatrices, node_lists

  def write_adj_list_to_file(self, equations):
    # Read all adjacency lists
    fptr = open('./outputs/pickles/adjlists.pkl', 'rb')
    adj_lists = pickle.load(fptr)
    fptr.close()
    
    # Write in text form
    for i in range(len(adj_lists)):
      with open('./outputs/adj_lists/adj_list_' + str(i) + '.txt', 'w') as file:
        file.write(str(adj_lists[i]))
    
    return 0
  
  def process_all_equations(self, equations):
    return self.get_graph_from_tokenized_equation(equations)

  def run(self, df):
    equations = df['equation']
    adjlists, adjmatrices, node_lists = self.process_all_equations(equations)
    self.write_adj_list_to_file(equations)
    return node_lists