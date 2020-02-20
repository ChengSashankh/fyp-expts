from stages.stage import Stage

import numpy as np
from pylatexenc.latexwalker import LatexWalker, LatexWalkerEndOfStream
from progressbar import ProgressBar

'''
Filter dataframe to get rid of problematic entries
Input: Grep results in pandas.DataFrame with headers as ['match', 'context']
Output: Filtered entries only from DataFrame with headers as ['match', 'context']
'''


class EquationTokenizationStage(Stage):

    def __init__(self, configs):
        self.name = configs['name']

    # Process a single equation
    def equation_to_tokens(self, equation):
        tokenized_with_type = []
        start = 0
        could_not_parse = False

        if '\\newcommand' in equation:
            # raise NameError('New command detected')
            return True, tokenized_with_type

        while start < len(equation):
            w = LatexWalker(equation, tolerant_parsing=True)

            try:
                tk = w.get_token(start)
            except LatexWalkerEndOfStream:
                break
            except Exception as e:
                print('Caught exception ' + str(e))
                print('Offending equation: ' + str(equation))
                could_not_parse = True
                return could_not_parse, tokenized_with_type

            tokenized_with_type.append([tk.tok, tk.arg])
            start = (tk.pos + tk.len)

        return could_not_parse, tokenized_with_type

    # Tokenize all equations
    def tokenize_all(self, equations):
        tokenized_equations = []
        skipped = np.zeros(len(equations))
        # pbar = ProgressBar()

        for i, equation in enumerate(equations):
            could_not_parse, tokenized_equation = self.equation_to_tokens(equation)
            if could_not_parse:
                skipped[i] = 1
            else:
                tokenized_equations.append(self.remove_specials(tokenized_equation))

        skipped = np.argwhere(skipped == 1)
        print (type(skipped))
        print (type(skipped[0]))

        skipped = [s[0] for s in skipped]

        print (type(skipped))
        print (type(skipped[0]))
        print ("Number skipped = " + str(len(skipped)))
        return skipped, tokenized_equations

    def remove_specials(self, tk_eqn):
        eqn = []

        for tk in tk_eqn:
            if len(tk) < 1 or tk[0] == 'specials' or tk[0] == 'comment':
                continue
            eqn.append(tk)

        return eqn

    # Drop the rows in the dataset for which the equation tokenization failed
    def drop_df_rows_without_tokenization(self, df, skipped):
        print ("Length of df before dropping: " + str(df.shape[0]))
        return df.drop(skipped)

    def run(self, df):
        equations = df['equation']
        skipped, tokenized_equations = self.tokenize_all(equations)
        df = self.drop_df_rows_without_tokenization(df, skipped)
        print("Length of df after dropping: " + str(df.shape[0]))
        df['equation'] = tokenized_equations

        return df
