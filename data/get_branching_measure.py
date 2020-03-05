import pickle as pkl
import numpy as np

# TODO
def get_tree_depth(adj_matrix):
    return 1


# Multiple defined as >2
def get_num_nodes_with_multiple_neighbours(adj_matrix):
    size = adj_matrix.shape[0]
    assert (adj_matrix.shape[0] == adj_matrix.shape[1])

    num_nodes = 0
    for i in range(size):
        count = 0
        for j in range(size):
            if adj_matrix[i][j] != 0:
                count += 1

        if count > 2:
            num_nodes += 1

    return num_nodes


# Average measure
def get_average_num_neighbours(adj_matrix):
    size = adj_matrix.shape[0]
    assert (adj_matrix.shape[0] == adj_matrix.shape[1])

    avg_num_neighbors = 0
    for i in range(size):
        for j in range(size):
            if adj_matrix[i][j] != 0:
                avg_num_neighbors += 1

    avg_num_neighbors = avg_num_neighbors / size

    return avg_num_neighbors


# Main
adj_matrices_path = ''
adj_matrices = pkl.load(open(adj_matrices_path, 'rb'))

measures = np.zeros(len(adj_matrices))
for i, adj_matrix in enumerate(adj_matrices):
    measures[i] = get_average_num_neighbours(adj_matrix)

pkl.dump(measures, open(''))