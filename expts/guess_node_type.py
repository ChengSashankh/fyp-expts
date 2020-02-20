import tensorflow as tf
import numpy as np
import pickle

node_vectors = pickle.load(open('./graph-conversion/outputs/node_vectors.pkl', 'rb'))
adjmatrices = pickle.load(open('./graph-conversion/outputs/pickles/adjmatrices.pkl', 'rb'))
labels = pickle.load(open('./graph-conversion/outputs/all_labels.pkl', 'rb'))

# Calculate degree matrix
degree_matrices = []
for adjmatrix in adjmatrices:
    assert(adjmatrix.shape[0] == adjmatrix.shape[1])

    deg = np.zeros([len(adjmatrix), len(adjmatrix)])

    for i in range(adjmatrix.shape[0]):
        deg[i][i] = np.sum(adjmatrix[i])
    
    degree_matrices.append(deg)

print ("Node vectors: " + str(node_vectors.shape))
print ("adjmatrices: " + str(len(adjmatrices)))
print ("Labels: " + str(labels.shape))

# Concat adjmatrix
total_size = 0
for adjmatrix in adjmatrices:
    assert(adjmatrix.shape[0] == adjmatrix.shape[1])
    total_size += adjmatrix.shape[0]

print (total_size)
joined_adjmatrix = np.zeros([total_size, total_size])

curr = 0
for adjmatrix in adjmatrices:
    mat_size = adjmatrix.shape[0]
    for i in range(0, mat_size):
        for j in range(0, mat_size):
            joined_adjmatrix[curr + i][curr + j] = adjmatrix[i][j]
    
    curr += mat_size

# concat node feature lists
joined_features = np.zeros([total_size, node_vectors.shape[2]])
next_vec = 0
for i in range(node_vectors.shape[0]):
    num_nodes = adjmatrices[i].shape[0]
    for j in range(num_nodes):
        joined_features[next_vec] = node_vectors[i][j]
        next_vec += 1

assert (next_vec == total_size)

pickle.dump(joined_adjmatrix, '')

#concat labels
# unpacked_labels = np.zeros(total_size)

# for i in range()

# Initialize weights
# weights = tf.Variable(tf.random_normal((,), stddev= 1))

# def layer(features, adjacency, degree, weights):
#     with tf.name_scope('gcn'):
#         d = tf.pow(degree + tf.eye(), -0.5)
#         y = tf.matmul(d, tf.matmul(adjacency, d))
#         kernel = tf.matmul(features, weights)
#
#         return tf.nn.relu(tf.matmul(y, kernel))

# model = layer(, )