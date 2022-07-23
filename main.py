from collections import defaultdict
from threading import Thread, Timer

import pandas as pd
import requests
from bs4 import BeautifulSoup

from online_crawler.crawler import back_queues, extract_link_from_front_queue_and_put_in_back_queue, \
    hosts_refresh_rates, reorder_front_queues
from parsivar import Tokenizer

from PostingsListProcesses import merge, find_documents_for_simple_terms, find_documents_for_phrase
from parsivar import Normalizer
from parsivar import FindStems
import sys
import utils
from kmeans_knn import kmeans
from TF_IDF import TF_IDF_query_process
import heapq
from normalizers.normalizer import normalize
import path

toker = Tokenizer()
normaler = Normalizer()
stem = FindStems()

PATH_SEPARATOR = '/'
FIRST_DATASET_DIR = 'Data/data.xlsx'
FIRST_DATASET_POS_INDEX_DIR = 'Python_Objects/pos_index_FIRST.pkl'
SECOND_DATASET_DIR = 'Data/IR-F19-Project02-14k.csv'
SECOND_DATASET_POS_INDEX_DIR = 'Python_Objects/pos_index_SECOND.pkl'

THIRD_DATASET_DIR = r'Data/total.csv'
THIRD_DATASET_POS_INDEX_DIR = 'Python_Objects/pos_index_THIRD.pkl'
LABELED_DATA_PATH = 'labeled_data/labeled_data.csv'

NUMBER_OF_DOCS_FOR_FIRST_DATASET = 1729
NUMBER_OF_DOCS_FOR_SECOND_DATASET = 7744
NUMBER_OF_DOCS_FOR_THIRD_DATASET = 158270

ONLINE_INDEX = {}
URL_MAP = {}
global NUMBER_OF_DOCS
NUMBER_OF_DOCS = 158270

classes = ['science', 'culture-art', 'politics', 'economy', 'social', 'international', 'sport', 'multimedia']

which_dataset = 'THIRD'

tf_idf_table = utils.load_file(f'Python_Objects/type_3_weighting_scheme_{which_dataset}_normalized.pkl')
pos_index = utils.load_file(f'Python_Objects/pos_index_{which_dataset}.pkl')
IDF = utils.load_file(f'Python_Objects/IDF_{which_dataset}.pkl')
knn_classified = utils.load_file(path.knn_result)
bayes_classified = utils.load_file(path.bayesian_result)


def parse_query(q, k, pos_index_dir, number_of_docs, which_dataset, weighting_scheme=3):
    """
    Gets query q from the user, and also top k documents to return
    :param q: query
    :param k: top k documents
    :return: ranked top k documents
    """

    # pos_index = utils.load_file(pos_index_dir)  # save it and load it
    print('hey1')
    simple_terms, phrasal_tokens, not_simple_terms, not_phrasal_tokens, categories = query_preprocess(q)
    simple_terms_tf, phrasal_tokens_tf = calculate_tf_in_query(simple_terms, phrasal_tokens)
    related_docs = []
    print('hey2')

    docs = relevant_documents(not_phrasal_tokens, not_simple_terms, phrasal_tokens, pos_index, related_docs,
                              simple_terms, number_of_docs)
    r = []
    online_docs = []
    try:
        online_docs = relevant_documents(not_phrasal_tokens, not_simple_terms, phrasal_tokens, ONLINE_INDEX, r,
                                         simple_terms, len(URL_MAP))
    except KeyError:
        pass

    # print(len(online_docs))
    print('hey3')

    mates = kmeans.get_cluster_mates(path.clustering_result_path, phrasal_tokens, simple_terms_tf,
                                     phrasal_tokens_tf, number_of_docs, tf_idf_table, pos_index, IDF)
    print('mates', len(mates))
    docs = [d for d in mates if d in docs]
    print('hey4')
    if len(categories) > 0:
        clas = categories[0].lower()
        docz = knn_classified[classes.index(clas)]
        docs = [d for d in docs if d in docz]

    # print('docs now:', len(docs))
    import time
    t = time.time()
    scored_docs = TF_IDF_query_process(list(set(docs)), phrasal_tokens, simple_terms_tf, phrasal_tokens_tf,
                                       number_of_docs, which_dataset, weighting_scheme, tf_idf_table,
                                       pos_index, IDF)
    top_k_docs = heapq.nlargest(k, scored_docs, scored_docs.get)
    print('last step took', time.time() - t)

    result = []
    partition_online_and_previous_docs_portion = 3
    online_doc_index = 0
    top_k_docs_index = 0

    for i in range(len(online_docs) + len(top_k_docs)):
        if i % partition_online_and_previous_docs_portion == partition_online_and_previous_docs_portion - 1:
            try:
                result.append(online_docs[online_doc_index])
                online_doc_index += 1
            except IndexError:
                pass
        else:
            try:
                result.append(top_k_docs[top_k_docs_index])
            except IndexError:
                pass
            top_k_docs_index += 1

    # return result
    return result


