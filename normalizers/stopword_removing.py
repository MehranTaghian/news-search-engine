import path

PATH_SEPARATOR = '/'
stop_words_path = path.root_directory + PATH_SEPARATOR + "normalizers" + PATH_SEPARATOR + "stopwords.txt"


def remove_stop_words(sen):
    with open(stop_words_path, mode='r', encoding='utf-8') as f:
        lines = f.readlines()
    stop_words = [w.strip() for w in lines]
    splited = sen.split(' ')
    res = ''
    for tok in splited:
        if tok not in stop_words:
            res += tok
            res += ' '
    return res[:-1]
