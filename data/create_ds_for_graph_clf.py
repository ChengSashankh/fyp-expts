import pickle

adj_matrix = pickle.load(open('/c/home/cksash/kdd/joined_adjmatrix.pkl', 'rb'))
node_feats = pickle.load(open('/c/home/cksash/kdd/node_vectors_joined.pkl', 'rb'))
graph_labels = pickle.load(open('/c/home/cksash/fyp-main/data/labels_words_first10000.pkl', 'rb'))
graph_numbers = pickle.load(open('/c/home/cksash/kdd/graph_number.pkl', 'rb'))

# Write the adj matrix as a text file with pairs mentioned
size = adj_matrix.shape[0]
pairs = []

for i in range(size):
    for j in range(size):
        if adj_matrix[i][j] == 1:
            pairs.append([i, j])
# Graph numbers are calculated and written
node_graph_map = []