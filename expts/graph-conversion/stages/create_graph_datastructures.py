from stages.stage import Stage

import multiprocessing
import ast
import pickle
import numpy as np
from progressbar import ProgressBar
from numpy.testing import assert_array_equal
import scipy.sparse as sp

RELATION_NODE = 'relation'
VARIABLE_NODE = 'variable'
PARSE_NODE = 'parse'


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
            'frac': ['macro', 'frac', 0, 2, '({[', ']})'],
            'tanh': ['macro', 'tanh', 0, 1, '({[', ']})'],
            'coth': ['macro', 'coth', 0, 1, '({[', ']})'],
            'cosh': ['macro', 'cosh', 0, 1, '({[', ']})'],
            'sinh': ['macro', 'sinh', 0, 1, '({[', ']})'],
            'cos': ['macro', 'cos', 0, 1, '({[', ']})'],
            'sin': ['macro', 'sin', 0, 1, '({[', ']})'],
            'tan': ['macro', 'tan', 0, 1, '({[', ']})'],
            'cot': ['macro', 'cot', 0, 1, '({[', ']})'],
            'csc': ['macro', 'csc', 0, 1, '({[', ']})'],
            'sec': ['macro', 'sec', 0, 1, '({[', ']})']
        }

        if token[1] in character_operators or token[1] in macro_operators:
            return True
        else:
            return False

    def get_operator_type(self, token):
        character_operators = set(list('=^-+/_'))
        macro_operators = {
            'frac': ['macro', 'frac', 0, 2, '({[', ']})'],
            'tanh': ['macro', 'tanh', 0, 1, '({[', ']})'],
            'coth': ['macro', 'coth', 0, 1, '({[', ']})'],
            'cosh': ['macro', 'cosh', 0, 1, '({[', ']})'],
            'sinh': ['macro', 'sinh', 0, 1, '({[', ']})'],
            'cos': ['macro', 'cos', 0, 1, '({[', ']})'],
            'sin': ['macro', 'sin', 0, 1, '({[', ']})'],
            'tan': ['macro', 'tan', 0, 1, '({[', ']})'],
            'cot': ['macro', 'cot', 0, 1, '({[', ']})'],
            'csc': ['macro', 'csc', 0, 1, '({[', ']})'],
            'sec': ['macro', 'sec', 0, 1, '({[', ']})']
        }

        if token[1] in character_operators:
            return ['character', token[1], 1, 1, '([{', '}])']

        if token[1] in macro_operators:
            return macro_operators[token[1]]

    def create_graph_node(self, token, node_type, op_type=(-1, -1)):
        return GraphNode(token, node_type, op_type)

    def get_node_classification(self, tokens):
        # pool = multiprocessing.Pool(processes=8)
        # is_operator = pool.map(self.is_operator, tokens)
        # return is_operator

        operator = []
        for token in tokens:
            operator.append(self.is_operator(token))

        return operator

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
                nodes[i - 1].neighbors.append(nodes[i])
                nodes[i].neighbors.append(nodes[i - 1])

        return nodes

    def get_brace_limits(self, tokens):
        braces_open = '{[('
        braces_close = '}])'
        brackets = []
        stack = []

        ## Identify the braces for intermediate nodes
        for i in range(len(tokens)):
            # Brace open node
            if tokens[i][0] == 'brace_open':
                stack.append(i)

            # Brace close node
            if tokens[i][0] == 'brace_close' and len(stack) != 0:
                # TODO: Do we need the type of brace?
                brace_type_index = braces_close.index(tokens[i][1])
                # if len(stack) == 0:
                #     print (tokens)
                #     print (tokens[i])
                #     print (i)
                start = stack.pop()
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
                nodes[i].neighbors.append(new_node)

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
                        nodes[k].neighbors.append(nodes[i])
                        nodes[i].neighbors.append(nodes[k])

                if after_neighbors > 0 and (i + after_neighbors) < len(nodes):
                    # Add relation edge from node to each after
                    for k in range(i + 1, i + after_neighbors):
                        nodes[i].neighbors.append(nodes[k])
                        nodes[k].neighbors.append(nodes[i])

        return nodes

    def get_adjlist_from_nodes(self, nodes):
        # Create empty ds
        adjlist = {}
        for i, node in enumerate(nodes):
            node.id = i
            adjlist[node.id] = []

        # Add all neighbors of node in adjlist
        for i, node in enumerate(nodes):
            for n in node.neighbors:
                adjlist[node.id].append(n.id)

        return adjlist

    def get_adjmatrix_from_nodes(self, nodes):
        # Create empty ds
        adjmatrix = np.zeros([len(nodes), len(nodes)])
        adjmatrix_sp = sp.dok_matrix((len(nodes), len(nodes)), dtype=np.int8)

        # Add all neighbors of node in adjlist
        for node in nodes:
            for n in node.neighbors:
                adjmatrix[node.id][n.id] = 1
                adjmatrix_sp[node.id][n.id] = 1

        return adjmatrix, adjmatrix_sp

    def get_graph_ds_from_nodes(self, nodes):
        # Get adjmatrix
        adjmatrix, adjmatrix_sp = self.get_adjmatrix_from_nodes(nodes)
        # Get adjlist
        adjlist = self.get_adjlist_from_nodes(nodes)

        return adjmatrix, adjmatrix_sp, adjlist, nodes

    ####################### Main methods #####################

    def _get_graph_from_tokenized_equation(self, tokens):
        # Classify tokens as operator and variable nodes
        is_operator = self.get_node_classification(tokens)

        # Create nodes for each token
        nodes = self.create_all_graph_nodes(tokens, is_operator)

        # Add all proximity edge
        nodes = self.add_proximity_edges(nodes)

        # Create the intermediate nodes

        # Use braces to identify sub-parts of equations and represent using intermediate state nodes
        brackets = self.get_brace_limits(tokens)

        # Create the intermediate nodes - ALL NODES ARE IN nodes - intermediate is not necessary
        intermediate_nodes, nodes = self.add_intermediate_nodes(brackets, nodes)

        # Add relation edges
        nodes = self.add_relation_edges(nodes)

        # Get the adjlist and adjmatrix from this
        adjmatrix, adjmatrix_sp, adjlist, nodes = self.get_graph_ds_from_nodes(nodes)

        return adjmatrix, adjmatrix_sp, adjlist, nodes

    # Main: Convert equations into graph
    def get_graph_from_tokenized_equation(self, equations):
        # Get graph ds corresponding to each equation
        adjmatrices = []
        adjlists = []
        node_lists = []

        error_ctr = 0
        pbar = ProgressBar()
        for equation in pbar(equations):
            # try:
            adjmatrix, adjmatrix_sp, adjlist, nodes = self._get_graph_from_tokenized_equation(equation)

            # Append
            adjmatrices.append(adjmatrix)
            adjlists.append(adjlist)
            node_lists.append(nodes)
        # except Exception as e:
        #   error_ctr += 1
        #   print ('Error: ' + str(error_ctr))
        #   print (e)

        # Save all graph ds to file
        # 1. Save adjmatrix
        # Write separately - not needed for now
        fptr = open('/Users/cksash/data/fyp/kdd/adjmatrices.pkl', 'wb')
        pickle.dump(adjmatrices, fptr)

        # Merge and write - more useful now
        total_nodes = sum([len(n) for n in node_lists])
        # adj_matrix_merged = np.zeros([total_nodes, total_nodes])
        adj_matrix_merged_sp = sp.dok_matrix((total_nodes, total_nodes), dtype=np.int8)
        print (adj_matrix_merged_sp.shape)

        sizes = [len(n) for n in node_lists]
        graph_number = []
        for idx, i in enumerate(sizes):
            for j in range(i):
                graph_number.append(idx + 1)

        curr_idx = 0
        for adj_matrix in adjmatrices:
            # Check whether its square as expected
            assert(adj_matrix.shape[0] == adj_matrix.shape[1])

            size = adj_matrix.shape[0]
            print(adj_matrix.shape)

            # adj_matrix_merged[curr_idx: curr_idx + size, curr_idx: curr_idx + size] = adj_matrix

            # Merge into sparse matrix instead
            for i in range(size):
                for j in range(size):
                    if adj_matrix[i][j] != 0:
                        adj_matrix_merged_sp[curr_idx + i, curr_idx + j] = adj_matrix[i][j]

            # Check whether the assignment is correctly done
            # assert_array_equal(adj_matrix_merged[curr_idx: curr_idx + size, curr_idx: curr_idx + size], adj_matrix)

            curr_idx = curr_idx + size

        # Check whether loop terminated correctly
        assert(curr_idx == total_nodes)
        adj_matrix_merged_sp = adj_matrix_merged_sp.tocsr()

        print("Shape of merged adjmatrix: " + str(adj_matrix_merged_sp.shape))

        fptr = open('/Users/cksash/data/fyp/kdd/joined_adjmatrix.pkl', 'wb')
        pickle.dump(adj_matrix_merged_sp, fptr)

        fptr = open('/Users/cksash/data/fyp/kdd/EQUATIONS_A.txt', 'w')
        fptr.write(str(adj_matrix_merged_sp))

        # 2. adjlist - but i dont need this now
        fptr = open('/Users/cksash/data/fyp/kdd/adjlists.pkl', 'wb')
        pickle.dump(adjlists, fptr)

        # Save the graph numbers too
        fptr = open('/Users/cksash/data/fyp/kdd/graph_number.pkl', 'wb')
        pickle.dump(graph_number, fptr)

        fptr = open('/Users/cksash/data/fyp/kdd/EQUATIONS_graph_indicator.txt', 'w')
        for n in graph_number:
            fptr.write(str(n) + '\n')

        return adjlists, adjmatrices, node_lists

    def write_adj_list_to_file(self, equations):
        # Read all adjacency lists
        fptr = open('/Users/cksash/data/fyp/kdd/adjlists.pkl', 'rb')
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
        # self.write_adj_list_to_file(equations)

        return_dict = {'df': df, 'node_lists': node_lists}

        return return_dict
