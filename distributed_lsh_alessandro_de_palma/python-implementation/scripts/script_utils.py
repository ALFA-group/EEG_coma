'''
    File containing utility functions for the scripts.
'''

import numpy as np
import matplotlib.pyplot as plt
from math import ceil, floor, sqrt
import matplotlib

# xlog is a flag which has to be set to true if the x axis must be logarithmic.
def custom_plot(fignumber, x, y, STD, xlabel, ylabel, title, errorbars, labelname="", dotted=False):

    plt.figure(fignumber)

    if(errorbars):
        if labelname != "":
            myplot = plt.errorbar(x, y, yerr=STD, marker='_', capsize=2, ms=10, mew=2, capthick=1,
                                  linestyle="dotted", label=labelname)
        else:
            myplot = plt.errorbar(x, y, yerr=STD, ecolor='b', marker='_', color='g', capsize=2, ms=10, mew=2, capthick=1,
                     linestyle="dotted")
            if dotted:
                myplot[-1][0].set_linestyle('dotted')
    else:
        if not dotted:
            plt.plot(x, y, marker='x', linestyle="-", label=labelname)
        else:
            plt.plot(x, y, marker='x', linestyle="dashed", label=labelname, ms=10)

    plt.grid(True)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend(loc='best')
    #plt.savefig(figname)


def get_intranode_data(filename, array=False):
    '''
    :param array: if True, return the query array instead of the median.
    :return: the overall table construction time and the median query time.
    '''

    queries = []
    with open(filename, "r") as file:
        for line in file:
            linesplit = line.split(",")

            if linesplit[0] == "tables":
                table = float(linesplit[2]) - float(linesplit[1])

            elif linesplit[0] == "query":
                queries.append(float(float(linesplit[2]) - float(linesplit[1])))

    if array:
        q_out = np.array(queries)
    else:
        q_out = np.median(queries)

    return table, q_out


def get_intranode_query_arrays(filename):
    '''
    :param filename: the name of the file
    :return: a tuple made of as many query timestamp arrays as there are columns in the intranode file
    '''

    arr1 = []
    arr2 = []
    arr3 = []
    arr4 = []
    arr5 = []
    with open(filename, "r") as file:
        for line in file:
            linesplit = line.split(",")

            if linesplit[0] == "query":
                arr1.append(float(linesplit[1]))
                arr2.append(float(linesplit[2]))
                arr3.append(float(linesplit[3]))
                arr4.append(float(linesplit[4]))
                arr5.append(float(linesplit[5]))

    return arr1, arr2, arr3, arr4, arr5


def get_middleware_data(filename, array=False):
    '''

    :param array: if True, return the query array instead of the median.
    :return: the overall table construction time and the median query time.
    '''

    queries = []
    with open(filename, "r") as file:
        for line in file:
            linesplit = line.split(",")

            if linesplit[0] == "tables":
                table = float(linesplit[2]) - float(linesplit[1])

            elif linesplit[0] == "query":
                queries.append(float(float(linesplit[2]) - float(linesplit[1])))

    if array:
        q_out = np.array(queries)
    else:
        q_out = np.median(queries)


    return table, q_out


def median_CI_from_array(array, diff):
    """
    Returns (lower_CI, median, upper_CI) where the CI's are 95% confidence intervals for the median.

    :param array: the array of values to compute them on
    :param diff: a flag for whether CI's should be expressed as a difference from the median.
    :return: (lower_CI, median, upper_CI)
    """

    array.sort()

    n = len(array)
    if n % 2 == 1:
        median = array[int(ceil(n / 2.0))-1]
    else:
        median = (array[int(n / 2)] + array[int(n / 2) - 1]) / 2.0

    # Computation for 95% confidence intervals.
    j = floor((n - 1.96 * sqrt(n)) / 2)
    j = max(0, j)
    k = ceil(1 + (n + 1.96 * sqrt(n)) / 2)
    k = min(n-1, k)

    if not diff:
        return array[j], median, array[k]
    else:
        return median - array[j], median, array[k] - median


def get_querytime_CI_node(filename):

    """
    Given a file return median and CI for the query time from a node log.

    :param filename: the log file's name.
    """

    temp, array = get_intranode_data(filename, array=True)

    return median_CI_from_array(array, False)


def get_comparison_CI_node(filename, type="max"):

    """
    Given a file return median and CI for the number of comparisons from a node log. Assume name is right and get it in mcc tuning.

    :param type: indicates whether to return max avg or min comparisons across processors.
    """

    if type == "max":
        index = 6
    elif type == "avg":
        index = 7
    elif type == "min":
        index = 8

    array = []
    with open(filename, "r") as file:
        for line in file:
            linesplit = line.split(",")

            if linesplit[0] == "query":
                array.append(float(linesplit[index]))

    return median_CI_from_array(array, False)


def get_comparison_CI_middleware(filename):

    """
    Given a file return median and CI for the number of comparisons from a middleware log. Assume name is right and get it in mcc tuning.
    """


    array = []
    with open(filename, "r") as file:
        for line in file:
            linesplit = line.split(",")

            if linesplit[0] == "query":
                array.append(float(linesplit[3]))

    return median_CI_from_array(array, False)


def plot_comparison_histogram_middleware(filename):

    """
    Given a file plot the histogram of the number of comparisons from a middleware log.
    """


    array = []
    with open(filename, "r") as file:
        for line in file:
            linesplit = line.split(",")

            if linesplit[0] == "query":
                array.append(float(linesplit[3]))

    plt.hist(array, color='g', bins=150, normed=False)
    plt.grid()
    plt.xlabel("Number of candidates")
    plt.ylabel("Number of queries")
    plt.title("Number of candidates distribution over queries")

    print(np.median(array))
    print(np.mean(array))

    return

if __name__ == "__main__":

    #filename1 = "dataparallel-abp-mout125-Lout72-min1-Lin1-alpha1.0-n801725-k10-2nodes-24cores.txt"
    #filename2 = "dataparallel-abp-mout125-Lout72-min20-Lin20-alpha5e-05-n801725-k10-2nodes-24cores.txt"

    matplotlib.rcParams.update({'font.size': 20})

    filename1 = "../results/distributed/abp-mout125-Lout120-min120-Lin20-alpha1.0-n801725-k10-2nodes-8cores.txt"
    filename2 = "../results/distributed/abp-mout125-Lout120-min65-Lin60-alpha0.005-n801725-k10-2nodes-8cores.txt"

    plt.figure(1)
    plot_comparison_histogram_middleware(filename1)
    plt.figure(20)
    plot_comparison_histogram_middleware(filename2)

    plt.show()