
def make_dict(words,add_unk=False):
    words = list(set(words))
    if (add_unk):
        words = ['unk'] + words
    word2idx = {}
    idx2word = {}
    vocabs = []
    indexes = []
    counter = 0
    for i, w1 in enumerate(words):
        vocabs.append(w1)
        flag = False
        if (not flag):
            indexes.append(counter)
            counter += 1
    # print(indexes)
    for i in range(len(vocabs)):
        # print(vocabs[i], indexes[i])
        word2idx[vocabs[i]] = indexes[i]
        if indexes[i] not in idx2word:
            idx2word[indexes[i]] = vocabs[i]
    return word2idx, idx2word