def calculate_tf_in_query(simple_terms, phrasal_tokens):
    simple_terms_with_tf = {}
    phrasal_terms_with_tf = {}
    for st in simple_terms:
        if st in simple_terms_with_tf:
            simple_terms_with_tf[st] += 1
        else:
            simple_terms_with_tf[st] = 1

    for phrase in phrasal_tokens:
        temp = ' '.join(phrase)
        if temp in phrasal_terms_with_tf:
            phrasal_terms_with_tf[temp] += 1
        else:
            phrasal_terms_with_tf[temp] = 1

    return simple_terms_with_tf, phrasal_terms_with_tf


def relevant_documents(not_phrasal_tokens, not_simple_terms, phrasal_tokens, pos_index, related_docs, simple_terms,
                       number_of_documents):
    for phrase in phrasal_tokens:
        if len(phrase) > 0:
            posting_list = find_documents_for_phrase(phrase, pos_index)
            related_docs.extend(list(posting_list[1].keys()))
            # related_docs = merge(related_docs, list(posting_list[1].keys()))

    not_related_docs = []
    for phrase in not_phrasal_tokens:
        if len(phrase) > 0:
            posting_list = find_documents_for_phrase(phrase, pos_index)
            not_related_docs.extend(posting_list[1].keys())

    simple_docs = []
    if len(simple_terms) > 0:
        simple_docs = find_documents_for_simple_terms(pos_index, simple_terms)

    not_simple_docs = []
    if len(not_simple_terms) > 0:
        not_simple_docs = find_documents_for_simple_terms(pos_index, not_simple_terms)

    if len(related_docs) > 0 and len(simple_docs) > 0:
        have = merge(simple_docs, related_docs)
        # have = set(simple_docs + related_docs)
    elif len(related_docs) > 0:
        have = related_docs
    else:
        have = simple_docs

    if len(have) == 0:
        not_have = not_simple_docs + not_related_docs
        docs = [e for e in list(range(2, number_of_documents + 2)) if e not in not_have]
    else:
        not_have = list(not_simple_docs) + not_related_docs
        docs = [e for e in have if e not in not_have]
    return docs


def query_preprocess(q):
    ## TODO: cat:, source:
    phrasal_tokens = []  # related tokens are those like "بازیابی اطلاعات"
    not_included_tokens = []  # tokens that the documents should not include them
    not_included_phrasal_tokens = []  # related tokens that the documents should not include them
    simple_token = []  # simple tokens like "ایران"
    sources = []
    categories = []

    # s = normaler.normalize(q)
    # tokens = toker.tokenize_words(s)

    tokens = normalize(q)

    # i = 0
    # while i < len(tokens):
    #     if tokens[i] in stopwords:
    #         tokens.remove(tokens[i])
    #     else:
    #         i += 1

    i = 0
    while i < len(tokens):
        if tokens[i] == 'source':
            # print('yes')
            del tokens[i]
            del tokens[i]
            sources.append(tokens.pop(i))
        elif tokens[i] == 'cat':
            del tokens[i]
            del tokens[i]
            categories.append(tokens.pop(i))
        else:
            i += 1

    # stemmed = []
    # for tok in tokens:
    #     # term = unifier(tok)
    #     t = stem.convert_to_stem(tok)
    #     stemmed.append(t)

    query = []
    # for tok in stemmed:
    for tok in tokens:
        if "!" in tok and len(tok) > 1:
            query.append('!')
            query.append(tok.replace('!', ''))
        elif '"' in tok and len(tok) > 1:
            query.append('"')
            query.append(tok.replace('"', ''))
        else:
            query.append(tok)

    tok = 0
    while tok < len(query):
        if query[tok] == '"':
            del query[tok]
            phrasal_tokens.append([])
            while query[tok] != '"':
                phrasal_tokens[len(phrasal_tokens) - 1].append(query.pop(tok))
            del query[tok]

        elif query[tok] == '!':
            del query[tok]
            if query[tok] == '"':
                del query[tok]
                not_included_phrasal_tokens.append([])
                while query[tok] != '"':
                    not_included_phrasal_tokens[len(not_included_phrasal_tokens) - 1].append(query.pop(tok))
                del query[tok]
            else:
                not_included_tokens.append(query.pop(tok))

        else:
            simple_token.append(query.pop(tok))

    return simple_token, phrasal_tokens, not_included_tokens, not_included_phrasal_tokens, categories


