from math import log10 as log

from parsivar import Tokenizer

from utils import cleanhtml
from parsivar import Normalizer
from parsivar import FindStems
import utils
import xlrd
import pandas as pd
from PostingsListProcesses import find_documents_for_phrase
from normalizers.normalizer import normalize

PATH_SEPARATOR = '/'
FIRST_DATASET_DIR = 'Data/data.xlsx'
SECOND_DATASET_DIR = 'Data/IR-F19-Project02-14k.csv'
THIRD_DATASET_DIR = r'C:\Users\Mehran\Desktop\Desktop files\Courses\Information ' \
                    r'Retrievla\Project\03\IR-project-data-phase-3-100k'
LABELED_DATA_PATH = 'labeled_data/labeled_data.csv'
stemmer = FindStems()


def create_TF_IDF_table(file_dir, type_of_file, target='FIRST', number_of_files_more_than_one=False):
    if type_of_file == 'csv':
        if not number_of_files_more_than_one:
            data = pd.read_csv(file_dir)
        else:
            import os
            filenames = os.listdir(file_dir)
            dfs = list()
            for f in filenames:
                df = pd.read_csv(THIRD_DATASET_DIR + PATH_SEPARATOR + f)
                dfs.append(df)
            data = pd.concat(dfs, axis=0, ignore_index=True)

    elif file_dir.split('.')[1] == 'xlsx':
        data = pd.read_excel(file_dir)

    N = len(data)
    # fileNo = 2

    # book = xlrd.open_workbook("data.xlsx")
    # first_sheet = book.sheet_by_index(0)
    # N = first_sheet.nrows
    IDF = {}
    term_frequency = {}
    frequency_in_doc = {}
    type_3_weighting_scheme = {}
    # Type 2 weighting scheme is the same as term frequency.
    type_1_weighting_scheme = {}

    N_over_doc_frequency = {}  # N / n_i

    # for i in range(2, N):
    for index, row in data.iterrows():
        print(index)
        content = row['content']
        title = row['title']
        summary = row['summary']

        if type(title) == float:
            # print("title", index)
            title = ''
        if type(content) == float:
            # print("content", index)
            content = ''
        if type(summary) == float:
            # print("summary", index)
            summary = ''

        # try:
        try:
            str = title + ' ' + summary + ' ' + content
        except TypeError:
            print('title', type(title))
            print(title)
            print('content', type(content))
            print(content)
            print('summary', type(summary))
            print(summary)
            print('#' * 50)

        tokens = normalize(str)

        frequency_in_doc[index] = {}
        term_frequency[index] = {}

        for tok in tokens:
            tok = stemmer.convert_to_stem(tok)
            if tok in term_frequency[index].keys():
                frequency_in_doc[index][tok] += 1  # calculating term frequency
            else:
                frequency_in_doc[index][tok] = 1

        for term in frequency_in_doc[index].keys():
            term_frequency[index][term] = (1 + log(frequency_in_doc[index][term]))
            if term in IDF.keys():
                IDF[term] += 1
            else:
                IDF[term] = 1

    for term in IDF.keys():
        N_over_doc_frequency[term] = N / IDF[term]
        IDF[term] = log(N / IDF[term])

    for i in range(0, N):
        type_3_weighting_scheme[i] = {}
        for term in term_frequency[i].keys():
            type_3_weighting_scheme[i][term] = term_frequency[i][term] * IDF[term]

    for i in range(0, N):
        type_1_weighting_scheme[i] = {}
        for term in term_frequency[i].keys():
            type_1_weighting_scheme[i][term] = frequency_in_doc[i][term] * IDF[term]

    utils.write_to_file(type_1_weighting_scheme, f'Python_Objects/type_1_weighting_scheme_{target}.pkl')
    utils.write_to_file(term_frequency, f'Python_Objects/type_2_weighting_scheme_{target}.pkl')
    utils.write_to_file(type_3_weighting_scheme, f'Python_Objects/type_3_weighting_scheme_{target}.pkl')
    utils.write_to_file(N_over_doc_frequency, f'Python_Objects/N_over_doc_freq_{target}.pkl')
    utils.write_to_file(type_3_weighting_scheme, f'Python_Objects/TF_IDF_{target}.pkl')
    utils.write_to_file(term_frequency, f'Python_Objects/TF_{target}.pkl')
    utils.write_to_file(IDF, f'Python_Objects/IDF_{target}.pkl')


