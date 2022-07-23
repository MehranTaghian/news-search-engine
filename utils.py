import re
import pickle
# import pandas as pd


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def write_to_file(object, name):
    pickle_out = open(name, "wb")
    pickle.dump(object, pickle_out)


def load_file(name):
    pickle_in = open(name, "rb")
    example_dict = pickle.load(pickle_in)
    return example_dict


def read_dataset(filename):
    string_data = []
    if filename.split('.')[1] == 'csv':
        data = pd.read_csv(filename)
    elif filename.split('.')[1] == 'xlsx':
        data = pd.read_excel(filename)
    for index, row in data.iterrows():
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
            print('cjontent', type(content))
            print(content)
            print('summary', type(summary))
            print(summary)
            print('#' * 50)
        string_data.append(str)
    return string_data
