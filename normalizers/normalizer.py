from normalizers import basic_normalizer as basic_n, correction_normalizer as correction_n, simple_normalizer
from normalizers.stopword_removing import remove_stop_words

from utils import cleanhtml
from parsivar import Normalizer
from parsivar import Tokenizer
from parsivar import FindStems

from normalizers import word_unification

import path

PATH_SEPARATOR = '/'
toker = Tokenizer()
normaler = Normalizer()
stem = FindStems()

pseudo_space = "\u200c"

word_unification.load_lists()


# print(word_unification.l_word_x[3])

## TODO: handle kardan madares, javameh
def normalize(sen):
    # basic_model = basic_n.MohaverekhanBasicNormalizer()
    # correction_model = correction_n.MohaverekhanCorrectionNormalizer()
    simple_model = simple_normalizer.SimpleNormalizer()
    sen = cleanhtml(sen)
    sen = normaler.normalize(sen)
    # sen = basic_model.normalize(sen)
    # sen = correction_model.normalize(sen)
    sen = simple_model.normalize(sen)
    sen = sen.replace('newline', '')
    # print(sen)
    tokens = toker.tokenize_words(sen)
    # print(tokens)
    tokens2 = word_unification.unify(tokens)
    # print(tokens2)

    stemmed = []
    # print(tokens2)
    stop_words_path = path.root_directory + PATH_SEPARATOR + "normalizers" + PATH_SEPARATOR + "stopwords.txt"

    with open(stop_words_path, mode='r', encoding='utf-8') as f:
        lines = f.readlines()
    stopwords = [w.strip() for w in lines]

    for tok in tokens2:
        if tok not in stopwords:
            tok = tok.replace(pseudo_space, ' ')
            tok = tok.replace(' ', '')
            # print(tok)
            t = stem.convert_to_stem(tok)
            stemmed.append(t)

    return stemmed