def TF_IDF_query_process(docs, phrasal_terms, simple_terms_tf_query, phrasal_terms_tf_query,
                         number_of_docs, which_dataset, weighting_scheme, tf_idf_table, pos_index, IDF):
    """

    :param docs: documents returned which are relevant to the query
    :param simple_tokens: one word terms
    :param phrasal_tokens: phrasal queries
    :param simple_terms_tf_query: term frequency of the simple words in query
    :param phrasal_terms_tf_query: term frequency of the phrase words in query
    :param weighting_scheme: one of the three weighting scheme as follows:
    1) document weighting: tf(t,d) * log (N / n_i)
        query term weighting: [0.5 + 0.5 * tf(t, q) / max(tf(t, q))] . log(N/n_i)
    2) document weighting: 1 + log(tf(t, d))
        query term weighting: log(1 + N/n_i)
    3) document weighting: (1 + log(tf(t, d))).log(N/n_i)
        query term weighting: (1 + log(tf(t, q))).log(N/n_i)
    :return: The ranked documents
    """

    if weighting_scheme == 1:
        return type_one_weighting_scheme(docs, phrasal_terms, simple_terms_tf_query,
                                         phrasal_terms_tf_query, which_dataset, number_of_docs)
    elif weighting_scheme == 2:
        return type_two_weighting_scheme(docs, phrasal_terms, simple_terms_tf_query,
                                         which_dataset, number_of_docs)
    else:
        return type_three_weighting_scheme(docs, phrasal_terms, simple_terms_tf_query,
                                           phrasal_terms_tf_query, number_of_docs, tf_idf_table, pos_index, IDF)


def type_one_weighting_scheme(docs, phrasal_terms, simple_terms_tf_query, phrasal_terms_tf_query, which_dataset, N):
    doc_vector = utils.load_file(f'Python_Objects/type_1_weighting_scheme_{which_dataset}.pkl')
    IDF = utils.load_file(f'Python_Objects/IDF_{which_dataset}.pkl')
    pos_index = utils.load_file(f'Python_Objects/pos_index_{which_dataset}.pkl')
    query_vector = {}
    freq_simple = list(simple_terms_tf_query.values())
    freq_phrase = list(phrasal_terms_tf_query.values())
    max_freq = max(freq_phrase + freq_simple)
    for s in simple_terms_tf_query:
        try:
            query_vector[s] = (0.5 + 0.5 * simple_terms_tf_query[s] / max_freq) * IDF[s]
        except KeyError:
            pass

    for phrase in phrasal_terms:
        IDF_phrase = add_weight_scheme_1_for_phrase(phrase, pos_index, doc_vector, N)
        phrase = ' '.join(phrase)
        query_vector[phrase] = (0.5 + 0.5 * phrasal_terms_tf_query[phrase] / max_freq) * IDF_phrase
    return calculate_score_for_docs(doc_vector, docs, query_vector)


def type_two_weighting_scheme(docs, phrasal_terms, simple_terms_tf_query, which_dataset, N):
    doc_vector = utils.load_file(f'Python_Objects/type_2_weighting_scheme_{which_dataset}.pkl')
    N_over_doc_freq = utils.load_file(f'Python_Objects/N_over_doc_freq_{which_dataset}.pkl')
    pos_index = utils.load_file(f'Python_Objects/pos_index_{which_dataset}.pkl')
    query_vector = {}

    for s in simple_terms_tf_query:
        try:
            query_vector[s] = log(1 + N_over_doc_freq[s])
        except KeyError:
            pass

    for phrase in phrasal_terms:
        N_over_doc_freq = add_weight_scheme_2_for_phrase(phrase, pos_index, doc_vector, N)
        phrase = ' '.join(phrase)
        query_vector[phrase] = log(1 + N_over_doc_freq)

    return calculate_score_for_docs(doc_vector, docs, query_vector)


def type_three_weighting_scheme(docs, phrasal_terms, simple_terms_tf_query, phrasal_terms_tf_query, N
                                , tf_idf_table, pos_index, IDF):
    # tf_idf_table = utils.load_file(f'Python_Objects/type_3_weighting_scheme_{which_dataset}.pkl')
    # pos_index = utils.load_file(f'Python_Objects/pos_index_{which_dataset}.pkl')
    # IDF = utils.load_file(f'Python_Objects/IDF_{which_dataset}.pkl')

    query_vector = {}

    for s in simple_terms_tf_query:
        try:
            query_vector[s] = (1 + log(simple_terms_tf_query[s])) * IDF[s]
        except KeyError:
            pass
    for phrase in phrasal_terms:
        idf = add_weight_scheme_3_for_phrase(phrase, pos_index, tf_idf_table, N)
        phrase = ' '.join(phrase)
        query_vector[phrase] = (1 + log(phrasal_terms_tf_query[phrase])) * idf

    return calculate_score_for_docs(tf_idf_table, docs, query_vector)


