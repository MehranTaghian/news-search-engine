import re


class Tokenizer():
    def __init__(self):
        pass

    def tokenize_words(self, doc_string):
        token_list = doc_string.strip().split()
        token_list = [x.strip("\u200c") for x in token_list if len(x.strip("\u200c")) != 0]
        return token_list

    def tokenize_sentences(self, doc_string):
        #finding the numbers
        pattern = r"[-+]?\d*\.\d+|\d+"
        nums_list = re.findall(pattern, doc_string)
        doc_string = re.sub(pattern, 'floatingpointnumber', doc_string)

        pattern = r'([!\.\?؟]+)[\n]*'
        suse = re.findall(pattern, doc_string)
        doc_string = re.sub(pattern, '\t\t', doc_string)

        pattern = r':\n'
        suse = re.findall(pattern, doc_string)
        doc_string = re.sub(pattern, '\t\t', doc_string)

        pattern = r';\n'
        suse = re.findall(pattern, doc_string)
        doc_string = re.sub(pattern, '\t\t', doc_string)

        pattern = r'؛\n'
        suse = re.findall(pattern, doc_string)
        doc_string = re.sub(pattern, '\t\t', doc_string)

        pattern = r'[\n]+'
        doc_string = re.sub(pattern, '\t\t', doc_string)

        for number in nums_list:
            pattern = 'floatingpointnumber'
            doc_string = re.sub(pattern, number, doc_string, 1)

        doc_string = doc_string.split('\t\t')
        return doc_string
