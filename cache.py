#!/usr/bin/env python3
#
# Copyright (c) 2018-2020 William Chanrico.
#
# This file is part of follower-gender-classification
# (see https://github.com/williamchanrico/follower-gender-classification).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import time
import _pickle as pickle
"""
Processed raw data cache format

[data] is a file where each line is of the form:

    [M] [term_1]:[count] [term_2]:[count] ...  [term_N]:[count]

where [M] is the number of unique terms in the document, and the [count]
associated with each term is how many times that term appeared in the document.

[label] is a file where each line is the corresponding label for [data].
The labels must be 0, 1, ..., C-1, if we have C classes.

Trained models are saved in pickle format
"""

TIMESTAMP = time.strftime("%H%M%S")


def cache_data(data, term_count, filename):
    filename = filename + "-" + TIMESTAMP + ".dat"

    with open(filename, "w") as f:
        for doc in data:
            f.write(str(term_count))
            for idx, count in enumerate(doc):
                f.write(" " + str(idx) + ":" + str(count))
            f.write("\n")


def cache_label(label, filename):
    filename = filename + "-" + TIMESTAMP + ".dat"

    with open(filename, "w") as f:
        for l in label:
            f.write(str(l) + "\n")


def cache_model(data, filename):
    print("Saving trained model into {}\n".format(filename))
    with open(filename, "wb") as save_file:
        pickle.dump(data, save_file)


def cache_data_and_label(data, label, word_count):
    print("Caching raw data... [suffix: {}]".format(TIMESTAMP))
    cache_label(label, "label")
    if type(data) is list:
        cache_data(data, word_count, "data")
    else:
        cache_model(data, "data-matrix-{}.dat".format(TIMESTAMP))


def cache_list_of_words(list_of_words):
    filename = "list-of-words-{}.p".format(len(list_of_words))
    print("Caching list of words into {}".format(filename))

    with open(filename, "wb") as save_file:
        pickle.dump(list_of_words, save_file)


def load_pickle(file):
    with open(file, "rb") as f:
        data = pickle.Unpickler(f).load()
    return data
