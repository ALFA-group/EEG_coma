'''
    File containing scripts to plot the results of multinode execution.
'''

import os
from script_utils import *
import matplotlib
from tabulate import tabulate

def plot_distributed_gaussian_test():
    # for now use only data on middleware.
    # This is a weak scaling plot.

    worker_list = [1, 2, 4]
    #cores = [8, 24]
    core = 24
    #n_list = [100000, 200000, 400000]
    n_lists = [[100000, 200000, 400000], [1000000, 2000000, 4000000]]


    # Plot data on middleware.
    folder = "../results/distributed/"
    basename = "distributed-gaussian100x{}_scaling_test-{}nodes-{}cores.txt"

    table_y = []
    queries_y = []
    for index in range(len(n_lists)):
        n_list = n_lists[index]
        if index == 0:
            basesize = 100000
        else:
            basesize = 1000000

        for i in range(len(worker_list)):
            n = n_list[i]
            nodes = worker_list[i]

            filename = folder + basename.format(n, nodes, core)
            table, queries = get_middleware_data(filename)
            table_y.append(table)
            queries_y.append(queries)

        # Plot tables.
        custom_plot(0, worker_list, table_y, table_y, "Number of nodes (nu)", "Time [s]", "Middleware: Table construction time", False, labelname="n/nu = {}".format(basesize), dotted=True)
        # Plot queries.
        custom_plot(1, worker_list, queries_y, queries_y, "Number of nodes", "Time [s]", "Middleware: Median query time", False, labelname="n/nu = {}".format(basesize), dotted=True)
        queries_y.clear()
        table_y.clear()

    # Plot the median of the data on cores.
    # This is to analyze the effect of network on the measurements (for a single query most of the latency is network).
    folder = "../results/intranode/"
    basename = "distributed-node{}-gaussian100x{}_scaling_test-{}cores.txt"
    table_y = []
    queries_y = []
    for index in range(len(n_lists)):
        n_list = n_lists[index]
        if index == 0:
            basesize = 100000
        else:
            basesize = 1000000

        for i in range(len(worker_list)):
            n = n_list[i]
            nodes = worker_list[i]

            #Iterate on nodes and append their worst case.
            table_list = []
            query_list = []
            for i in range(nodes):
                filename = folder + basename.format(i+1, n, core)
                table_node, queries_node = get_intranode_data(filename, array=True)
                table_list.append(table_node)
                query_list.append(queries_node)

            table_y.append(np.max(np.array(table_list)))
            # Each point is the median of the max query time across nodes (for each query take the slowest node).
            queries_y.append(np.median(np.max(np.array(query_list), axis=0)))

        # Plot tables.
        custom_plot(2, worker_list, table_y, table_y, "Number of nodes", "Time [s]",
                    "Node max: Table construction time", False, labelname="n/nu = {}".format(basesize), dotted=True)
        # Plot queries.
        custom_plot(3, worker_list, queries_y, queries_y, "Number of nodes", "Time [s]",
                    "Median max query time across nodes", False, labelname="n/nu = {}".format(basesize), dotted=True)
        queries_y.clear()
        table_y.clear()

    plt.show()

    return


