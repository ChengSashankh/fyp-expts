from stages.stage import Stage

import pandas as pd
import numpy as np
import pickle

'''
Save dataframe to file
Input: Grep results in pandas.DataFrame with headers as ['match', 'context']
Output: Grep results in pandas.DataFrame with headers as ['match', 'context']
'''


class GetNodeVectors(Stage):
    def __init__(self, configs):
        self.name = configs['name']
        self.vector_dim = 10

    # TODO: replicate the implementation in create graph DS stage.
    # IMPORTANT: Update any changes in create graph DS stage as well.
    def get_node_type_sub_vec(self, token):
        return 1

    def get_token_text_formatting_sub_vec(self, token):
        text = token[1]
        text = ''
        basic_operators = list('+/*^_-')

        numeric_bit = 1 if text.isnumeric() else 0
        alphabetic_bit = 1 if text.isalpha() else 0
        operator_bit = 1 if text in basic_operators else 0
        capitalized_bit = 1 if (text.isalpha() and text.isupper()) else 0

        sub_vec = [numeric_bit, alphabetic_bit, operator_bit, capitalized_bit]

        return sub_vec

    # DONE: Verify token tag index and string literals
    def get_token_tag_sub_vec(self, token):
        tag = token[0]

        char_bit = 1 if tag == 'char' else 0
        macro_bit = 1 if tag == 'macro' else 0
        brace_open_bit = 1 if tag == 'brace_open' else 0
        brace_close_bit = 1 if tag == 'brace_close' else 0
        begin_environment_bit = 1 if tag == 'begin_environment' else 0
        end_environment_bit = 1 if tag == 'end_environment' else 0

        sub_vector = [char_bit, macro_bit, brace_open_bit, brace_close_bit, begin_environment_bit, end_environment_bit]

        return sub_vector

    # TODO: Only part of vector implemented. Implement the rest
    def get_features_from_token(self, token):
        # Vector format
        # TODO: Complete this
        # vec = [operator_node, variable_node, intermediate_node, char, macro, brace_open, brace_close, begin_environment, end_environment, capitalized, formatting_only, eqn_array_env, equation_env]
        node_vector = self.get_token_tag_sub_vec(token) + self.get_token_text_formatting_sub_vec(token)
        return node_vector

    def write_node_vectors_to_file(self, vectors):
        pickle.dump(vectors, open('/Users/cksash/data/fyp/kdd/node_vectors_joined.pkl', 'wb'))
        # Muted since its not possible to save 3D array as text file
        # np.savetxt('./outputs/node_vectors.txt', vectors)

    # TODO: Enforce max number of tokens in equation
    def run(self, node_lists):
        # tokenized_equations = df['equation']
        # All additional data structures needed for this stage will be input in this manner from an object if needed

        # num_equations = df.shape[0]
        # max_tokens_in_eqn = 100
        # node_vec_dimension = 10

        all_equations_vectors = []

        total_len = sum([len(n) for n in node_lists])

        # max_len = 0
        # for node_list in node_lists:
        #   max_len = max(max_len, len(node_list))

        all_equations_vectors = np.zeros([total_len, self.vector_dim])

        count = 0
        for i, nodes in enumerate(node_lists):
            for j, node in enumerate(nodes):
                all_equations_vectors[count] = self.get_features_from_token(node.value)
                count = count + 1

        print("Shape of all node vectors: " + str(all_equations_vectors.shape))

        self.write_node_vectors_to_file(all_equations_vectors)

        return node_lists
