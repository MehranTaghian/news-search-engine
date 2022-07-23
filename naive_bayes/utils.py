import pickle
import numpy as np
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
import path

train_data_fraction = 1.0
classifier = None
mapper = None


class Mapper:
    def __init__(self):
        self.mapping = {}
        self.mapping_current_index = 0

    def get_term_id(self, term):
        if term in self.mapping.keys():
            return self.mapping[term]
        else:
            self.mapping[term] = self.mapping_current_index
            self.mapping_current_index += 1
            return self.mapping[term]


def load_pkl(path):
    file = open(path, "rb")
    return pickle.load(file)


def read_labels(path):
    data = pd.read_csv(path, sep='\n').to_numpy()
    return data.ravel()


def display_statistics(classifier):
    print('class_count_ :', classifier.class_count_)
    print('class_log_prior_ :', classifier.class_log_prior_)
    print('classes_ :', classifier.classes_)
    print('n_features_ :', classifier.n_features_)
    # print('feature_log_prob_ :', classifier.feature_log_prob_)


def train(train_data, labels):
    clf = MultinomialNB()
    clf.fit(train_data, labels)
    # display_statistics(clf)
    return clf


def predict(test_data):
    global classifier
    return classifier.predict(test_data)


def convert_tf_idf_dictionary_to_naive_bayes_input(tf_idf_vector):
    new_vector = np.ndarray(shape=(1, number_of_terms), dtype=np.float)
    new_vector.fill(0)

    for term, score in tf_idf_vector.items():
        if term in mapper.mapping.keys():
            new_vector[0, mapper.mapping[term]] = score
    return new_vector


def build_classifier():
    labeled_data_tf_idf = load_pkl(path=path.labeled_data_tf_idf_relative_path)
    labeled_data_positional_index = load_pkl(path=path.labeled_data_positional_index_path)
    number_of_documents = len(labeled_data_tf_idf.keys())
    global mapper, classifier, number_of_terms
    number_of_terms = len(labeled_data_positional_index.keys())
    X = np.ndarray(shape=(number_of_documents, number_of_terms), dtype=np.float)
    X.fill(0)
    mapper = Mapper()

    for doc_id, tf_idf_list in labeled_data_tf_idf.items():
        for term, score in tf_idf_list.items():
            id_ = mapper.get_term_id(term)
            X[doc_id, id_] = score

    samples, features = X.shape
    f = int(samples * train_data_fraction)
    train_data = X[:f]
    test_data = X[f:]
    Y = read_labels(path.labels_path)
    classifier = train(train_data=train_data, labels=Y[:f])
    # print('accuracy on train dataset: ', classifier.score(train_data, Y[:f]))
    # print('accuracy on test dataset: ', classifier.score(test_data, Y[f:]))
    # print("-" * 70, end='\n')


def predict_all_and_save():
    import utils
    res = [[] for i in range(8)]

    doc_vector = utils.load_file(f'Python_Objects/type_3_weighting_scheme_THIRD_normalized.pkl')
    build_classifier()
    for docid in doc_vector.keys():
        a = convert_tf_idf_dictionary_to_naive_bayes_input(doc_vector[docid])
        clas = predict(a)[0]
        # print(clas)
        res[clas - 1].append(docid)
        if docid % 10000 == 0:
            print(docid)

    utils.write_to_file(res, path.bayesian_result)
