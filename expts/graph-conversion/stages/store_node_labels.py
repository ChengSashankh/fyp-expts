from stages.stage import Stage

import pandas as pd
import numpy as np
import pickle

'''
Save dataframe to file
Input: Grep results in pandas.DataFrame with headers as ['match', 'context']
Output: Grep results in pandas.DataFrame with headers as ['match', 'context']
'''


class StoreNodeLabels(Stage):
    def __init__(self, configs):
        self.name = configs['name']
        self.label_dim = 2

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

        if token.value[1] in character_operators or token.value[1] in macro_operators:
            return True
        else:
            return False

    def get_labels_for_equation(self, tokenized_equation):
        labels = np.zeros([len(tokenized_equation), self.label_dim])
        answers = []
        for i, token in enumerate(tokenized_equation):
            if self.is_operator(token):
                labels[i][0] = 1
                answers.append(0)
            else:
                labels[i][1] = 1
                answers.append(1)

            assert (np.sum(labels[i]) == 1)

        return labels, answers

    def label_all_equations(self, node_lists):
        # max_len = 0
        # for t in tokenized_equations:
        #     max_len = max(max_len, len(t))

        total_len = sum([len(e) for e in node_lists])
        all_labels = np.zeros([total_len, self.label_dim])

        count = 0

        # These are not one hot
        all_node_labels_direct = []

        for i, equation in enumerate(node_lists):
            labels, answers = self.get_labels_for_equation(equation)
            all_node_labels_direct = [all_node_labels_direct] + answers
            for j, label in enumerate(labels):
                all_labels[count, :] = label
                count += 1

        # Check the assignment
        for label_one_hot in all_labels:
            assert (np.sum(label_one_hot) == 1)

        return all_labels, answers

    def run(self, input_dict):
        df = input_dict['df']
        node_lists = input_dict['node_lists']

        print("DF shape: " + str(df.shape))
        print("Node list length: " + str(sum([len(n) for n in node_lists])))

        # TODO: Why is the node list size and the df tokenized size not the same? intermediates?

        tokenized_equations = df['equation']

        assert (type(tokenized_equations) == pd.core.series.Series)
        assert (type(tokenized_equations[0]) == list)

        all_labels, labels_answers = self.label_all_equations(node_lists)

        print("Shape of all labels: " + str(all_labels.shape))

        # Store the labels to file
        pickle.dump(all_labels, open('/Users/cksash/data/fyp/kdd/all_labels.pkl', 'wb'))

        # Store the labels directly for graph classification
        fptr = open('/Users/cksash/data/fyp/kdd/EQUATIONS_node_labels.txt', 'w')
        for ans in labels_answers:
            fptr.write(str(ans) + '\n')

        return node_lists
