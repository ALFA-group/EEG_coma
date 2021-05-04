"""
Script to make scatter plots from ABP prediction tuning.

"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from script_utils import get_comparison_CI_middleware

def read_mcc_tuning_file(filename, p, n, nodes, cores):

    lsh = []
    slsh = []

    with open(filename, "r") as file:

        for line in file:

            linesplit = line.split("_")
            if len(linesplit) < 2:
                continue

            if linesplit[0] == "exhaustive":
                baseline = (1, float(linesplit[4][3:]))

            if linesplit[0][0:4] == "mout":

                mcc = float(linesplit[7][3:])
                # mout125_Lout96_min1_Lin20_alpha1.0_acc0.9535_recall0.8_mcc0.40127743952868367_medquery0.05535745620727539_comp5178.5_n801725_k10_slshbase
                # abp-mout125-Lout96-min150-Lin40-alpha0.005-n801725-k10-2nodes-24cores.txt
                filename = "../results/distributed/abp-{}-{}-{}-{}-{}-{}-{}-{}nodes-{}cores.txt".format(linesplit[0], linesplit[1], linesplit[2],
                                                                             linesplit[3], linesplit[4], linesplit[10],
                                                                             linesplit[11].strip(), nodes, cores)
                lowCI, median, uppCI = get_comparison_CI_middleware(filename)

                # Express CI's as differences.
                median = n / median / p
                lowCI = median - n / lowCI / p
                uppCI = n / uppCI / p - median

                if float(linesplit[4][5:]) == 1:
                    if len(linesplit) == 13:
                        slsh_base = ((lowCI, median, uppCI), mcc)
                    else:
                        lsh.append(((lowCI, median, uppCI), mcc))
                else:
                    slsh.append(((lowCI, median, uppCI), mcc))

        return baseline, lsh, slsh, slsh_base


def read_singlelayer_tuning_file(filename, p, n, nodes, cores, dataparallel=False):
    """
    No two classes of points (lsh and slsh), simple test.
    """

    if dataparallel:
        base = "dataparallel"
        folder = "dataparallel"
    else:
        base = ""
        folder = "distributed"

    slsh = []

    with open(filename, "r") as file:

        for line in file:

            linesplit = line.split("_")
            if len(linesplit) < 2:
                continue

            if linesplit[0] == "exhaustive":
                baseline = (1, float(linesplit[4][3:]))

            if linesplit[0][0:4] == "mout":

                mcc = float(linesplit[7][3:])
                # mout125_Lout96_min1_Lin20_alpha1.0_acc0.9535_recall0.8_mcc0.40127743952868367_medquery0.05535745620727539_comp5178.5_n801725_k10_slshbase
                # abp-mout125-Lout96-min150-Lin40-alpha0.005-n801725-k10-2nodes-24cores.txt
                filename = "../results/{}/{}abp-{}-{}-{}-{}-{}-{}-{}-{}nodes-{}cores.txt".format(folder, base, linesplit[0],
                                                                                                        linesplit[1],
                                                                                                        linesplit[2],
                                                                                                        linesplit[3],
                                                                                                        linesplit[4],
                                                                                                        linesplit[10],
                                                                                                        linesplit[
                                                                                                            11].strip(),
                                                                                                        nodes, cores)
                lowCI, median, uppCI = get_comparison_CI_middleware(filename)

                # Express CI's as differences.
                median = n / median / p
                lowCI = median - n / lowCI / p
                uppCI = n / uppCI / p - median

                if len(linesplit) == 13:
                    slsh_base = ((lowCI, median, uppCI), mcc)
                else:
                    slsh.append(((lowCI, median, uppCI), mcc))


        return baseline, slsh, slsh_base


if __name__ == "__main__":

    matplotlib.rcParams.update({'font.size': 20})

    plt.figure(1)
    cores = 8
    nodes = 2
    p = cores*nodes
    n = 803725

    baseline, lsh, slsh, slsh_base = read_mcc_tuning_file("8coresspeedmmcc.txt", p, n, nodes, cores)

    #plt.scatter(baseline[0], baseline[1], c='blue', marker='*', s=150, label="PKNN")
    plt.errorbar(slsh_base[0][1], slsh_base[1], xerr=[[slsh_base[0][0]], [slsh_base[0][2]]], fmt='o', c='green', capsize=4, ms=10, mew=4, capthick=2, elinewidth=2, label="SLSH onset")
    plt.errorbar([e[0][1] for e in lsh], [e[1] for e in lsh], xerr=[[e[0][0] for e in lsh], [e[0][2] for e in lsh]], c='green', fmt='x', capsize=4, ms=10, mew=4, capthick=2, elinewidth=2, label="LSH")
    plt.errorbar([e[0][1] for e in slsh], [e[1] for e in slsh], xerr=[[e[0][0] for e in slsh], [e[0][2] for e in slsh]], c='red', fmt='|', capsize=4, ms=10, mew=4, capthick=2, elinewidth=2, label="SLSH")

    #plt.axvline(x=1)
    plt.legend(loc='best')
    plt.grid()
    plt.ylabel("MCC")
    plt.xlabel("Speed-up to PKNN [n. comparisons]")
    plt.title("Speed vs. MCC trade-off")

    plt.show()

    '''
    plt.figure(2)

    cores = 24
    nodes = 2 #4
    p = cores * nodes
    n = 1371479

    baseline, slsh, slsh_base = read_singlelayer_tuning_file("../results/24cores-2nodes-dataparallel-tuning-55.txt", p, n, nodes, cores, dataparallel=True)

    plt.scatter(baseline[0], baseline[1], c='blue', marker='*', s=150, label="PKNN")
    plt.errorbar(slsh_base[0][1], slsh_base[1], xerr=[[slsh_base[0][0]], [slsh_base[0][2]]], fmt='o', c='green',
                 capsize=4, ms=10, mew=4, capthick=2, elinewidth=2, label="Chosen tradeoff")
    plt.errorbar([e[0][1] for e in slsh], [e[1] for e in slsh], xerr=[[e[0][0] for e in slsh], [e[0][2] for e in slsh]],
                 c='green', fmt='|', capsize=4, ms=10, mew=4, capthick=2, elinewidth=2, label="LSH")

    plt.axvline(x=1)
    plt.legend(loc='best')
    plt.grid()
    plt.ylabel("MCC")
    plt.xlabel("Speed-up to PKNN [n. comparisons]")
    plt.title("Speed vs. MCC trade-off")

    plt.show()'''
