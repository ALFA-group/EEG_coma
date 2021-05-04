'''
    File containing scripts to run experiments for intranode execution.
'''

import sys, os

def run_single_node_test(ip):

    command = "\"cd /home/ubuntu/code/distributed_SLSH; python3 -u main.py node --mode local --task test --cores {} --n {}\""
    ssh = "ssh -i /home/aledepo93/.ssh/openstack.key ubuntu@{} ".format(ip)  # User settings.

    #n_list = [5000, 10000, 20000]
    n_list = [100000]
    #cores_list = [1, 2, 4, 8, 16, 24]
    cores_list = [24]

    for n in n_list:
        for cores in cores_list:
            print(command.format(cores, n))
            os.system(ssh + command.format(cores, n))

    return


def run_single_node_accuracy(ip, dataparallel=False):

    if dataparallel:
        dataparallelstring = "--dataparallel yes"
    else:
        dataparallelstring = ""

    command = "\"cd /home/ubuntu/code/distributed_SLSH; python3 -u main.py node --mode local --task accuracy --cores {} --n {} --d {} " \
              "--m_out {} --L_out {} --m_in {} --L_in {} --alpha {} --k {} --filename {} {}\""
    ssh = "ssh ubuntu@{} ".format(ip)  # User settings.

    if ip == "local":
        ssh = ""
        command = "cd /home/ubuntu/code/distributed_SLSH; python3 -u main.py node --mode local --task accuracy --cores {} --n {} --d {} " \
                  "--m_out {} --L_out {} --m_in {} --L_in {} --alpha {} --k {} --filename {} {}"

    # n = [84337, 361740]
    n = [803724, 1373479]
    d = 30
    filename = ["ABP-AHE-lag30m-cond30m-d30-withgaps.data", "ABP-AHE-lag5m-cond5m-withgaps.data"]

    cores = [1, 2, 4, 8, 16, 24]
    m_out_list = [125, 125]
    L_out = 24 * 3
    m_in = [90]
    L_in = [60]
    k = [10]
    alpha = [0.005]

    for i in range(len(n)):
        cn = n[i]
        cfilename = filename[i]
        m_out = m_out_list[i]

        for ccores in cores:
            for cm_in in m_in:
                for cL_in in L_in:
                    for ck in k:
                        for calpha in alpha:
                            print(command.format(ccores, cn, d, m_out, L_out, cm_in, cL_in, calpha, ck, cfilename, dataparallelstring))
                            os.system(ssh + command.format(ccores, cn, d, m_out, L_out, cm_in, cL_in, calpha, ck, cfilename, dataparallelstring))

    return


def run_single_node_exhaustive_test(ip):

    command = "\"cd /home/ubuntu/code/distributed_SLSH; python3 main.py node --mode local --task exhaustive-accuracy --cores {} --n {} --d {} --k {} --filename {}\""
    ssh = "ssh ubuntu@{} ".format(ip)  # User settings.

    if ip == "local":
        ssh = ""
        command = "cd /home/ubuntu/code/distributed_SLSH; python3 main.py node --mode local --task exhaustive-accuracy --cores {} --n {} --d {} --k {} --filename {}"

    n = [803724]
    d = 30
    filename = ["ABP-AHE-lag30m-cond30m-d30-withgaps.data"]

    cores = [8, 16, 24]
    k = 1

    for i in range(len(n)):
        cn = n[i]
        cfilename = filename[i]

        for ccores in cores:
            print(command.format(ccores, cn, d, k, cfilename))
            os.system(ssh + command.format(ccores, cn, d, k, cfilename))

    return



if __name__ == "__main__":

    ip = sys.argv[1]
    dataparallel = True
    #run_single_node_test(ip)

    run_single_node_accuracy(ip, dataparallel=dataparallel)