def index_doc(file_dir, type_of_file, target_name="Python_Objects/pos_index.pkl", number_of_files_more_than_one=False):
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

    pos_index = {}
    # book = xlrd.open_workbook("data.xlsx")
    # first_sheet = book.sheet_by_index(0)
    # for i in range(1, first_sheet.nrows):
    for index, row in data.iterrows():
        print(index)
        #     print(i)
        # content = first_sheet.cell(i, 5).value
        # title = first_sheet.cell(i, 1).value
        # summary = first_sheet.cell(i, 3).value
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

        # str = normaler.normalize(str)
        # tokens = toker.tokenize_words(str)

        tokens = normalize(str)
        ## NOTICE: it is from GFG   https://www.geeksforgeeks.org/python-positional-index/

        for pos, term in enumerate(tokens):
            # term = unifier(term)
            # term = stem.convert_to_stem(term)

            if term in pos_index:
                pos_index[term][0] += 1
                if index in pos_index[term][1]:
                    pos_index[term][1][index].append(pos)
                else:
                    pos_index[term][1][index] = [pos]
            else:
                pos_index[term] = []
                pos_index[term].append(1)
                pos_index[term].append({})
                pos_index[term][1][index] = [pos]
    utils.write_to_file(pos_index, target_name)

    return pos_index


def online_index(content, title, url):
    str = title + " " + content
    global NUMBER_OF_DOCS

    URL_MAP[NUMBER_OF_DOCS] = url

    tokens = normalize(str)
    ## NOTICE: it is from GFG   https://www.geeksforgeeks.org/python-positional-index/
    index = NUMBER_OF_DOCS

    for pos, term in enumerate(tokens):
        # term = unifier(term)
        # term = stem.convert_to_stem(term)

        if term in ONLINE_INDEX:
            ONLINE_INDEX[term][0] += 1
            if index in ONLINE_INDEX[term][1]:
                ONLINE_INDEX[term][1][index].append(pos)
            else:
                ONLINE_INDEX[term][1][index] = [pos]
        else:
            ONLINE_INDEX[term] = []
            ONLINE_INDEX[term].append(1)
            ONLINE_INDEX[term].append({})
            ONLINE_INDEX[term][1][index] = [pos]

    NUMBER_OF_DOCS += 1


# index_doc(FIRST_DATASET_DIR, 'excel', FIRST_DATASET_POS_INDEX_DIR)
# index_doc(SECOND_DATASET_DIR, 'csv', SECOND_DATASET_POS_INDEX_DIR)
# index_doc(THIRD_DATASET_DIR, 'csv', THIRD_DATASET_POS_INDEX_DIR, number_of_files_more_than_one=True)
# index_doc(LABELED_DATA_PATH, 'csv', target_name="Python_Objects/labeled_data_pos_index.pkl",
#           number_of_files_more_than_one=False)
# pos_index = index_doc()
# # # Sample positional index to test the code.
# sample_pos_idx1 = pos_index["مقام"]
# sample_pos_idx2 = pos_index["معظم"]
# print(sample_pos_idx1)
# print(sample_pos_idx2)
# res = intersect_posting_lists(sample_pos_idx1, sample_pos_idx2)
# print(res)
# print(parse_query(query))

# [5, {5: [154, 282], 9: [45, 211, 292]}]
# it means occurer 5 times 2 times in doc5 and 3 times in doc9 in specified positions
# print(sample_pos_idx)

# query = 'تهران  !"به گزارش خیرنگار مهر"'
# query = '"مقام معظم"'
# query = 'تهران'
# query = 'خبرنگار'
# query = '"پس‌لرزه‌های برهم زدن یک مراسم در قم/جعفری گیلانی: اینها چماقداران مدرن و بی‌عقل هستند/فردی که ۵ حکم از رهبری دارد را تحمل نمی‌کنند"'

