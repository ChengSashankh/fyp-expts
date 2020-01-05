from stages.stage import Stage
from stages.graph-node import GraphNode

import multiprocessing
import ast 
import pickle
from progressbar import ProgressBar 

RELATION_NODE = 'relation'
VARIABLE_NODE = 'variable'
PARSE_NODE    = 'parse'

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

  def from_string_to_array(self, equation):
    return ast.literal_eval(equation) 
  
  def from_string_to_array_wrapper(self, equations):
    pool = multiprocessing.Pool(processes=8)
    equations = pool.map(self.from_string_to_array, equations)

    return equations
  
  def is_operator(self, token):
    character_operators = set(list('=^-+/_'))
    macro_operators = {
      'frac' : ['frac', 2, '({[', ']})'],
      'tanh' : ['tanh', 1, '({[', ']})'],
      'coth' : ['coth', 1, '({[', ']})'],
      'cosh' : ['cosh', 1, '({[', ']})'],
      'sinh' : ['sinh', 1, '({[', ']})'],
      'cos'  : ['cos', 1, '({[', ']})'],
      'sin'  : ['sin', 1, '({[', ']})'],
      'tan'  : ['tan', 1, '({[', ']})'],
      'cot'  : ['cot', 1, '({[', ']})'],
      'csc'  : ['csc', 1, '({[', ']})'],
      'sec'  : ['sec', 1, '({[', ']})']
    }

    if token[1] in character_operators or token[1] in macro_operators:
      return True
    else:
      return False

  def get_operator_type(self, token):
    character_operators = set(list('=^-+/_'))
    macro_operators = {
      'frac' : ['macro', 'frac', 2, '({[', ']})'],
      'tanh' : ['macro', 'tanh', 1, '({[', ']})'],
      'coth' : ['macro', 'coth', 1, '({[', ']})'],
      'cosh' : ['macro', 'cosh', 1, '({[', ']})'],
      'sinh' : ['macro', 'sinh', 1, '({[', ']})'],
      'cos'  : ['macro', 'cos', 1, '({[', ']})'],
      'sin'  : ['macro', 'sin', 1, '({[', ']})'],
      'tan'  : ['macro', 'tan', 1, '({[', ']})'],
      'cot'  : ['macro', 'cot', 1, '({[', ']})'],
      'csc'  : ['macro', 'csc', 1, '({[', ']})'],
      'sec'  : ['macro', 'sec', 1, '({[', ']})']
    }

    if token[1] in character_operators:
      return ['character', token[1], 2, '([{', '}])']
    
    if token[1] in macro_operators:
      return macro_operators[token[1]]

  def create_graph_node(self, token, node_type):
    return GraphNode(token, node_type)

  # Rewriting old graph creation code properly
  def get_graph_from_tokenized_equation(self, tokens):
    # Classify tokens as operator and variable nodes
    pool = multiprocessing.Pool(processes=8)
    is_operator = pool.map(self.is_operator, tokens)

    # Create nodes for each token
    nodes = []
    for i, token in enumerate(tokens):
      if is_operator[i]:
        nodes.append(self.create_graph_node(token, RELATION_NODE))
      else:
        nodes.append(self.create_graph_node(token, VARIABLE_NODE))
    
    # Add all proximity edge
    for i in range(len(nodes)):
      # Add bidirectional edge
      if i > 0: 
        nodes[i - 1].neigbours.append(nodes[i])
        nodes[i].neigbours.append(nodes[i - 1])

    # Create the intermediate nodes

    ## Use braces to identify sub-parts of equations and represent using intermediate state nodes
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
        brace_type_index = braces_close.index(tokens[i][1])
        start = brackets.pop()
        end = i

        # brackets.append((braces_open[brace_type_index], braces_close[brace_type_index], start, end))
        brackets.append((start, end))
    
    # Create the intermediate nodes
    intermediate_nodes = []
    for brace in brackets:
      intermediate_nodes.append()
                                 
  
  def tokens_to_graph(self, tokens):
    # Classify tokens as operator/relation and variable nodes
    # pool = multiprocessing.Pool(processes=8)
    # are_operators = pool.map(self.is_operator, tokens)

    is_operator = []
    for token in tokens:
      is_operator.append(self.is_operator(token))

    operators = [tokens[i] for i in range(len(tokens)) if is_operator[i]]
    variables = [tokens[i] for i in range(len(tokens)) if not is_operator[i]]

    # Create the Graph Nodes
    
    # pool = multiprocessing.Pool(processes=8)
    # operator_nodes = pool.map(self.create_relation_node, operators)

    operator_nodes = []
    for operator in operators:
      operator_nodes.append(self.create_relation_node(operator))

    # pool = multiprocessing.Pool(processes=8)
    # variable_nodes = pool.map(self.create_variable_node, variables)

    variable_nodes = []
    for variable in variables:
      variable_nodes.append(self.create_variable_node(variable))

    parse_nodes = []

    # Initialize adjacency list
    # adj_list will contain integer pairs (neighbour_node, edge_type)
    PROXIMITY_EDGE = 0
    OPERATOR_EDGE = 1
    PARSE_EDGE = 2

    token2node = {}
    adj_list = {} 
    node_id = {}
    id_ctr = 1

    for i, o in enumerate(operator_nodes):
      token2node[tuple(operators[i])] = operator_nodes[i]
      node_id[o] = id_ctr
      id_ctr += 1
      adj_list[o] = []
    
    for i, v in enumerate(variable_nodes):
      token2node[tuple(variables[i])] = variable_nodes[i]
      node_id[v] = id_ctr
      id_ctr += 1
      adj_list[v] = []
    
    # Populate adjacency list
    ## (Proximity Edges) Connect all adjacent variables
    prev = -1
    for i in range(len(tokens)):
      # On finding variable
      if not self.is_operator(tokens[i]):
        if prev < 0:
          # If this is the first variable
          prev = i
        else: 
          # If this is not the first variable, add bidirectional proximity edges in the equation graph
          adj_list[token2node.get(tuple(tokens[prev]))].append([token2node.get(tuple(tokens[i])), PROXIMITY_EDGE])
          adj_list[token2node.get(tuple(tokens[i]))].append([token2node.get(tuple(tokens[prev])), PROXIMITY_EDGE])

    ## (Operator-Variable Edges) Add all variables for each operator

    ### Use braces to identify sub-parts of equations and represent using intermediate state nodes
    braces_open = '{[('
    braces_close = '}])'
    stack = []

    compressed_equation = []
    for i in range(len(tokens)):
      # Brace open node
      if tokens[i][1] in braces_open:
        stack.append([i, tokens[i][1]])

      # Brace close node
      elif tokens[i][1] in braces_close:
        brace = stack[len(stack) - 1]
        if braces_close.index(tokens[i][1]) == braces_open.index(brace[1]):
          # Create parse node
          parse_node = GraphNode(
             'PARSE[' + str(brace[0]) + '-' + str(i) + ']',
             PARSE_NODE,
             'PARSE')
          
          parse_nodes.append(parse_node)

          compressed_equation.append(parse_node)
          
          node_id[parse_node] = id_ctr
          parse_node_token = ['PARSE' + str(id_ctr), 'PARSE'  + str(id_ctr)]
          id_ctr += 1

          
          # Add to adjacency list
          adj_list[parse_node] = []
          
          # Add edges from parse node to all containing nodes
          start = brace[0]
          end = i
          for i in range(start, end + 1):
            # Add bidirectional nodes
            adj_list[parse_node].append([token2node.get(tuple(tokens[i])), PARSE_EDGE])
            adj_list[token2node.get(tuple(tokens[i]))].append([parse_node, PARSE_EDGE])

          # Remove the opening bracket
          stack.pop()
        else:
          print (stack)
          raise Exception('Braces don\'t match')
      
      # All other nodes
      else:
        compressed_equation.append(tokens[i])

    # Adding relations on the adjacency list
    for i in range(len(compressed_equation)):
      # On finding operator
      if self.is_operator(tokens[i]):
        if i - 1 >= 0:
          adj_list[token2node.get(tuple(tokens[i - 1]))].append([token2node.get(tuple(tokens[i])), OPERATOR_EDGE])
          adj_list[token2node.get(tuple(tokens[i]))].append([token2node.get(tuple(tokens[i - 1])), OPERATOR_EDGE])
        
        if i + 1 <= len(tokens):
          adj_list[token2node.get(tuple(tokens[i + 1]))].append([token2node.get(tuple(tokens[i])), OPERATOR_EDGE])
          adj_list[token2node.get(tuple(tokens[i]))].append([token2node.get(tuple(tokens[i + 1])), OPERATOR_EDGE])
    
    # We are now done. We return all the Graph data structures needed.
    return adj_list, token2node, compressed_equation

  # Main: Convert equations into graph
  def turn_equations_into_graph(self, equations):
    # Get array form of tokenized equations from strings
    equations = self.from_string_to_array_wrapper(equations)

    # Get graph ds corresponding to each equation
    adj_matrix = []
    adj_lists = []
    token2nodes = []
    compressed_equations = []

    error_ctr = 0
    # pbar = ProgressBar()
    for equation in equations:
      try:
        adj_list, token2node, compressed_equation = self.tokens_to_graph(equation)
      except Exception as e:
        error_ctr += 1
        print ('Error: ' + str(error_ctr))
        print (e)
      
      adj_lists.append(adj_list)
      token2nodes.append(token2node)
      compressed_equations.append(compressed_equation)
    
    # Save graph ds for each to file
    for i in range(len(equations)):
      fptr = open('./outputs/pickles/adj_list_' + str(i) + '.pkl', 'wb')
      pickle.dump(adj_lists[i], fptr)
      fptr.close()

      fptr = open('./outputs/pickles/token2node_' + str(i) + '.pkl', 'wb')
      pickle.dump(token2nodes[i], fptr)
      fptr.close()
      
      fptr = open('./outputs/pickles/compressed_equation_' + str(i) + '.pkl', 'wb')     
      pickle.dump(compressed_equations[i], fptr)
      fptr.close()

    return 0
  
  def write_adj_list_to_file(self, equations):
    # Read all adjacency list pickles
    adj_lists = []
    for i in range(len(equations)):
      fptr = open('./outputs/pickles/adj_list_' + str(i) + '.pkl', 'rb')
      adj_lists.append(pickle.load(fptr))
      fptr.close()
    
    # Write in text form
    for i in range(len(equations)):
      with open('./outputs/adj_lists/adj_list_' + str(i) + '.txt', 'w') as file:
        ctr = 1
        node2num = {}
        for key in adj_lists[i]:
          node2num[key] = ctr
          ctr += 1
        
        for key in adj_lists[i]:
          line = str(node2num.get(key))

          for n in adj_lists[i][key]:
            line = line + ' ' + str(node2num.get(n[0]))
          
          line = line + '\n'
          file.write(line)
    
    return 0
  
  def process_all_equations(self, equations):
    self.turn_equations_into_graph(equations)

  def run(self, df):
    equations = df['equation']
    self.process_all_equations(equations)
    self.write_adj_list_to_file(equations)
    return './outputs/pickles/'