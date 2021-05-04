'''
    File containing scripts to run experiments for distributed execution.
'''

import os
from time import sleep
import sys


def run_distributed_slsh_test(node_ips, port, middleware_ip, middleware=False):
    """
    Strong scaling experiment: see how the system performs if you increase the load and the nodes
    at the same time.

    :param node_ips: list of ips of the workes (nodes)
    :param port: the port the nodes accept connections on.
    :param middleware_ip: ip of the middleware
    :param middleware: A flag, True if the script is executed on middleware.

    :return: nothing
    """

    kill_machines(node_ips, middleware_ip, from_middleware=middleware)
    sleep(10)

    d = 100
    worker_list = [1, 2, 4]
    #cores = [8, 24]
    cores = [24]
    #n_list = [100000, 200000, 400000]
    n_lists = [[100000, 200000, 400000], [1000000, 2000000, 4000000]]

    for c in cores:
        for n_list in n_lists:
            for i in range(len(worker_list)):

                workers = worker_list[i]
                n = n_list[i]

                # Run all workers for this experiment.
                for j in range(workers):
                    run_worker_test(j + 1, node_ips[j], port, c, n, d, from_middleware=middleware)
                # Run the middleware and wait for it to terminate.
                sleep(10)
                run_middleware_test(middleware_ip, node_ips[:workers], port, c, n, d, middleware=middleware)
                sleep(10)
                # kill_machines(node_ips, middleware_ip, from_middleware=middleware)
                sleep(250)

                # Change port to avoid issues.
                port += 10

    return


def run_worker_test(node_id, worker_ip, port, n_cores, n, d, from_middleware=False):

    command = "\"cd /home/ubuntu/code/distributed_SLSH; python3 main.py node --mode distributed --task test --node_id {} --port {} --cores {} --n {} --d {}\" &".format(node_id, port, n_cores, n, d)  # Run command in background.

    if from_middleware:
        directory = "ubuntu"  # User settings.
    else:
        directory = "aledepo93"  # User settings.

    ssh = "ssh -i /home/{}/.ssh/openstack.key ubuntu@{} ".format(directory, worker_ip)  # User settings.

    print(ssh + command)
    os.system(ssh + command)


def run_middleware_test(middleware_ip, node_ips, port, n_cores, n, d, middleware=False):

    nodes = ""
    for i in range(len(node_ips)):
        ip = node_ips[i]
        nodes += ip + ":{}".format(port)
        if i < len(node_ips)-1:
            nodes += "-"

    # Execute from middleware.
    if middleware:
        command = "python3 main.py orchestrator --task test --synchronous synchronous --nodes_list {} --cores {} --n {} --d {}".format(nodes, n_cores, n, d)
        print(command)
        os.system(command)
    # Execute from a client.
    else:
        command = "\"cd /home/ubuntu/code/distributed_SLSH; python3 main.py orchestrator --task test --synchronous synchronous --nodes_list {} --cores {} --n {} --d {}\"".format(nodes, n_cores, n, d)  # Wait for this to terminate.
        ssh = "ssh -i /home/aledepo93/.ssh/openstack.key ubuntu@{} ".format(middleware_ip)  # User settings.
        print(ssh + command)
        os.system(ssh + command)


def run_distributed_slsh_abp_prediction(node_ips, port, middleware_ip, middleware=False, dataparallel=False):
    """
    Tuning for AHE prediction on large datasets.

    :param node_ips: list of ips of the workes (nodes)
    :param port: the port the nodes accept connections on.
    :param middleware_ip: ip of the middleware
    :param middleware: A flag, True if the script is executed on middleware.
    :param dataparallel: A flag, True if the intranode parallelism is on data rather than on tables.

    :return: nothing
    """

    if dataparallel:
        dataparallelstring = "--dataparallel yes"
    else:
        dataparallelstring = ""

    kill_machines(node_ips, middleware_ip, from_middleware=middleware)
    sleep(10)

    d = 30
    workers = [2, 1]
    # cores = [1, 2, 4, 8, 12, 16, 20, 24]
    cores = 8
    n = [1373479] #803724
    # filename = ["ABP-AHE-lag30m-cond30m-d30-withgaps.data", "ABP-AHE-lag10m-cond10m-withgaps.data"]
    filename = ["ABP-AHE-lag5m-cond5m-withgaps.data"]

    m_out_list = [125]  # [190]
    L_out_list = [24 * 3]
    m_in = [90]
    L_in = [60]
    k = [10]
    alpha = [0.005]  # [0.005]

    for i in range(len(workers)):
        cworkers = workers[i]
        cn = n[0]
        cfilename = filename[0]

        for m_out in m_out_list:
            for L_out in L_out_list:
                for cm_in in m_in:
                    for cl_in in L_in:
                        for ck in k:
                            for calpha in alpha:
                                # Run all workers for this experiment.
                                for j in range(cworkers):
                                    run_worker_abp_prediction(j + 1, node_ips[j], port, cores, cn, d, m_out, L_out,
                                                              cm_in, cl_in, calpha, ck, from_middleware=middleware, dataparallel=dataparallel)
                                # Run the middleware and wait for it to terminate.
                                sleep(30)
                                run_middleware_abp_prediction(middleware_ip, node_ips[:cworkers], port, cores, cn, d,
                                                              m_out, L_out, cm_in, cl_in, calpha, ck, cfilename,
                                                              middleware=middleware, dataparallel=dataparallel)
                                sleep(280)
                                kill_machines(node_ips, middleware_ip, from_middleware=middleware)

                                # Change port to avoid issues.
                                port += 10

    return


