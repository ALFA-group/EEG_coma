"""
Utils for handling ABP datasets.

"""

import numpy as np
import pickle
from math import ceil

def sample_dataset_and_queries(filename, positive_ratio, n_queries):
    """
    From file filename pickle a dataset with the given rate of positives
    and n_queries random queries which will not be in the dataset.
    The dataset (and queries) format is a (point as numpy array, label) list.

    :param filename: the name of the file
    :param positive_ratio: the chosen rate of positives (e.g., 0.2)
    :return: nothing
    """

    positives = []
    negatives = []

    with open("datasets/" + filename, "r") as file:
        for line in file:
            split_label = line.split(" - ")
            point_string = split_label[0].split(" ")
            clabel = int(split_label[1])
            point = np.array([float(x) for x in point_string])

            if clabel == 0:
                negatives.append((point, clabel))
            else:
                positives.append((point, clabel))

    pos = len(positives)
    neg = len(negatives)
    n = pos + neg

    # Permute both positive and negatives.
    positives_order = np.random.permutation(len(positives))
    negatives_order = np.random.permutation(len(negatives))

    if positive_ratio > float(pos)/n:
        neg = ceil(float(pos)/positive_ratio - pos)
        n = pos + neg
        negatives_order = negatives_order[:neg]

    query_indices = np.sort(np.random.choice(n, size=n_queries, replace=False))
    # Enforce at least 20 positives are in the set.
    positive_queries = len([i for i in query_indices if i < len(positives)])
    while positive_queries <= 20:
        query_indices = np.sort(np.random.choice(n, size=n_queries, replace=False))
        positive_queries = len([i for i in query_indices if i < len(positives)])

    queries = []
    dataset = []
    counter = 0
    query_index = 0

    for i in positives_order:
        cpositive = positives[i]
        if query_index < n_queries:
            if counter == query_indices[query_index]:
                queries.append(cpositive)
                counter += 1
                query_index += 1
                continue
        dataset.append(cpositive)
        counter += 1

    for i in negatives_order:
        cnegative = negatives[i]
        if query_index < n_queries:
            if counter == query_indices[query_index]:
                queries.append(cnegative)
                counter += 1
                query_index += 1
                continue
        dataset.append(cnegative)
        counter += 1


    with open("datasets/" + filename[:len(filename) - 5] + "-dataset.pickle", 'wb') as file:
        pickle.dump(dataset, file)

    with open("datasets/" + filename[:len(filename) - 5] + "-queries.pickle", 'wb') as file:
        pickle.dump(queries, file)


def undersample_dataset(filename, undersample_ratio):
    """
    Performs stratified sampling with rate undersample_ratio on the already pickled dataset filename.

    :param filename: name of the dataset
    :param undersample_ratio: rate of undersampling (e.g., 0.2)
    :return: nothing
    """

    with open("datasets/" + filename[:len(filename) - 5] + "-dataset.pickle", 'rb') as file:
        dataset = pickle.load(file)

    positives = []
    negatives = []

    for pair in dataset:
        if pair[1] == 1:
            positives.append(pair)
        else:
            negatives.append(pair)

    pos = int(len(positives)*undersample_ratio)
    neg = int(len(negatives) * undersample_ratio)

    pos_indices = np.sort(np.random.choice(len(positives), size=pos, replace=False))
    neg_indices = np.sort(np.random.choice(len(negatives), size=neg, replace=False))

    output = []
    for i in pos_indices:
        output.append(positives[i])
    for i in neg_indices:
        output.append(negatives[i])

    with open("datasets/" + filename[:len(filename) - 5] + "{}-dataset.pickle".format(undersample_ratio), 'wb') as file:
        pickle.dump(output, file)

if __name__ == "__main__":

    filename = "ABP-AHE-lag5m-cond5m-withgaps.data"

    #sample_dataset_and_queries(filename, 0, 2000, 1)

    ratios = [4.0/5, 3.0/5, 2.0/5, 1.0/5]
    for ratio in ratios:
        undersample_dataset(filename, ratio)