import pandas as pd

input_df = pd.read_csv('../../server/sample_search.csv')

print (input_df.columns)

new_df = pd.DataFrame(columns=['equation', 'context', 'references'])

pre = input_df['pre']
post = input_df['post']
refs = input_df['refs']
equation = input_df['tkn_eq']

cons = []
for i in range(len(pre)):
    cons.append(str(pre[i]) + ' ' + str(post[i]))

new_df['equation'] = equation
new_df['context'] = cons
new_df['references'] = refs

new_df.to_csv('test_df.csv')