import utils
from math import log10 as log
import numpy as np
# import pandas as pd
from collections import Counter


def normalize_doc_vecs(doc_vector):
    # Normalize Document Vectors
    for i in doc_vector.keys():
        denominator = 0
        for term in doc_vector[i].keys():
            denominator += doc_vector[i][term] ** 2
        denominator = denominator ** (1 / 2)
        for term in doc_vector[i].keys():
            doc_vector[i][term] /= denominator
    return doc_vector


def sim_function_for_docs(doc1, doc2):
    sim = 0
    for t in doc1.keys():
        if t in doc2:
            sim += doc1[t] * doc2[t]

    return sim
def sim_with_all_cents(doc,centroids):
    sims = [0 for i in range(len(centroids))]
    for t in doc.keys():
        for j in range(len(centroids)):
            if t in centroids[j]:
                sims[j] += doc[t] * centroids[j][t]

    return sims

def mean_function_for_docs(some_docs):
    mean = Counter()
    for i in range(len(some_docs)):
        mean.update(some_docs[i])
    # print('mean has', len(list(mean.keys())), 'attrs')
    mean = to_most_freqs(mean)
    denominator = 0
    for term in mean.keys():
        denominator += mean[term] ** 2
    denominator = denominator ** (1 / 2)
    for term in mean.keys():
        mean[term] /= denominator
    return mean


def to_most_freqs(x, at_most=500):
    sor = sorted(Counter(x))[:at_most]
    m2 = {}
    for t in sor:
        m2[t] = x[t]
    return m2


def get_query_vector(phrasal_terms, simple_terms_tf_query, phrasal_terms_tf_query, N, tf_idf_table, pos_index, IDF):
    query_vector = {}
    # tf_idf_table = utils.load_file(f'Python_Objects/TF_IDF_{which_dataset}.pkl')
    # pos_index = utils.load_file(f'Python_Objects/pos_index_{which_dataset}.pkl')
    # IDF = utils.load_file(f'Python_Objects/IDF_{which_dataset}.pkl')
    from TF_IDF import add_weight_scheme_3_for_phrase
    for s in simple_terms_tf_query:
        try:
            query_vector[s] = (1 + log(simple_terms_tf_query[s])) * IDF[s]
        except KeyError:
            pass
    for phrase in phrasal_terms:
        idf = add_weight_scheme_3_for_phrase(phrase, pos_index, tf_idf_table, N)
        phrase = ' '.join(phrase)
        query_vector[phrase] = (1 + log(phrasal_terms_tf_query[phrase])) * idf

    return query_vector


def get_all_attributes(docs):
    attrs = []
    for d in docs.keys():
        attrs.extend(list(docs[d].keys()))
    return list(set(attrs))


def to_nparray(doc, term_2_termid):
    vec = [0 for i in range((len(term_2_termid)))]
    for d in doc.keys():
        vec[term_2_termid[d]] = doc[d]
    return np.array(vec)



def euclidean_dis(d1, d2):
    dis = 0
    d1k = d1.keys()
    d2k = d2.keys()
    for t in set(list(d1.keys()) + list(d2.keys())):
        d1_val = 0
        d2_val = 0
        if t in d1k:
            d1_val = d1[t]
        if t in d2k:
            d1_val = d2[t]

        dis += (d1_val - d2_val) ** 2
    return dis