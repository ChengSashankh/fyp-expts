from stages.stage import Stage

import nltk
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from progressbar import ProgressBar

nltk.download('punkt')

'''
Tokenize, remove stopwords and stem context of equations. 
Input: Grep results in pandas.DataFrame with headers as ['match', 'context']
Output: DataFrame with contexts tokenized and preprocessed.
'''
class LinguisticPreprocessing(Stage):
  def __init__(self, configs):
    self.name = configs['name']
    self.stemming = configs['stemming']
  
  def tokenize_sentence(self, sentence):
    return word_tokenize(sentence)
  
  def remove_stopwords(self, tokenized_sentence):
    stop_words = set(stopwords.words('english'))
    return [word for word in tokenized_sentence if word not in stop_words]

  def stem_words_in_sentence(self, tokenized_sentence):
    porter = PorterStemmer()
    return [porter.stem(word) for word in tokenized_sentence]

  def process_contexts(self, contexts):
    processed_contexts = []

    pbar = ProgressBar()
    
    for context in pbar(contexts):
      tokenized_context = self.tokenize_sentence(context)
      tokenized_context = self.remove_stopwords(tokenized_context)
      tokenized_context = self.stem_words_in_sentence(tokenized_context)

      processed_contexts.append(' '.join(tokenized_context))
    
    return processed_contexts

  def run(self, df):
    processed_contexts = self.process_contexts(df['context'])
    processed_references = self.process_contexts(df['reference'])
    
    df['context'] = processed_contexts
    df['reference'] = processed_references

    return df

