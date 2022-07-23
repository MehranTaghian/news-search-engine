from normalizers import cache

pseudo_space = "\u200c"


## TODO: half space unicode ????
class SimpleNormalizer:

    def __init__(self):
        self.from_begin = ['می']
        self.at_end = ['تر', 'ها', 'ترین', 'های','ای','ایم','اید','ام']
        self.strict = ['ها', 'های']

    def normalize(self, text_content):
        # print(text_content)
        # print(text_content)
        splitted = self.split(text_content).split()
        # print(splitted)
        result = ""
        flag = True
        for i in range(len(splitted)):
            if flag:
                if splitted[i] in self.from_begin:
                    # result += " "
                    continue
                    # result += splitted[i]
                    # if i + 1 < len(splitted):
                        # result += pseudo_space
                        # result += splitted[i + 1]

                    # flag = False
                elif splitted[i] in self.at_end:
                    # result += pseudo_space
                    # result += splitted[i]
                    continue
                else:
                    result += " "
                    result += splitted[i]
            else:
                flag = True
        return result[1:]

    def split(self, text_content):
        splited = text_content.split()
        result = ""
        # print('here',splited)
        for tok in splited:
            if not cache.is_token_valid(tok) or tok[-3:] in self.strict or tok[-2:] in self.strict:
                token = tok
                # print(tok)
                if len(token) >= 2:
                    if token[:2] in self.from_begin:
                        # print('b',token)
                        result += " "
                        result += token[:2]
                        result += " "
                        token = tok[2:]
                if len(token) >= 2:
                    if token[-2:] in self.at_end:
                        # print(token)
                        # print(token[-2:])
                        # print(tok[-2:])
                        result += " "
                        result += token[:-2]
                        result += " "
                        result += tok[-2:]
                    elif len(token) >= 3 and token[-3:] in self.at_end:
                        result += " "
                        result += token[:-3]
                        result += " "
                        result += tok[-3:]
                    elif len(token) >= 4 and token[-4:] in self.at_end:
                        result += " "
                        result += token[:-4]
                        result += " "
                        result += tok[-4:]
                    else:
                        result += " "
                        result += token
            else:
                # print('ook',tok)
                result += " "
                result += tok
        return result[1:]
