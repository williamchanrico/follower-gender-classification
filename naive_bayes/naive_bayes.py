#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import glob
import io
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from random import shuffle

import nltk
import numpy as np
from nltk import (NaiveBayesClassifier, WordNetLemmatizer, classify,
                  word_tokenize)
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from progress import end_progress, progress, start_progress
import cache

data = []
list_of_gender = []
list_of_words = []
train_data_gender = []

BLACKLIST_WORDS = []


def load_blacklist_words(filename):
    global BLACKLIST_WORDS
    with open(filename) as f:
        BLACKLIST_WORDS = f.readlines()
    BLACKLIST_WORDS = [x.strip() for x in BLACKLIST_WORDS]

def read_file(filename):
    load_blacklist_words("../data/blacklist.txt")

    with open(filename, "r", encoding="utf-8") as f:
        file = json.load(f)
        if str(file["gender"]) == "False":  # Invalid gender
            return

    for _, comment in enumerate(file["comments"]):
        words_in_comment = word_tokenize(comment["text"].lower())

        valid = True
        for word in BLACKLIST_WORDS:
            if word.lower() in words_in_comment:
                valid = False
                break

        if valid:
            data.append((file["gender"], comment["text"].lower()))

    shuffle(data)


def naive_bayes(cache_model):
    print("Running Naive-Bayes Classifier Training")

    idx = 0
    total = len(data)
    start_progress("Pre-processing {} of data".format(total))
    for gender, comment in data:
        idx += 1
        word_exist = {}
        word_not_exist = {}

        if gender not in list_of_gender:
            list_of_gender.append(gender)

        for word in word_tokenize(comment):
            word_exist[word] = True
            word_not_exist[word] = False

            if word not in list_of_words:
                list_of_words.append(word)

        for gen in list_of_gender:
            if gen == gender:
                train_data_gender.append((word_exist, gen))
            else:
                train_data_gender.append((word_not_exist, gen))
        progress(idx / total * 100)
    end_progress()
    print("\nFinished pre-processing ({} data)".format(total))

    print("Training {} gender data".format(total))
    main_gender_classifier = NaiveBayesClassifier.train(train_data_gender)

    if cache_model:
        cache.cache_model(main_gender_classifier, 'model/gender_classifier_{}.p'.format(total))

    print("Cross validation")
    average_accuracy = 0
    size = len(train_data_gender)

    for i in range(1, 9):
        test_set = train_data_gender[round((i - 1) * size / 8): round((i) * size / 8)]
        training_set = train_data_gender[0: round((i - 1) * size / 8)]
        training_set.extend(train_data_gender[round((i) * size / 8):])

        gender_classifier = NaiveBayesClassifier.train(training_set)

        print("Test-{0}: {1:.2%}".format(i, classify.accuracy(gender_classifier, test_set)))
        average_accuracy += classify.accuracy(gender_classifier, test_set)
    average_accuracy /= 8

    print("Average accuracy: " + "{0:.2%}\n".format(average_accuracy))

    return main_gender_classifier

def nb_classify(classifier, text=""):
    text_dict = {}

    if text == "":
        print("Classifying using trained Naive-Bayes model")
        print("===========================================\n")

        while True:
            text = input("Insert phrase >> ").lower()
            if text in ["quit", "exit"]:
                return None

            text_dict.clear()
            for word in word_tokenize(text):
                text_dict[word.lower()] = True
            answer = classifier.classify(text_dict)
            print("Guessed Gender: '{}'\n".format(answer))
    else:
        text_dict.clear()
        for word in word_tokenize(text):
            text_dict[word.lower()] = True
        answer = classifier.classify(text_dict)

        return 0 if answer == "female" else 1


def main(args):
    print("Running Naive-Bayes Classifier\n")
    if args.model != "":
        print("Loading model file: {}\n".format(args.model))
        classifier = cache.load_model(args.model)
    else:
        filenames = glob.glob("../data/raw_comments/*.json")
        shuffle(filenames)

        total = len(filenames)
        start_progress("Reading {} user(s) data".format(total))

        for index, filename in enumerate(filenames):
            progress((index + 1) / total * 100)
            read_file(filename)

        end_progress()

        print("\nFinished reading data")
        print("Total number of user: " + str(len(filenames)))
        print("Total number of comments: " + str(len(data)) + "\n")

        if args.limit != -1:
            print("Limiting number of comments: {}".format(args.limit))
            del data[args.limit:]

        classifier = naive_bayes(args.cache_model)

    nb_classify(classifier)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-l",
        "--limit",
        action="store",
        dest="limit",
        default=-1,
        type=int,
        help="Limit processed data")

    parser.add_argument(
        "-m",
        "--model",
        action="store",
        dest="model",
        default="",
        type=str,
        help="Specify model file (pickle format)")

    parser.add_argument(
        "-c",
        "--cache",
        action="store_true",
        dest="cache_model",
        default=False,
        help="Cache trained mode data")

    args = parser.parse_args()
    main(args)
