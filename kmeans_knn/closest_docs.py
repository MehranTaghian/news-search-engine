import kmeans_knn.kmeans as kmeans
import path
from scipy.sparse import csr_matrix, save_npz, load_npz
from collections import Counter
from TF_IDF import calculate_score_for_docs
import utils
import heapq
import numpy as np

import time
import math


def save_closest_docs(k=10):
    which_dataset = 'THIRD'
    # doc_vector = utils.load_file(f'Python_Objects/type_3_weighting_scheme_{which_dataset}_normalized.pkl')
    # tf_idf_table = utils.load_file(f'Python_Objects/type_3_weighting_scheme_{which_dataset}.pkl')
    # pos_index = utils.load_file(f'Python_Objects/pos_index_{which_dataset}.pkl')
    close_ones = []
    t = time.time()
    sparse_mat = load_npz(path.knn_sparse_matrix)
    print(time.time() - t)
    # sco = sparse_mat.dot(sparse_mat.T)

    # exit()

    n_doc = 158270
    t = 0
    batch_size = 300

    for id in range(math.ceil(n_doc / batch_size)):

        if id % 1 == 0:
            print(id)
            print(time.time() - t)
            t = time.time()
        query_vector = sparse_mat[id * batch_size:min((id + 1) * batch_size, n_doc)]
        vec = sparse_mat.dot(query_vector.T)
        vec = vec.toarray()
        vec = vec.argsort(axis=0)[-1 * (k + 1):][::-1]

        vec = vec.T
        vec = vec[:, 1:]
        np.save(path.close_ones + '/' + str(id), vec)
        # close_ones.extend(vec)
        # print(np.shape(close_ones))


def merge_files():
    n_doc = 158270

    batch_size = 300
    all = []
    for id in range(math.ceil(n_doc / batch_size)):
        cloz = np.load(path.close_ones + '/' + str(id)+'.npy')
        all.append(cloz)
    all = np.concatenate(all, axis=0)
    print(np.shape(all))
    np.save(path.close_ones + '/all' , all)


def test():
    clozez = np.load(path.close_ones + '/all.npy')
    print(clozez[0])
    print(clozez[1])
    print(clozez[2])

    sparse_mat = load_npz(path.knn_sparse_matrix)
    # print(time.time() - t)
    # sco = sparse_mat.dot(sparse_mat.T)

    # exit()

    n_doc = 158270
    t = 0
    batch_size = 300

    query_vector = sparse_mat[:3]
    vec = sparse_mat.dot(query_vector.T)
    vec = vec.toarray()
    vec = vec.argsort(axis=0)[-1 * (10 + 1):][::-1]

    vec = vec.T
    vec = vec[:, 1:]
    print(vec)