## TODO: why to normalize it eah time

def calculate_score_for_docs(doc_vector, docs, query_vector):
    # Normalize Document Vectors
    # for i in docs:
    #     denominator = 0
    #     for term in doc_vector[i].keys():
    #         denominator += doc_vector[i][term] ** 2
    #     denominator = denominator ** (1 / 2)
    #     for term in doc_vector[i].keys():
    #         doc_vector[i][term] /= denominator

    # Normalize Query Vector
    denominator = 0
    for t in query_vector:
        denominator += query_vector[t] ** 2
    denominator = denominator ** (1 / 2)

    scored_docs = {}
    for i in docs:
        scored_docs[i] = 0
        for t in query_vector:
            query_normalize = query_vector[t] / denominator
            try:
                scored_docs[i] += doc_vector[i][t] * query_normalize  # Cosine similarity
            except KeyError:
                pass
    return scored_docs


def add_weight_scheme_3_for_phrase(phrase, pos_index, docs_vector, N):
    _, doc_list = find_documents_for_phrase(phrase, pos_index)
    df = len(doc_list)
    idf = log(N / df)
    for d in doc_list.keys():
        tf = 1 + log(len(doc_list[d]))
        docs_vector[d][' '.join(phrase)] = tf * idf
    return idf


def add_weight_scheme_2_for_phrase(phrase, pos_index, docs_vector, N):
    _, doc_list = find_documents_for_phrase(phrase, pos_index)
    df = len(doc_list)
    for d in doc_list.keys():
        tf = 1 + log(len(doc_list[d]))
        docs_vector[d][' '.join(phrase)] = tf
    return N / df


def add_weight_scheme_1_for_phrase(phrase, pos_index, docs_vector, N):
    _, doc_list = find_documents_for_phrase(phrase, pos_index)
    df = len(doc_list)
    idf = log(N / df)
    for d in doc_list.keys():
        frequency = len(doc_list[d])
        docs_vector[d][' '.join(phrase)] = frequency * idf
    return idf


def find_IDF_for_phrase(phrase, pos_index, N):
    _, doc_list = find_documents_for_phrase(phrase, pos_index)
    return log(N / len(doc_list))


def create_dictionary():
    normalizer = Normalizer()
    tokenizer = Tokenizer()
    stemmer = FindStems()

    dictionary = []
    book = xlrd.open_workbook("data.xlsx")
    first_sheet = book.sheet_by_index(0)

    # print(df.columns)
    # for i in range(len(df['content'])):
    for i in range(10):
        content = first_sheet.cell(i, 5).value
        title = first_sheet.cell(i, 1).value
        summary = first_sheet.cell(i, 3).value
        content = cleanhtml(content)
        string = title + ' ' + summary + ' ' + content
        string = normalizer.normalize(string)
        tokens = tokenizer.tokenize_words(string)

        # print(tokens)
        stemmed = []
        for tok in tokens:
            t = stemmer.convert_to_stem(tok)
            stemmed.append(t)

        dictionary.extend(stemmed)

    dictionary = sorted(list(set(dictionary)))
    # word2idx, idx2word = make_dict(dictionary)
    # # TODO : save them to pickle to use later
    #
    # print(word2idx)
    utils.write_to_file(dictionary, "dictionary.pkl")
    return dictionary

# ---------------------------------------------------- General test
# create_TF_IDF_table(FIRST_DATASET_DIR, 'FIRST')
# create_TF_IDF_table(SECOND_DATASET_DIR, 'csv', 'SECOND')
# create_TF_IDF_table(THIRD_DATASET_DIR, 'csv', 'THIRD', True)
# create_TF_IDF_table(LABELED_DATA_PATH, 'csv', 'labeled_data', False)

# add_TF_IDF_for_phrase(['مقام', 'معظم'], utils.load_file('pos_index.pkl'))
# print(' '.join(['مقام', 'معظم']))
# df, doc_list = find_documents_for_phrase(['مقام', 'معظم'], utils.load_file('pos_index.pkl'))
# print(df)
# print(len(doc_list.keys()))

# -----------------------------------------------------TF IDF test

#
# # Normalization
# for i in doc_vector.keys():
#     denominator = 0
#     for term in doc_vector[i].keys():
#         denominator += doc_vector[i][term] ** 2
#     denominator = denominator ** (1 / 2)
#     for term in doc_vector[i].keys():
#         doc_vector[i][term] /= denominator
#
# print(doc_vector)