def plot_abp_scaling():

    # abp-mout125-Lout96-min150-Lin40-alpha0.005-n801725-k10-2nodes-24cores.txt
    #basename = "../results/distributed/abp-mout{}-Lout{}-min{}-Lin{}-alpha{}-n{}-k{}-{}nodes-{}cores.txt"
    basename = "../results/dataparallel/dataparallel-abp-mout{}-Lout{}-min{}-Lin{}-alpha{}-n{}-k{}-{}nodes-{}cores.txt"

    # Strong scaling on nodes.
    m_out_list = [125, 150] #[125, 190]
    L_out_list = [24*3, 120] #24 * 3
    m_in = 1 #90
    L_in = 1 #60
    k = 10
    alpha = 1.0 #0.005

    worker_list = [2, 3, 4, 5]#[1, 2, 3, 4, 5]
    cores = 24 #8
    dataset_sizes = [801725, 1371479]
    n_lists = [[size for i in range(len(worker_list))] for size in dataset_sizes]  # Strong scaling plot.

    array = []
    for index in range(len(n_lists)):
        n_list = n_lists[index]
        m_out = m_out_list[index]
        L_out = L_out_list[index]
        basesize = int(0.2 * dataset_sizes[index])

        for i in range(len(worker_list)):
            n = n_list[i]
            nodes = worker_list[i]

            filename = basename.format(m_out, L_out, m_in, L_in, alpha, n, k, nodes, cores)
            lowCI, median, upCI = get_comparison_CI_middleware(filename)
            array.append((median-lowCI, median, upCI - median))

        # Plot DSLSH.
        custom_plot(index, np.array(worker_list)*cores, [x[1] for x in array], [[x[0] for x in array], [x[2] for x in array]], r'Number of overall processors $\nu p$', "Max. Comparisons",
                    r'Strong scaling $n=$'+"{}".format(n), True, labelname="DSLSH", dotted=True)

        # Plot baseline.
        baseline = n / np.array(worker_list) / cores
        custom_plot(index, np.array(worker_list)*cores, baseline, baseline, r'Number of overall processors $\nu p$', "Max. Comparisons",
                    r'Strong scaling $n=$'+"{}".format(n), False, labelname="PKNN", dotted=True)

        # Print latex table.
        table = np.transpose(np.array([np.array(worker_list)*cores, [x[1]/1000 for x in array], ["[{}, {}]".format(x[1]/1000 - x[0]/1000,x[1]/1000 + x[2]/1000) for x in array], np.array(baseline)/1000, [baseline[ind]/array[ind][1] for ind in range(len(array))], [array[0][1]/x[1] for x in array] ]))
        print(tabulate(table, tablefmt="latex_booktabs", floatfmt=".2f"))


        array.clear()

    # Weak scaling.
    '''
    m_out_list = [190]
    L_out = 24 * 3
    m_in = 90
    L_in = 60
    k = 10
    alpha = 0.005

    worker_list = [1, 2, 3, 4, 5]
    cores = 8
    dataset_sizes = [1371479]
    ratios = np.array([1.0/5, 2.0/5, 3.0/5, 4.0/5, 1.0])
    n_lists = [[int(ratio) for ratio in size * ratios] for size in dataset_sizes]  # Strong scaling plot.
    print(n_lists)

    array = []
    for index in range(len(n_lists)):
        n_list = n_lists[index]
        m_out = m_out_list[index]
        basesize = int(0.2 * dataset_sizes[index])

        for i in range(len(worker_list)):
            n = n_list[i]
            nodes = worker_list[i]

            filename = basename.format(m_out, L_out, m_in, L_in, alpha, n, k, nodes, cores)
            lowCI, median, upCI = get_comparison_CI(filename)
            array.append((median - lowCI, median, upCI - median))

        # Plot DSLSH.
        custom_plot(index + 5, np.array(worker_list) * 8, [x[1] for x in array],
                    [[x[0] for x in array], [x[2] for x in array]], r'Number of overall processors $\nu p$',
                    "Max. Comparisons",
                    r'Weak scaling $n/\nu=$' + "{}".format(basesize), True, labelname="DSLSH", dotted=True)

        # Plot baseline.
        baseline = np.array(n_list) / np.array(worker_list) / 8
        custom_plot(index + 5, np.array(worker_list) * 8, baseline, baseline, r'Number of overall processors $\nu p$',
                    "Max. Comparisons",
                    r'Weak scaling $n/\nu=$' + "{}".format(basesize), False, labelname="PKNN", dotted=True)
        array.clear()
    '''


def plot_accuracy_scaling_fromfile(filename):
    """
    No two classes of points (lsh and slsh), simple test.
    """

    mcc = np.empty(5)
    datasetsizes = np.empty(5)
    baseline = np.empty(5)

    with open(filename, "r") as file:

        for line in file:

            linesplit = line.split("_")
            if len(linesplit) < 2:
                continue

            if linesplit[0] == "exhaustive":
                nodes = int(linesplit[9][5:])
                baseline[nodes-1] = float(linesplit[4][3:])
                datasetsizes[nodes-1] = int(linesplit[7][1:])

            if linesplit[0][0:4] == "mout":
                if len(linesplit) == 13:
                    nodes = int(linesplit[12][5:])
                    mcc[nodes-1] = float(linesplit[7][3:])

    # Plot DSLSH.
    custom_plot(10, datasetsizes, mcc,
                mcc, r'Dataset size $n$',
                "MCC",
                "MCC with increasing dataset size", False, labelname="DSLSH", dotted=True)

    # Plot baseline.
    custom_plot(10, datasetsizes, baseline, baseline,
                r'Dataset size $n$',
                "MCC",
                "MCC with increasing dataset size", False, labelname="PKNN", dotted=True)


if __name__ == "__main__":

    #plot_distributed_gaussian_test()

    # Plot ABP scaling.
    matplotlib.rcParams.update({'font.size': 20})

    plot_abp_scaling()
    #plot_accuracy_scaling_fromfile("scaling.txt")
    plt.show()
