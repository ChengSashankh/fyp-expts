import pandas as pd

df = pd.read_csv('~/Documents/data/tables.csv')
mdfile = open('tables_with_refs.md', 'w')

mdfile.write('# Tables with references\n')


for i, row in df.iterrows():
    t = '\n```\n{% raw %}\n' + str(row['table']) + '\n{% endraw %}\n```\n'
    r = '\n```\n{% raw %}\n' + str(row['refs']) + '\n{% endraw %}\n```\n'
    
    mdfile.write('\nExample ' + str(i + 1))
    mdfile.write('\nTable:\n')
    mdfile.write(t)
    mdfile.write('References:\n')
    mdfile.write(r)