import pandas as pd
import numpy as np
import pickle

import nltk
from nltk import word_tokenize
from nltk import PorterStemmer
from nltk.corpus import stopwords

from progressbar import ProgressBar

num_equations = 10000

nltk.download('stopwords')
stop_words = stopwords.words('english')

vocab2id = {}
id2vocab = {}

# Pre-process contexts
def linguistic_preprocess(contexts):
    porter = PorterStemmer()
    processed = []
    pbar = ProgressBar()
    term_id = 0

    print('Stop words, lemmatization')

    for context in pbar(contexts):
        # Tokenize the sentence
        tkn_context = word_tokenize(context)

        # Drop the stopwords
        tkn_context = [word for word in tkn_context if word not in stop_words]

        # Retain only alphabetic words
        tkn_context = [word.lower() for word in tkn_context if word.isalpha()]

        # Stem the tokens
        stemmed = []
        for tkn in tkn_context:
            tkn_stemmed = porter.stem(tkn)

            if len(tkn_stemmed) <= 2:
                continue

            # Add to vocabulary
            if porter.stem(tkn) not in vocab2id:
                vocab2id[tkn_stemmed] = term_id
                id2vocab[term_id] = tkn_stemmed
                term_id += 1

            stemmed.append(vocab2id[tkn_stemmed])

        processed.append(stemmed)

    print("Size of vocabulary: " + str(len(vocab2id.keys())))
    pickle.dump(vocab2id, open('vocab2id_first10000.pkl', 'wb'))
    pickle.dump(id2vocab, open('id2vocab_first10000.pkl', 'wb'))

    return processed


df = pd.read_csv('~/data/fyp/kdd/equations.csv')
df = df[0: num_equations]
print(df.columns)

contexts = df['contexts']
processed = linguistic_preprocess(contexts)

# One hot encoding
vocab_size = len(vocab2id.keys())
labels = np.zeros([num_equations, vocab_size])
print("One hot encoding shape: " + str(labels.shape))

for index, term_ids in enumerate(processed):
    for term_id in term_ids:
        labels[index][term_id] += 1.0

    assert (sum(labels[index]) == len(term_ids))

pickle.dump(labels, open('labels_words_first10000.pkl', 'wb'))