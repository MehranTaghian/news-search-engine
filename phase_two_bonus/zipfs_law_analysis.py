import pandas as pd

from main import PATH_SEPARATOR
from making_dicts import make_dict
import sys
import utils
import xlrd
import math

from normalizers.normalizer import normalize
from utils import read_dataset
import path

freqs_name = path.python_objects + PATH_SEPARATOR + "second_Dataset_freqs.pkl"


def save_freqs(data):
    data = read_dataset(data)
    d = {}
    for i in range(len(data)):
        str = data[i]
        tokens = normalize(str)
        for pos, term in enumerate(tokens):
            if term in d:
                d[term] = d[term] + 1
            else:
                d[term] = 1

    freqs = sorted(list(d.values()), reverse=True)
    utils.write_to_file(freqs, freqs_name)


# save_freqs(path.SECOND_DATASET_DIR)
print('Done')
freqs = pos_index = utils.load_file(freqs_name)
law = [freqs[0] / i for i in range(1, len(freqs) + 1)]
import numpy as np
import matplotlib.pyplot as plt

plt.scatter(range(1, 501), freqs[:500], alpha=0.5)
plt.plot(range(1, 501), law[:500], alpha=0.5)
plt.title('Zipfs Law')
plt.ylabel('freq')
plt.xlabel('rank')

plt.show()
