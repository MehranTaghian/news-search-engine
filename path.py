import os

root_directory = os.path.dirname(__file__)

mohaverekhan_parsed_dir = os.path.join(root_directory, 'normalizers\mohaverekhan_parsed.pkl')
python_objects = os.path.join(root_directory, "Python_Objects")

FIRST_DATASET_DIR = 'Data/data.xlsx'
FIRST_DATASET_POS_INDEX_DIR = 'Python_Objects/pos_index_FIRST.pkl'
SECOND_DATASET_DIR = 'Data/IR-F19-Project02-14k.csv'
SECOND_DATASET_POS_INDEX_DIR = 'Python_Objects/pos_index_SECOND.pkl'
NUMBER_OF_DOCS_FOR_FIRST_DATASET = 1729
NUMBER_OF_DOCS_FOR_SECOND_DATASET = 7744

clustering_result_path = python_objects + '/k_40_iter_13_THIRD.pkl'

pandas_matrix = python_objects + '/pandas_matrix.pkl'
labels_excel = 'Data/labels.xlsx'
knn_1000_docs = python_objects + '/knn_1000docs.pkl'
knn_y = python_objects + '/knn_y'
knn_termids = python_objects + '/knn_termids.pkl'
knn_all_terms = python_objects + '/knn_all_trems.pkl'
knn_sparse_matrix = python_objects + '/knn_sparsemat.npz'

knn_result = python_objects + '/knn_result_k5.pkl'
bayesian_result = python_objects + '/bayes_result.pkl'

labeled_data_tf_idf_relative_path = python_objects + '/type_1_weighting_scheme_labeled_data.pkl'
labeled_data_positional_index_path = python_objects + '/labeled_data_pos_index.pkl'
labels_path = os.path.join(root_directory, 'labeled_data', 'labels.csv')

closest_docs = python_objects + 'closest_ones.pkl'
close_ones = root_directory + '/close_ones'
