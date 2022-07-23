import random
import path
import time
from kmeans_knn.vector_represention import *
from scipy.sparse import csr_matrix, save_npz, load_npz


# from scipy.sparse import csr_matrix, save_npz, load_npz


def save_pandas_matrix(which_dataset):
    doc_vector = utils.load_file(f'Python_Objects/type_3_weighting_scheme_{which_dataset}_normalized.pkl')
    attrs = get_all_attributes(doc_vector)
    # initial = {}
    # for t in attrs:
    #     initial[t] = 0
    doc_ids = list(doc_vector.keys())
    t = time.time()
    frames2 = []
    for i in doc_ids:
        print(i)
        # t2 = time.time()
        # init2 = initial.copy()
        # init2.update(doc_vector[i])
        # print('t2',time.time()-t2)
        frames2.append(pd.DataFrame(doc_vector[i], index=[i]))
    print('frames added in', time.time() - t)
    t = time.time()
    matrix = pd.concat(frames2).fillna(0)
    print('pandas matrix create in', time.time() - t)
    utils.write_to_file(matrix, path.pandas_matrix)


def get_clusters(doc_vector_orig, iters, k):
    doc_vector = {}
    for id in doc_vector_orig.keys():
        doc_vector[id] = to_most_freqs(doc_vector_orig[id])

    centroids = random.sample(list(doc_vector_orig.keys()), k)
    centroids = [doc_vector[i] for i in centroids]

    belongs = {}
    for i in range(iters):
        t1 = time.time()
        print('Iter:', i)

        clusters = [[] for g in range(k)]
        pre_centroids = centroids.copy()
        for j in doc_vector.keys():
            if j % 50000 == 0:
                print('doc', j, ' at iter ', i)
            # max_sim = 0
            sims = sim_with_all_cents(doc_vector[j], centroids)
            belongs[j] = np.argmax(sims)

            clusters[belongs[j]].append(doc_vector[j])
        print('similarities done')
        t3 = time.time()
        for l in range(len(centroids)):
            centroids[l] = mean_function_for_docs(clusters[l])
        print('mean takes', time.time() - t3)
        if centroids == pre_centroids:
            break
        print('iter', i, 'took', time.time() - t1)
    clusters = [{} for g in range(k)]
    for j in range(len(centroids)):
        clusters[j]['centroid'] = centroids[j]
        clusters[j]['cluster'] = []
    for j in doc_vector.keys():
        clusters[belongs[j]]['cluster'].append(j)
    return clusters


def compute_and_save_clusterings(iters, k, which_dataset):
    doc_vector = utils.load_file(f'Python_Objects/type_3_weighting_scheme_{which_dataset}_normalized.pkl')
    # doc_vector = normalize_doc_vecs(doc_vector)
    r = get_clusters(doc_vector, iters, k)
    utils.write_to_file(r, path.python_objects + f'/k_{k}_iter_{iters}_{which_dataset}.pkl')

clusters = utils.load_file(path.clustering_result_path)

def get_cluster_mates(path, phrasal_terms, simple_terms_tf_query, phrasal_terms_tf_query, N,
                      tf_idf_table, pos_index, IDF, from_how_many_cluster=3):

    query_vector = get_query_vector(phrasal_terms, simple_terms_tf_query, phrasal_terms_tf_query, N, tf_idf_table,
                                    pos_index, IDF)

    # Normalize Query Vector
    # denominator = 0
    # for t in query_vector:
    #     denominator += query_vector[t] ** 2
    # denominator = denominator ** (1 / 2)

    # best_sim = 0
    # best_sim_id = 0



    indptr = [0]
    indices = []
    data = []
    vocabulary = {}
    t = time.time()
    cents = [c['centroid'] for c in clusters]
    cents.append(query_vector)
    for i in range(len(cents)):

        for term in cents[i].keys():
            index = vocabulary.setdefault(term, len(vocabulary))
            indices.append(index)
            data.append(cents[i][term])
        indptr.append(len(indices))
    sparse_matrix = csr_matrix((data, indices, indptr), dtype=float)
    q_vec = sparse_matrix[-1,:]
    sparse_matrix = sparse_matrix[:-1,:]
    sims = q_vec.dot(sparse_matrix.T)
    # print(np.shape(sims))

    clus_ids = np.array(sims).argsort()[-1 * from_how_many_cluster:]
    all = []
    for id in clus_ids:
        all.extend(clusters[id]['cluster'])
    return all


def get_cluster_mates_from_vec(path, query_vector):
    clusters = utils.load_file(path)

    best_sim = 0
    best_sim_id = 0
    for i, c in enumerate(clusters):
        sim = 0
        for t in query_vector:
            if t in c['centroid']:
                sim += c['centroid'][t] * (query_vector[t])
        if sim >= best_sim:
            best_sim = sim
            best_sim_id = i

    return list(clusters[best_sim_id]['cluster'])


def compute_RSS(doc_vector, clusterings_path, which_dataset='THIRD'):
    clusterings = utils.load_file(clusterings_path)

    rss = 0
    for i in range(len(clusterings)):
        c = clusterings[i]['centroid']
        for doc_id in clusterings[i]['cluster']:
            # print(doc_id)
            rss += euclidean_dis(c, doc_vector[doc_id])
    return rss


def get_plot_of_RRSs(ks, iter, which_dataset='THIRD'):
    RSSs = []
    doc_vector = utils.load_file(f'Python_Objects/type_3_weighting_scheme_{which_dataset}_normalized.pkl')

    for k in ks:
        print('k=', k)
        rss = compute_RSS(doc_vector, path.python_objects + f'/k_{k}_iter_{iter}_{which_dataset}.pkl')
        RSSs.append(rss)
    import matplotlib.pyplot as plt
    plt.scatter(ks, RSSs)
    plt.xlabel('k')
    plt.ylabel('RSS')
    plt.show()

#
# def knn_matrixi(k,iters):
#     sparse_mat = load_npz(path.knn_sparse_matrix)
#     n_docs = np.shape(sparse_mat)[0]
#     centroids = random.sample(range(n_docs), k)
#     centroids = sparse_mat[centroids, :]
#     print(np.shape(centroids))
#
#     for iter in range(iters):
#         scores = sparse_mat.dot(centroids.T)
#         # batch_size = 10000
#         args = scores.argmax(axis=1)
#         print(np.shape(args))
#         for j in range(k):
#             print(j)
#             centids = [[] for l in range(k)]
#             for l in range(n_docs):
#                 # print(l)
#                 # print(args[l,0])
#                 centids[args[l, 0]].append(l)
#             mean = sparse_mat[centids[j], :].mean(axis=0)
#             # print(np.shape(mean),np.shape(sparse_mat))
#             sco = sparse_mat[centids[j], :].dot(mean.T)
#             # print('size',np.shape(sco))
#             cent  = sco.argmax()
#             # print('cent',cent)
#             centroids[j, :] = sparse_mat[cent,:]
#             # exit
#         # for i in range(int(n_docs / batch_size)):
#         #     sco = scores[i * batch_size:min((i+1) * batch_size, n_docs), :].toarray()
#         #     print(np.shape(sco))
#         #     # print(sco)
#         #     args = sco.argmax(axis=1)
#         #     print(np.shape(args))