def run_worker_abp_prediction(node_id, worker_ip, port, n_cores, n, d, m_out, L_out, m_in, L_in, alpha, k, from_middleware=False, dataparallel=False):

    if dataparallel:
        dataparallelstring = "--dataparallel yes"
    else:
        dataparallelstring = ""

    command = "\"cd /home/ubuntu/code/distributed_SLSH; python3 -u main.py node --mode distributed --task accuracy --node_id {} --port {} --cores {} --n {} --d {} " \
              "--m_out {} --L_out {} --m_in {} --L_in {} --alpha {} --k {} {}\" &".format(node_id, port, n_cores, n, d, m_out, L_out, m_in, L_in, alpha, k, dataparallelstring)  # Run command in background.

    if from_middleware:
        directory = "ubuntu"  # User settings.
    else:
        directory = "aledepo93"  # User settings.

    ssh = "ssh -i /home/{}/.ssh/openstack.key ubuntu@{} ".format(directory, worker_ip)  # User settings.

    print(ssh + command)
    os.system(ssh + command)


def run_middleware_abp_prediction(middleware_ip, node_ips, port, n_cores, n, d, m_out, L_out, m_in, L_in, alpha, k, filename, middleware=False, dataparallel=False):

    if dataparallel:
        dataparallelstring = "--dataparallel yes"
    else:
        dataparallelstring = ""

    nodes = ""
    for i in range(len(node_ips)):
        ip = node_ips[i]
        nodes += ip + ":{}".format(port)
        if i < len(node_ips)-1:
            nodes += "-"

    # Execute from middleware.
    if middleware:
        #m_out L_out m_in L_in alpha k filename
        command = "python3 -u main.py orchestrator --task accuracy --synchronous synchronous --nodes_list {} --cores {} --n {} --d {} " \
                  "--m_out {} --L_out {} --m_in {} --L_in {} --alpha {} --k {} --filename {} {}".format(nodes, n_cores, n, d, m_out, L_out, m_in, L_in, alpha, k, filename, dataparallelstring)
        print(command)
        os.system(command)
    # Execute from a client.
    else:
        command = "\"cd /home/ubuntu/code/distributed_SLSH; python3 -u main.py orchestrator --task accuracy --synchronous synchronous --nodes_list {} --cores {} --n {} --d {} " \
                  "--m_out {} --L_out {} --m_in {} --L_in {} --alpha {} --k {} --filename {} {}\"".format(nodes, n_cores, n, d, m_out, L_out, m_in, L_in, alpha, k, filename, dataparallelstring)  # Wait for this to terminate.
        ssh = "ssh ubuntu@{} ".format(middleware_ip)  # User settings.
        print(ssh + command)
        os.system(ssh + command)


def kill_machines(workers, middleware, from_middleware=False):

    if from_middleware:
        directory = "ubuntu"  # User settings.
    else:
        directory = "aledepo93"  # User settings.

    ssh = "ssh -i /home/{}/.ssh/openstack.key ubuntu@{} "  # User settings.
    command = "\"pkill python\""

    for worker in workers:
        os.system(ssh.format(directory, worker) + command)

    if from_middleware:
        os.system(command)
    else:
        os.system(ssh.format(directory, middleware) + command)


if __name__ == "__main__":

    """
    Usage:
        middleware
            run from /home/ubuntu/code/distributed_SLSH/
            python3 ../scripts/run_multinode.py middleware

        client
            run from distributed_lsh_alessandro_de_palma/python_implementation/scripts/
            python3 run_multinode.py client


    IMPORTANT: in order to run a script on the middleware without keeping the terminal open, use
    nohup python3 -u ../scripts/run_multinode.py middleware &
    """

    node_ips = ["128.52.161.48", "128.52.161.31"]  # User settings.
    port = 3000  # The port the nodes accept connections on.  # User settings.
    middleware_ip = "128.52.161.43"  # User settings.

    dataparallel = True

    middleware = (sys.argv[1] == "middleware")

    run_distributed_slsh_abp_prediction(node_ips, port, middleware_ip, middleware, dataparallel=dataparallel)
