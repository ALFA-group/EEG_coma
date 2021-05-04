import os
from time import sleep
from run_multinode import run_middleware_abp_prediction, run_worker_abp_prediction, kill_machines

def run_lsh_layer(node_ips, port, middleware_ip, dataparallel=False, from_middleware=False):
    """
    Tuning for AHE prediction on large datasets.

    :param node_ips: list of ips of the workes (nodes)
    :param port: the port the nodes accept connections on.
    :param middleware_ip: ip of the middleware

    :return: nothing
    """

    d = 30
    workers = 2
    n = 801724
    filename = "ABP-AHE-lag30m-cond30m-d30-withgaps.data"
    m_out_list = [100, 125, 150, 175, 200]
    L_out_list = [72, 96, 120]
    m_in = 1
    L_in = 1
    alpha = 1
    k = 10
    cores = 24

    for m_out in m_out_list:
        for L_out in L_out_list:
            # Run all workers for this experiment.
            for j in range(workers):
                run_worker_abp_prediction(j + 1, node_ips[j], port, cores, n, d, m_out, L_out,
                                          m_in, L_in, alpha, k, dataparallel=dataparallel, from_middleware=from_middleware)
            # Run the middleware and wait for it to terminate.
            sleep(30)
            run_middleware_abp_prediction(middleware_ip, node_ips[:workers], port, cores, n, d,
                                          m_out, L_out, m_in, L_in, alpha, k, filename, dataparallel=dataparallel, middleware=from_middleware)
            sleep(280)
            kill_machines(node_ips, middleware_ip, from_middleware=from_middleware)

            # Change port to avoid issues.
            port += 10


def run_slsh_layer(node_ips, port, middleware_ip, m_out, L_out, dataparallel=False, from_middleware=False):
    """
    Tuning for AHE prediction on large datasets.

    :param node_ips: list of ips of the workes (nodes)
    :param port: the port the nodes accept connections on.
    :param middleware_ip: ip of the middleware

    :return: nothing
    """

    d = 30
    workers = 2
    n = 801724
    filename = "ABP-AHE-lag30m-cond30m-d30-withgaps.data"
    #m_in_list = [40, 65, 90, 115]
    m_in_list = [20, 60]
    L_in_list = [20, 60]
    #alpha = [0.005]
    alpha = [0.0001, 0.0005]
    k = 10
    cores = 24

    for m_in in m_in_list:
        for L_in in L_in_list:
            for calpha in alpha:
                # Run all workers for this experiment.
                for j in range(workers):
                    run_worker_abp_prediction(j + 1, node_ips[j], port, cores, n, d, m_out, L_out,
                                              m_in, L_in, calpha, k, dataparallel=dataparallel, from_middleware=from_middleware)
                # Run the middleware and wait for it to terminate.
                sleep(30)
                run_middleware_abp_prediction(middleware_ip, node_ips[:workers], port, cores, n, d,
                                              m_out, L_out, m_in, L_in, calpha, k, filename, dataparallel=dataparallel, middleware=from_middleware)
                sleep(280)

                # Change port to avoid issues.
                port += 10


def run_baseline(ip):

    command = "\"cd /home/ubuntu/code/distributed_SLSH; python3 main.py node --mode local --task exhaustive-accuracy --cores {} --n {} --d {} --k {} --filename {}\""
    ssh = "ssh ubuntu@{} ".format(ip)  # User settings.

    if ip == "local":
        ssh = ""
        command = "cd /home/ubuntu/code/distributed_SLSH; python3 main.py node --mode local --task exhaustive-accuracy --cores {} --n {} --d {} --k {} --filename {}"

    n = 801724
    d = 30
    filename = "MIMICIII-ABP-AHE-lag30m-cond30m.data"
    cores = 1
    k = 1

    print(command.format(cores, n, d, k, filename))
    os.system(ssh + command.format(cores, n, d, k, filename))


if __name__ == "__main__":

    """
    Usage:

        run from distributed_SLSH/
        python3 ../scripts/run_speedMCC.py


    IMPORTANT: in order to run a script without keeping the terminal open, use
    nohup python3 -u run_speedMCC.py &
    """

    node_ips = ["128.52.162.68", "128.52.162.69"]  # User settings.
    port = 3000  # The port the nodes accept connections on.  # User settings.
    middleware_ip = "128.52.161.43"  # User settings.

    dataparallel = True

    #run_lsh_layer(node_ips, port, middleware_ip, dataparallel=dataparallel, from_middleware=True)

    m_out = 125
    L_out = 72
    run_slsh_layer(node_ips, port, middleware_ip, m_out, L_out, dataparallel=dataparallel, from_middleware=True)

    run_baseline(middleware_ip)