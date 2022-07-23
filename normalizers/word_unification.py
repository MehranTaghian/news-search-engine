import path
PATH_SEPARATOR = '/'
pseudo_space = "\u200c"

one_word_x = []

one_word_y = []

two_word_x = []
two_word_y = []

three_word_x = []
three_word_y = []

four_word_x = [[]]
four_word_y = []
five_word_x = [[]]
five_word_y = []
six_word_x = [[]]
six_word_y = []

l_word_x = [0, one_word_x, two_word_x, three_word_x, four_word_x, five_word_x, six_word_x]
l_word_y = [0, one_word_y, two_word_y, three_word_y, four_word_y, five_word_y, six_word_y]


def load_lists():
    with open(path.root_directory + PATH_SEPARATOR + "normalizers" + PATH_SEPARATOR + "mokhafaf.txt", encoding='utf-8',
              mode='r') as f:
        lines = f.readlines()
        # print(lines)

        for i in range(int(len(lines) / 2)):
            word = lines[2 * i].replace('\n', '').strip()
            nxt_word = lines[2 * i + 1].replace('\n', '').strip()
            l_word_x[1].append(word)
            l_word_y[1].append(nxt_word)
    with open(path.root_directory + PATH_SEPARATOR + "normalizers" + PATH_SEPARATOR + "multispelling.txt",
              encoding='utf-8', mode='r') as f:
        lines = f.readlines()
        for i in range(int(len(lines) / 2)):
            word = lines[2 * i].replace('\n', '').strip()
            nxt_word = lines[2 * i + 1].replace('\n', '').strip()
            l_word_x[1].append(word)
            l_word_y[1].append(nxt_word)
    with open(path.root_directory + PATH_SEPARATOR + "normalizers" + PATH_SEPARATOR + "addition_stem.txt",
              encoding='utf-8', mode='r') as f:
        lines = f.readlines()
        for i in range(int(len(lines) / 2)):
            word = lines[2 * i].replace('\n', '').strip()
            nxt_word = lines[2 * i + 1].replace('\n', '').strip()
            l_word_x[1].append(word)
            l_word_y[1].append(nxt_word)
    with open(path.root_directory + PATH_SEPARATOR + "normalizers" + PATH_SEPARATOR + "expressions.txt",
              encoding='utf-8', mode='r') as f:
        lines = f.readlines()

        for word in lines:
            splited = word.replace('\n', '').strip().split(' ')
            l = len(splited)
            if l < len(l_word_x):
                if l == 1:
                    splited = splited[0]
                l_word_x[l].append(splited)
                l_word_y[l].append(word.replace('\n', '').replace(' ', pseudo_space))
                get_all_forms(splited)
                # print('all forms',all_forms)
                if l != 1:
                    for form in all_forms:
                        l2 = len(form)
                        # print(form, l2)
                        l_word_x[l2].append(form)
                        l_word_y[l2].append(word.replace('\n', '').replace(' ', pseudo_space))


global all_forms
all_forms = []


def get_all_forms(tokens):
    global all_forms
    all_forms = []
    return get_all_forms_work(tokens[1:], [tokens[0]])


def get_all_forms_work(tokens, prev):
    if len(tokens) == 0:
        all_forms.append(prev)
        return

    p = prev.copy()
    p[-1] = p[-1] + tokens[0]
    get_all_forms_work(tokens[1:], p)
    p = prev.copy()
    p.append(tokens[0])
    get_all_forms_work(tokens[1:], p)


def unify(sen):
    r1 = unification(sen)
    other = ""
    for s in sen:
        other += ' ' + s.replace(pseudo_space, ' ')
    other = other.split()
    r2 = unification(other)
    if r1 == sen and r2 != sen:
        return r2
    else:
        return r1


def unification(sen):
    i = 0
    while i < len(sen):
        if sen[i] in l_word_x[1]:
            sen[i] = l_word_y[1][l_word_x[1].index(sen[i])]
            i += 1
            continue
        get_out = False
        for l in range(2, 4):
            # print('L',l)
            if get_out:
                break
            if i < len(sen) - l + 1:
                for j in range(len(l_word_x[l])):
                    # print("hay")
                    cond = True
                    for k in range(l):
                        # print(sen[i + k], l_word_x[l][j][k])
                        cond = cond and (sen[i + k] == l_word_x[l][j][k])
                    # print(cond)
                    if cond:
                        sen[i] = l_word_y[l][j]
                        for k in range(1, l):
                            sen[i + k] = ""
                        i = i + l - 1
                        get_out = True
                        break
        i += 1
    new_sen = []
    for tok in sen:
        if len(tok) > 0:
            new_sen.append(tok)
    return new_sen
