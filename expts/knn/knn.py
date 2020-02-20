from sklearn.neighbors import KDTree
import numpy as np
from flask import request, jsonify, Flask

# KDTree indexing

n_points = 10
n_features = 10

# TODO: Get from actual model
vectors = np.zeros([n_points, n_features])
# TODO: Get real labels
labels = np.zeros(n_points)

tree = KDTree(vectors, leaf_size=2)

# Reverse lookups
vec2label = {}

assert (vectors.shape[0] == labels.shape[0])

for i in range(len(labels)):
  vec2label[str(vectors[i])] = labels[i]

# API 

app = Flask(__name__)
@app.route('/query', methods=['POST'])
def query():
  if request.method == 'POST':
    data = request.json
    
    results = KDTree.query(np.array(data['queries']), k=5)

    return str(results)
app.run()