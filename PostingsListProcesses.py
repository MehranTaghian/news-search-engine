def intersect_posting_lists(list1, list2, distance):
    answer = {}
    docs1 = list1[1]
    docs2 = list2[1]
    d1 = list(docs1.keys())
    d2 = list(docs2.keys())
    p1 = 0
    p2 = 0
    size = 0
    while p1 < len(d1) and p2 < len(d2):
        if d1[p1] == d2[p2]:  ## at the same document
            l = []
            pp1 = docs1[d1[p1]]
            pp2 = docs2[d2[p2]]
            pointer1 = 0
            pointer2 = 0
            while pointer1 < len(pp1):
                while pointer2 < len(pp2):
                    if pp2[pointer2] - abs(pp1[pointer1]) == distance:
                        l.append(pp2[pointer2])
                    elif pp2[pointer2] > pp1[pointer1]:
                        break
                    pointer2 += 1
                while (not len(l) == 0) and l[0] - pp1[pointer1] != distance:
                    l.remove(l[0])
                for ps in l:
                    size += 2
                    if d1[p1] not in answer.keys():
                        answer[d1[p1]] = [ps]
                    else:
                        answer[d1[p1]].extend([ps])
                pointer1 += 1
            p1 += 1
            p2 += 1
        elif d1[p1] < d2[p2]:
            p1 += 1
        else:
            p2 += 1
    return [size, answer]


def merge(list1, list2):
    result = []
    i, j = 0, 0
    while i < len(list1) and j < len(list2):
        if list1[i] == list2[j]:
            result.append(list1[i])
            i += 1
            j += 1
        elif list1[i] > list2[j]:
            j += 1
        else:
            i += 1
    return result


def find_documents_for_simple_terms(pos_index, simple_terms):
    if simple_terms[0] in pos_index:
        posting_list = list(pos_index[simple_terms[0]][1].keys())
    else:
        posting_list = []
    for i in range(1, len(simple_terms)):
        if simple_terms[i] in pos_index:
            posting_list2 = list(pos_index[simple_terms[i]][1].keys())
            posting_list = merge(posting_list, posting_list2)
            # posting_list = set(list(posting_list) + posting_list2)
    return posting_list


def find_documents_for_phrase(phrase, pos_index):
    posting_list = pos_index[phrase[0]]
    distance_between_tokens_in_phrase = 1
    for i in range(1, len(phrase)):
        if phrase[i] in pos_index:
            # print(distance_between_tokens_in_phrase)
            # print(phrase[i])
            posting_list2 = pos_index[phrase[i]]
            posting_list = intersect_posting_lists(posting_list, posting_list2,
                                                   distance_between_tokens_in_phrase)
            distance_between_tokens_in_phrase = 1
        else:
            # print('no')
            distance_between_tokens_in_phrase += 1
    return posting_list
