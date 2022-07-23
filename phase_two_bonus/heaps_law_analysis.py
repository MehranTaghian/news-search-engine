import math

from main import PATH_SEPARATOR
from normalizers.normalizer import normalize
import numpy as np
import matplotlib.pyplot as plt
from utils import read_dataset, write_to_file, load_file

import path

heaps_law_data_ms = path.python_objects + PATH_SEPARATOR + 'heaps_ms.pkl'
heaps_law_data_ts = path.python_objects + PATH_SEPARATOR + 'heaps_ts.pkl'


def save_freqs():
    vocab = set()
    ms = []
    ts = []
    tokes_nums = 0
    data = read_dataset(path.SECOND_DATASET_DIR)
    for i in range(len(data)):
        str = data[i]
        tokens = normalize(str)
        tokes_nums += len(tokens)
        for pos, term in enumerate(tokens):
            vocab.add(term)
        if i % 10 == 0:
            ts.append(math.log10(tokes_nums))
            ms.append(math.log10(len(list(vocab))))
    write_to_file(ts, heaps_law_data_ts)
    write_to_file(ms, heaps_law_data_ms)


# save_freqs()
# print("done")
ms = load_file(heaps_law_data_ms)
ts = load_file(heaps_law_data_ts)
print(ts[-1])
print(ms[-1])
# Create data
N = len(ms)
x = np.array(ts)
y = np.array(ms)
colors = (0, 0, 0)
area = np.pi * 3

# Plot

m1 = ms[int(len(ms) / 4)]
t1 = ts[int(len(ms) / 4)]

m2 = ms[int(len(ms) * (3 / 4))]
t2 = ts[int(len(ms) * (3 / 4))]

b = (m2 - m1) / (t2 - t1)
logk = m2 - b * t2


def func(x):
    return np.array([b * t + logk for t in x])


plt.scatter(x, y, s=area, c=colors, alpha=0.5)
plt.title('Heaps Law')
plt.ylabel('Log Vocab')
plt.xlabel('Log Tokens')
x = np.linspace(3, 6, 170)
plt.plot(x, func(x))
plt.show()
