import os
from time import sleep
from run_multinode import run_middleware_abp_prediction, run_worker_abp_prediction, kill_machines

def run_strongscaling_experiment(node_ips, port, middleware_ip, from_middleware=False, dataparallel=False):
    """
    Tuning for AHE prediction on large datasets.

    :param node_ips: list of ips of the workes (nodes)
    :param port: the port the nodes accept connections on.
    :param middleware_ip: ip of the middleware

    :return: nothing
    """

    d = 30
    n_list = [801724, 1373479]
    filename_list = ["ABP-AHE-lag30m-cond30m-d30-withgaps.data", "ABP-AHE-lag5m-cond5m-withgaps.data"]
    m_out_list = [125, 150]
    L_out_list = [72, 120]
    m_in = 1 #90
    L_in = 1 #60
    k = 10
    alpha = 1 #0.005
    cores = 24
    workers_list = [1, 2, 3, 4]

    for i in range(len(n_list)):
        n = n_list[i]
        filename = filename_list[i]
        m_out = m_out_list[i]
        L_out = L_out_list[i]

        for workers in workers_list:
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


if __name__ == "__main__":

    """
    Usage:

        run from scripts/
        python3 run_strongscaling.py


    IMPORTANT: in order to run a script without keeping the terminal open, use
    nohup python3 -u run_strongscaling.py &
    """

    node_ips = ["128.52.162.68", "128.52.162.69", "128.52.162.77", "128.52.162.78"]  # User settings.
    port = 3000  # The port the nodes accept connections on.  # User settings.
    middleware_ip = "128.52.161.43"  # User settings.

    dataparallel = True

    run_strongscaling_experiment(node_ips, port, middleware_ip, from_middleware=True, dataparallel=dataparallel)