# query = '"ادارات استان زنجان فردا از ساعت ۱۲ تعطیل می‌شوند"'  # 392
# query = "!تهران"
# query = "تهران !نمایشگاهی !جاده !خدمه"
# query = 'تهران !"نمایشگاهی" !جاده !خدمه'
# query = '"وی با ابراز امیدواری نسبت به برخورد با چنین رفتارهایی گفت:"'
# query = '"مردم لبنان"'
# query = 'تهران'
# query = 'تهران "مقام معظم"'
# query = 'تهران تهران تهران "مقام معظم" "مقام معظم" "مقام معظم" "مقام معظم" "مقام معظم"'
# query = 'استقلال تهران داربی'
# query = 'تهران بتشسیمت'

# print(normalize(query))
# print(parse_query(query, 10, FIRST_DATASET_POS_INDEX_DIR, NUMBER_OF_DOCS_FOR_FIRST_DATASET, 'FIRST', 3))
# print(parse_query(query, 10, FIRST_DATASET_POS_INDEX_DIR, NUMBER_OF_DOCS_FOR_FIRST_DATASET, 'FIRST', 2))
# print(parse_query(query, 10, FIRST_DATASET_POS_INDEX_DIR, NUMBER_OF_DOCS_FOR_FIRST_DATASET, 'FIRST', 1))

# print(parse_query(query, 10, SECOND_DATASET_POS_INDEX_DIR, NUMBER_OF_DOCS_FOR_SECOND_DATASET, 'SECOND', 3))
# print(parse_query(query, 10, SECOND_DATASET_POS_INDEX_DIR, NUMBER_OF_DOCS_FOR_SECOND_DATASET, 'SECOND', 2))
# print(parse_query(query, 10, SECOND_DATASET_POS_INDEX_DIR, NUMBER_OF_DOCS_FOR_SECOND_DATASET, 'SECOND', 1))


# li = {'test': 1, '3': 2, '2': 6, '5': 7, '6': 4, '8': 3}  # ,9,6,3,10,11,15,14,12]
# print(heapq.nlargest(4, li, key=li.get))

if __name__ == "__main__":
    pass
    # First Dataset
    # print(','.join([str(v) for v in
    #                 parse_query(str(sys.argv[1]), 20, FIRST_DATASET_POS_INDEX_DIR, NUMBER_OF_DOCS_FOR_FIRST_DATASET,
    #                             'FIRST', weighting_scheme=1)]))

    # # Second Dataset
    # print(','.join([str(v) for v in
    #                 parse_query(str(sys.argv[1]), 30, THIRD_DATASET_POS_INDEX_DIR,
    #                             NUMBER_OF_DOCS_FOR_THIRD_DATASET,
    #                             'THIRD', weighting_scheme=3)]))
    #
    # print(','.join(
    #     parse_query(str(sys.argv[1]), 30, THIRD_DATASET_POS_INDEX_DIR,
    #                 NUMBER_OF_DOCS_FOR_THIRD_DATASET,
    #                 'THIRD', weighting_scheme=3)))
file_content = pd.read_csv(THIRD_DATASET_DIR, index_col=0)


def fetch_and_parse():
    while True:
        url, title = back_queues.get_url()
        if url is not None:
            page = requests.get(url=url)
            parsed_html = BeautifulSoup(page.text, "html.parser")
            # content = [(url, title, parsed_html.text), ]
            print("URL", url)
            online_index(parsed_html.text, title, url)
            # local_cursor.executemany('INSERT INTO %s VALUES (?,?,?)' % db_table, content)
            # fetcher_parser_logger.info('fetch a url and parse. ' + url + '  |  ' + str(counter == commit_counter),
            #                            extra={'url': url, 'commit': counter == commit_counter})


num_of_extractors = 2
num_of_parsers = 1

for i in range(0, num_of_extractors):
    thread = Thread(target=extract_link_from_front_queue_and_put_in_back_queue)
    # thread.daemon = True
    thread.start()
    hosts_refresh_rates[thread.ident] = defaultdict(int)

for i in range(0, num_of_parsers):
    thread = Thread(target=fetch_and_parse)
    # thread.daemon = True
    thread.start()

Timer(5, reorder_front_queues).start()
