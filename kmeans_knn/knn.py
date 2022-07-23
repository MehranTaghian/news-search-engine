from collections import Counter
import time
import utils
import path
import numpy as np
from scipy.sparse import csr_matrix, save_npz, load_npz
from kmeans_knn import vector_represention
import xlrd


def get_X():
    term_2_termid = utils.load_file(path.knn_termids)
    first1000doc = utils.load_file(path.knn_1000_docs)
    x = np.zeros((1000, len(term_2_termid)))
    # doc_vec = first1000doc[0]
    for i in range(1000):
        for term in first1000doc[i].keys():
            x[i][term_2_termid[term]] = first1000doc[i][term]
    return x


def get_class(doc_vec, X, y, k, term_2_termid, which_dataset='THIRD'):
    # all_attrs = utils.load_file(path.knn_all_terms)
    # term_2_termid = utils.load_file(path.knn_termids)

    q_npvec = vector_represention.to_nparray(doc_vec, term_2_termid)
    scores = q_npvec.dot(X.T)

    args = scores.argsort()[-1 * k:][::-1]

    b = Counter(y[args])
    cls = b.most_common(1)
    return int(cls[0][0])




def knn_and_save_all(k, which_dataset='THIRD'):

    res = [[] for i in range(8)]
    y = np.load(path.knn_y + '.npy')

    sparse_mat = load_npz(path.knn_sparse_matrix)
    labeled = sparse_mat[:1000]
    scores = sparse_mat.dot(labeled.T)

    n_doc = np.shape(sparse_mat)[0]
    for i in range(n_doc):
        if i % 10000 == 0:
            print(i)
        vec = scores[i].toarray()[0]
        vec = vec.argsort()[-1 * k:][::-1]
        b = Counter(y[vec])
        cls = b.most_common(1)
        cls = int(cls[0][0])
        res[cls - 1].append(i)
    utils.write_to_file(res, path.python_objects + f'/knn_result_k{k}.pkl')


def save_needed_stuff(which_dataset='THIRD'):
    doc_vector = utils.load_file(f'Python_Objects/type_3_weighting_scheme_{which_dataset}_normalized.pkl')

    wb = xlrd.open_workbook(path.labels_excel)
    sheet = wb.sheet_by_index(0)

    sheet.cell_value(0, 0)

    # all_attrs = vector_represention.get_all_attributes(doc_vector)
    y = np.zeros(1000)

    t = time.time()

    for i in range(1000):
        y[i] = sheet.cell_value(i + 1, 1)
    print('it took', time.time() - t)

    indptr = [0]
    indices = []
    data = []
    vocabulary = {}
    t = time.time()
    for i in doc_vector.keys():
        if i % 10000 == 0:
            print(i, ':', time.time() - t)
            t = time.time()
        for term in doc_vector[i].keys():
            index = vocabulary.setdefault(term, len(vocabulary))
            indices.append(index)
            data.append(doc_vector[i][term])
        indptr.append(len(indices))
    sparse_matrix = csr_matrix((data, indices, indptr), dtype=float)
    save_npz(path.knn_sparse_matrix, sparse_matrix)
    np.save(path.knn_y, y)
