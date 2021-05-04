'''
    File containing scripts to plot the results of intranode execution.
'''

import os
from script_utils import *
import matplotlib

def plot_single_gaussian_test():

    cores_list = [1, 2, 4, 8, 16, 24]
    n_list = [5000, 10000, 20000]
    folder = "../results/intranode/"
    basename = "gaussian100x{}_scaling_test-{}cores.txt"

    table_y = []
    queries_y = []
    for n in n_list:
        for cores in cores_list:
            filename = folder + basename.format(n, cores)
            table, queries = get_intranode_data(filename)
            table_y.append(table)
            queries_y.append(queries)

        # Plot tables.
        custom_plot(0, cores_list, table_y, table_y, "Number of cores", "Time [s]", "Table construction time", False, labelname="n = {}".format(n), dotted=True)
        # Plot queries.
        custom_plot(1, cores_list, queries_y, queries_y, "Number of cores", "Time [s]", "Median query time", False, labelname="n = {}".format(n), dotted=True)
        queries_y.clear()
        table_y.clear()

    plt.show()

    return


def plot_comparisonimbalance_test():

    # abp-mout125-Lout96-min150-Lin40-alpha0.005-n801725-k10-24cores.txt
    basename = "../results/strong-scaling-analysis/dataparallel-abp-mout{}-Lout{}-min{}-Lin{}-alpha{}-n{}-k{}-{}cores.txt"

    m_out_list = [125,  190]
    L_out = 24 * 3
    m_in = 90
    L_in = 60
    k = 10
    alpha = 0.005

    cores = [1, 4, 8, 16, 24]
    n_list = [801725, 1371479]

    maxarray = []
    avgarray = []
    minarray = []
    for index in range(len(n_list)):
        n = n_list[index]
        m_out = m_out_list[index]

        for ccores in cores:
            filename = basename.format(m_out, L_out, m_in, L_in, alpha, n, k, ccores)
            lowCI, median, upCI = get_comparison_CI_node(filename, type="max")
            maxarray.append((median - lowCI, median, upCI - median))
            lowCI, median, upCI = get_comparison_CI_node(filename, type="avg")
            avgarray.append((median - lowCI, median, upCI - median))
            lowCI, median, upCI = get_comparison_CI_node(filename, type="min")
            minarray.append((median - lowCI, median, upCI - median))

        # Plot max.
        custom_plot(index, np.array(cores), [x[1] for x in maxarray],
                    [[x[0] for x in maxarray], [x[2] for x in maxarray]], r'Number of cores $p$',
                    "Comparisons",
                    r'Intra-node strong scaling $n=$' + "{}".format(n), True, labelname="Max comparisons", dotted=True)

        # Plot max.
        custom_plot(index, np.array(cores), [x[1] for x in avgarray],
                    [[x[0] for x in avgarray], [x[2] for x in avgarray]], r'Number of cores $p$',
                    "Comparisons",
                    r'Intra-node strong scaling $n=$' + "{}".format(n), True, labelname="Avg comparisons", dotted=True)

        # Plot max.
        custom_plot(index, np.array(cores), [x[1] for x in minarray],
                    [[x[0] for x in minarray], [x[2] for x in minarray]], r'Number of cores $p$',
                    "Comparisons",
                    r'Intra-node strong scaling $n=$' + "{}".format(n), True, labelname="Min comparisons", dotted=True)

        print(maxarray[0][1]/np.array(maxarray))
        maxarray.clear()
        avgarray.clear()
        minarray.clear()

    plt.show()


def plot_strongscaling_runtime():

    # abp-mout125-Lout96-min150-Lin40-alpha0.005-n801725-k10-24cores.txt
    basename = "../results/strong-scaling-analysis/-dataparallel-abp-mout{}-Lout{}-min{}-Lin{}-alpha{}-n{}-k{}-{}cores.txt"

    # Exhaustive baseline.
    bas_lowCI, bas_median, bas_upCI = get_querytime_CI_node(
        "../results/intranode/exhaustive-abp-partial30x803725_scaling_test-24cores.txt")

    m_out_list = [125,  190]
    L_out = 24 * 3
    m_in = 90
    L_in = 60
    k = 10
    alpha = 0.005

    cores = [1, 4, 8, 16, 24]
    n_list = [801725, 1371479]

    array = []
    for index in range(len(n_list)):
        n = n_list[index]
        m_out = m_out_list[index]

        for ccores in cores:
            filename = basename.format(m_out, L_out, m_in, L_in, alpha, n, k, ccores)
            lowCI, median, upCI = get_querytime_CI_node(filename)
            array.append((median - lowCI, median, upCI - median))

        # Plot max.
        custom_plot(index, np.array(cores), [x[1] for x in array],
                    [[x[0] for x in array], [x[2] for x in array]], r'Number of cores $p$',
                    "Query time [s]",
                    r'Intra-node strong scaling $n=$' + "{}".format(n), True, labelname="DSLSH", dotted=True)

        custom_plot(index, np.array(cores), [bas_median for x in range(len(cores))],
                    [[bas_lowCI for x in range(len(cores))], [bas_upCI for x in range(len(cores))]],
                    r'Number of cores $p$',
                    "Query time [s]",
                    r'Intra-node strong scaling $n=$' + "{}".format(n), True, labelname = "Sequential sklearn K-NN", dotted = False
        )

        print(array)
        array.clear()


    plt.show()


if __name__ == "__main__":

    matplotlib.rcParams.update({'font.size': 20})

    #plot_single_gaussian_test()


    plot_comparisonimbalance_test()
    #plot_strongscaling_runtime()
