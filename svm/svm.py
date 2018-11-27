#!/usr/bin/env python3

# https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html

import argparse
import json
import math
import random
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import time

from progress import end_progress, progress, start_progress
from sklearn import svm
from sklearn.model_selection import cross_val_score

import cache

BLACKLIST_WORDS = []


def load_blacklist_words(filename):
    global BLACKLIST_WORDS
    with open(filename) as f:
        BLACKLIST_WORDS = f.readlines()
    BLACKLIST_WORDS = [x.strip() for x in BLACKLIST_WORDS]


def run_tests(data, label, size, split, kernel, gamma, coef):
    print("\n\nRunning tests")
    print("=============")
    print("Kernel:", kernel)
    print("Gamma:", gamma)
    print("Coef:", coef)
    print("=============\n")

    model = svm.SVC(C=coef, kernel=kernel, gamma=gamma)

    if split > 1:
        print("> Training model using {} data (Cross-validation)".format(size))
        scores = cross_val_score(model, data, label, cv=split)

        print("=====================================")
        print("Avg. Accuracy: {0:.2f}%\n".format(scores.mean() * 100))
    else:
        print("> Training model using {} data".format(size))
        model.fit(data, label)

        cache_name = "model/gender_classifier_{}.p".format(size)
        print("Caching trained model into {}".format(cache_name))
        cache.cache_model(model, cache_name)

    return model


def main(args):
    start_time = time.time()
    print("Running SVM Classifier")

    print("Reading blacklist words file")
    load_blacklist_words("../data/blacklist.txt")

    print("Reading raw gender-comment data")
    with open('../data/male-comments.json', 'r') as f:
        male_comment = json.load(f)
    with open('../data/female-comments.json', 'r') as f:
        female_comment = json.load(f)

    # Lower case all comments
    male_comment = [[x[0], x[1].lower()] for x in male_comment]
    female_comment = [[x[0], x[1].lower()] for x in female_comment]

    # Filter blacklisted words in comments
    male_comment = [[x[0], x[1]] for x in male_comment if
        all(c not in BLACKLIST_WORDS for c in x[1].split(' '))]
    female_comment = [[x[0], x[1]] for x in female_comment if
        all(c not in BLACKLIST_WORDS for c in x[1].split(' '))]

    random.shuffle(male_comment)
    random.shuffle(female_comment)
    print("Loaded {} male and {} female comments".format(len(male_comment), len(female_comment)))

    female_ratio = (1.0 - args.male_female_ratio)
    if args.limit != -1:
        print("Limiting male and female comments to {} male and {} female ({} total)".format(
            int(args.limit * args.male_female_ratio), int(args.limit * female_ratio), args.limit))
        try:
            del male_comment[int(args.limit * args.male_female_ratio):]
            del female_comment[int(args.limit * female_ratio):]
        except:
            print("Not enough male/female comments data")
            sys.exit(1)

    gender_comment = []
    for idx, data in enumerate(male_comment):
        data[1] = data[1].lower()
        gender_comment.append(data)
    for idx, data in enumerate(female_comment):
        data[1] = data[1].lower()
        gender_comment.append(data)
    random.shuffle(gender_comment)

    list_of_words = set()
    for data in gender_comment:
        list_of_words.update(data[1].split(' '))
    list_of_words = list(list_of_words)
    word_count = len(list_of_words)

    if args.cache:
        cache.cache_list_of_words(list_of_words)

    print("Total of {} words found\n".format(word_count))

    data = []
    label = []
    total = len(gender_comment)
    start_progress("Processing {} raw gender-comment data".format(total))
    for i, j in enumerate(gender_comment):
        if j[0] == 'female':  # Label for female = 0, and male = 1
            label.append(0)
        else:
            label.append(1)

        wc = {}
        for word in j[1].split():
            if word in wc:
                wc[word] += 1
            else:
                wc[word] = 1

        d = []
        for idx in range(word_count):
            count = 0
            if list_of_words[idx] in wc:
                count = wc[list_of_words[idx]]
            d.append(count)
        data.append(d)

        progress((i + 1) / total * 100)
        if i == total:
            break
    end_progress()

    if args.cache:
        cache.cache_data_and_label(data, label, word_count)

    run_tests(data, label, total, args.split, args.kernel, args.gamma, args.coef)

    print("Elapsed time: {0:.2f}s".format(time.time() - start_time))


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="limit",
        default=-1,
        type=int,
        help="Limit processed data, equal male and female comments")

    parser.add_argument(
        "-s",
        "--split",
        action="store",
        dest="split",
        default=1,
        type=int,
        help="Split test and training data, cross-validation")

    parser.add_argument(
        "-r",
        "--male-female-ratio",
        action="store",
        dest="male_female_ratio",
        default=0.5,
        type=float,
        help="Male to female ratio")

    parser.add_argument(
        "-c",
        "--cache",
        action="store_true",
        dest="cache",
        default=False,
        help="Cache processed raw data")

    parser.add_argument(
        "-o",
        "--coef",
        action="store",
        dest="coef",
        default=10,
        type=int,
        help="Kernel coefficient for ‘rbf’, ‘poly’ and ‘sigmoid’")

    parser.add_argument(
        "-g",
        "--gamma",
        action="store",
        dest="gamma",
        default=1,
        type=int,
        help="Gamma value")

    # Specifies the kernel type to be used in the algorithm
    # Must be one of ‘linear’, ‘poly’, ‘rbf’, ‘sigmoid’, ‘precomputed’ or a
    # callable. If none is given, ‘rbf’ will be used
    parser.add_argument(
        "-k",
        "--kernel",
        action="store",
        dest="kernel",
        default="rbf",
        help="Specifies the kernel type to be used in the algorithm")

    args = parser.parse_args()
    main(args)
