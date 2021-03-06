'''
    File containing measurements to be executed.
'''

from worker_node.SLSH.hash_family import *
from worker_node.node import execute_node
from worker_node.query import Query
from worker_node.utils.logging_node import execute_node_logging
from middleware.utils.logging_middleware import execute_middleware_logging
from middleware.root import execute_middleware
from prediction import *
import pickle
import argparse

# Execute test on a single node.
def parallel_gaussian_test(d, n, cores):
    '''
    Execute speed test on a single node with cores cores.
    d is the dimensionality of the dataset, n the number of points to generate.
    The generated dataset is a isotropic gaussian.

    :param d: dataset dimensionality
    :param n: number of datapoints

    :return: nothing
    '''

    # Data generation.
    mean = 0
    std = 20
    X_shape = (d, n)
    X = np.random.normal(mean, std, X_shape) # Generate dataset.

    # SLSH parameters.
    m_out = 50*2
    L_out = 24*4  # It has to be a multiple of 24 for it to scale decently.
    m_in = 30
    L_in = 10
    k = 1
    alpha = 0.1
    H_out = L1LSH([(-100, 100)] * d)
    H_in = COSLSH(d)

    # Queries generation.
    n_queries = 100
    queries = [Query(np.random.normal(mean, std, d)) for i in range(n_queries)] # Generate random gaussian queries as the dataset points.

    # Execute algorithm.
    table_log, queries = execute_node(cores, k, m_out, L_out, m_in, L_in, H_out, H_in, alpha, X=X, queries=queries)

    # Log output.
    execute_node_logging(("gaussian{}x{}_scaling_test".format(d, n), cores), queries, table_log)

    return


# Execute test on middleware.
def middleware_distributed_gaussian_test(d, n, nodes_list, cores, synchro):

    # The dataset is drawn from a isotropic gaussian.
    filename = "./datasets/gaussian_{}x{}".format(d, n)

    # Queries generation.
    k = 1
    n_queries = 100
    mean = 0
    std = 20
    queries = [Query(np.random.normal(mean, std, d)) for i in range(n_queries)]  # Generate random gaussian queries as the dataset points.

    # Execute parallel code.
    table_log, queries = execute_middleware(nodes_list, cores, n, d, k, queries=queries, filename=filename, synchronous=synchro)

    execute_middleware_logging(("distributed-gaussian{}x{}_scaling_test".format(d, n), len(nodes_list), cores), queries, table_log)

    return


def node_distributed_test(node_id, port, d, n, cores):
    """
    Execute the node for a distibuted SLSH system.
    The dataset choice is done at the middleware.

    :param d: the dimensionality of a point
    :param cores: number of cores to use

    :return: nothing.
    """

    # SLSH parameters.
    m_out = 50 * 2
    L_out = 24 * 4  # It has to be a multiple of 24 for it to scale decently.
    m_in = 20
    L_in = 10
    k = 1
    alpha = 0.01
    H_out = L1LSH([(-100, 100)] * d)
    H_in = COSLSH(d)

    # Execute parallel code.
    table_log, queries = execute_node(cores, k, m_out, L_out, m_in, L_in, H_out, H_in, alpha, distributed=True, port=port)
    # Log output.
    execute_node_logging(("distributed-node{}-gaussian{}x{}_scaling_test".format(node_id, d, n), cores), queries, table_log)

    return


def parallel_labeled_abp_test(filename, n, cores, m_out, L_out, m_in, L_in, alpha, k, exhaustive=False, dataparallel=False, one_nn=False):
    '''
    Execute test on a single node with cores cores. It must fit into memory as is.
    filename is the name of the filename in the dataset folder.
    The generated dataset is a isotropic gaussian.

    :param filename: the name of the file
    :param cores: number of cores to use
    :param m_out: number of outer hash functions
    :param L_out: number of outer tables
    :param m_in: number of inner hash functions
    :param L_in: number of inner tables
    :param alpha: SLSH ratio
    :param k: number of neighbors to use

    :return: nothing
    '''

    if dataparallel:
        base = "dataparallel-"
    else:
        base = ""

    X, labels, queries, query_labels = get_dataset_and_queries_from_pickles(filename)

    d = len(queries[0].point)
    n = len(labels)

    # SLSH parameters.
    H_out = L1LSH([(40, 120)] * d)
    H_in = COSLSH(d)

    # Execute algorithm.
    table_log, queries = execute_node(cores, k, m_out, L_out, m_in, L_in, H_out, H_in, alpha, X=X, queries=queries, labels=labels, exhaustive=exhaustive, dataparallel=dataparallel)

    if exhaustive and one_nn:
        with open("queries-output-{}.pickle".format(n), 'wb') as file:
            pickle.dump(queries, file)

    accuracy = compute_accuracy(queries, query_labels)
    print("The prediction accuracy is: {}".format(accuracy))

    recall = compute_recall(queries, query_labels)
    print("The recall is: {}".format(recall))

    mcc = compute_mcc(queries, query_labels)
    print("The mcc is: {}".format(mcc))

    # Log output.
    if not exhaustive:
        execute_node_logging(("{}abp-mout{}-Lout{}-min{}-Lin{}-alpha{}-n{}-k{}".format(base, m_out, L_out, m_in, L_in, alpha, n, k), cores), queries, table_log, accuracy=accuracy, recall=recall, mcc=mcc, accparameters=(m_out, L_out, m_in, L_in, alpha, n, k))
    else:
        execute_node_logging(("exhaustive-abp-partial{}x{}_scaling_test".format(d, n), cores), queries, table_log,
                             accuracy=accuracy, recall=recall, mcc=mcc, accparameters=(n, k, cores), exhaustive=exhaustive)

    return


def node_distributed_labeled_abp(node_id, n, d, port, cores, m_out, L_out, m_in, L_in, alpha, k, dataparallel=False):
    """
    Execute ABP prediction in a distributed fashion. This function runs a node.

    :param node_id: this node's ID (used for naming)
    :param port: the port to receive connections on
    :param cores: number of cores to use
    :param m_out: number of outer hash functions
    :param L_out: number of outer hash tables
    :param m_in: number of inner hash functions
    :param L_in: number of inner hash tables
    :param alpha: SLSH threshold
    :param k: number of neighbors
    """

    if dataparallel:
        base = "dataparallel-"
    else:
        base = ""

    # SLSH parameters.
    H_out = L1LSH([(40, 120)] * d)
    H_in = COSLSH(d)

    # Execute algorithm.
    table_log, queries = execute_node(cores, k, m_out, L_out, m_in, L_in, H_out, H_in, alpha, prediction=True, distributed=True, port=port, dataparallel=dataparallel)

    execute_node_logging(("{}abp-mout{}-Lout{}-min{}-Lin{}-alpha{}-n{}-k{}".format(base, m_out, L_out, m_in, L_in, alpha, n, k), cores), queries, table_log, accparameters=(n, k, cores))


def middleware_distributed_labeled_abp(filename, d, n, nodes_list, cores, m_out, L_out, m_in, L_in, alpha, k, dataparallel=False, one_nn=False):
    """
    Execute ABP prediction in a distributed fashion. This function runs the middleware.

    :param filename: dataset filename (without path, assumed to be in ./dataset/)
    :param d: dimensionality of a point
    :param n: number of points
    :param nodes_list:  list of nodes according to parse_nodes_list's format
    :param cores: number of cores
    :param m_out: number of outer hash functions
    :param L_out: number of outer hash tables
    :param m_in: number of inner hash functions
    :param L_in: number of inner hash tables
    :param alpha: SLSH threshold
    :param k: number of neighbors
    :return: nothing
    """

    if dataparallel:
        base = "dataparallel-"
    else:
        base = ""

    if one_nn:
        base += "1nn-"

    X, labels, queries, query_labels = get_dataset_and_queries_from_pickles(filename)

    d = len(queries[0].point)
    n = len(labels)

    # Execute parallel code.
    table_log, queries = execute_middleware(nodes_list, cores, n, d, k, X=X, queries=queries, labels=labels, synchronous=True, prediction=True)

    accuracy = compute_accuracy(queries, query_labels)
    print("The prediction accuracy is: {}".format(accuracy))

    recall = compute_recall(queries, query_labels)
    print("The recall is: {}".format(recall))

    mcc = compute_mcc(queries, query_labels)
    print("The mcc is: {}".format(mcc))

    if one_nn:
        # If we want to check retrieval recall for 1nn, overwrite prediction recall with retrieval accuracy.
        retr_recall = compute_retrieval_recall_1NN(n, queries)
        recall = retr_recall

    execute_middleware_logging(("{}abp-mout{}-Lout{}-min{}-Lin{}-alpha{}-n{}-k{}".format(base, m_out, L_out, m_in, L_in, alpha, n, k), len(nodes_list), cores), queries,
                               table_log, accuracy=accuracy, recall=recall, mcc=mcc, accparameters=(m_out, L_out, m_in, L_in, alpha, n, k))
    return


def get_dataset_and_queries_from_pickles(filename):
    """
    Given the filename of the original dataset, returns (as a tuple of four elements):
    - the dataset in numpy matrix form
    - the dataset labels as numpy array
    - the list of queries as numpy arrays
    - the query labels as numpy array

    :param filename: name of the original dataset
    :return: (dataset, dataset labels, queries, queries labels)
    """

    with open("datasets/" + filename[:len(filename) - 5] + "-dataset.pickle", 'rb') as file:
        dataset = pickle.load(file)

    with open("datasets/" + filename[:len(filename) - 5] + "-queries.pickle", 'rb') as file:
        querylist = pickle.load(file)

    n = len(dataset)
    d = len(dataset[0][0])

    # Convert to numpy.
    X = np.empty((d, n))
    labels = np.empty(n)
    for i in range(len(dataset)):
        point = dataset[i][0]
        labels[i] = dataset[i][1]
        X[:, i] = np.array(point)

    n_queries = len(querylist)

    queries = []
    query_labels = np.empty(n_queries, dtype=int)
    for i in range(len(querylist)):
        queries.append(Query(querylist[i][0]))
        query_labels[i] = querylist[i][1]

    return X, labels, queries, query_labels


def parse_nodes_list(string):
    """
    Parse a node list in the format ip:port-ip:port-ip:port

    :param string: the input
    :return: a list of pairs (ip, port)
    """

    pairs = string.split("-")
    splitted_pairs = [pair.split(":") for pair in pairs]

    return [(pair[0], int(pair[1])) for pair in splitted_pairs]


def parse_arguments():
    """
    Parse command-line arguments with argparser.

    :return: the command-line arguments in the class instance returned by argparser
    """

    parser = argparse.ArgumentParser(description="Distributed SLSH")
    # General arguments.
    parser.add_argument(
        "role",
        type=str,
        choices=['node', 'orchestrator'],
        help="Specifies whether to run the orchestrator or a node")
    parser.add_argument(
        "--task",
        type=str,
        choices=['test', 'accuracy', 'exhaustive-accuracy'],
        help="Specifies whether to run the orchestrator or a node")
    parser.add_argument(
        "--filename",
        type=str,
        help="The .txt file storing the dataset")
    parser.add_argument(
        "--n",
        type=int,
        help="Number of points")
    parser.add_argument(
        "--d",
        type=int,
        help="Point dimensionality")
    parser.add_argument(
        "--m_out",
        type=int,
        help="Number of hash functions for outer LSH layer")
    parser.add_argument(
        "--L_out",
        type=int,
        help="Number of hash tables for outer LSH layer")
    parser.add_argument(
        "--m_in",
        type=int,
        help="Number of hash functions for inner LSH layer")
    parser.add_argument(
        "--L_in",
        type=int,
        help="Number of hash tables for inner LSH layer")
    parser.add_argument(
        "--alpha",
        type=float,
        help="SLSH population ratio threshold")
    parser.add_argument(
        "--k",
        type=int,
        help="Number of nearest neighbors")
    parser.add_argument(
        "--cores",
        type=int,
        help="Number of cores per node")
    parser.add_argument(
        "--dataparallel",
        type=str,
        choices=['yes', 'no'],
        help="Number of cores per node")


    # Node-specific arguments.
    parser.add_argument(
        "--mode",
        type=str,
        choices=['distributed', 'local'],
        help="Run node locally or relying on a middleware")
    parser.add_argument(
        "--port",
        type=int,
        help="Port number nodes accept connections on")
    parser.add_argument(
        "--node_id",
        type=int,
        help="Node id (for logging purposes, starts from 1)")

    # Orchestrator-specific arguments.
    parser.add_argument(
        "--nodes_list",
        type=str,
        help="List of nodes and ports the middleware connects to, in format ip:port-ip:port (e.g., 127.0.0.1:1025-127.0.0.1:1050)")
    parser.add_argument(
        "--synchronous",
        type=str,
        choices=['synchronous', 'asynchronous'],
        help="Specify whether middleware will be executed synchronously")

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_arguments()

    if not args.dataparallel:
        dataparallel = False
    else:
        dataparallel = (args.dataparallel == "yes")

    if args.role == "node":

        if not (args.mode and args.task):
            raise IOError("Missing arguments: you need to specify mode and task when running nodes.")

        # Execute the worker node in the distributed setting.
        if args.mode == "distributed":

            if args.task == "test":
                # Format: role execution_mode test node_id port cores n d

                if not (args.node_id and args.port and args.d and args.n and args.cores):
                    raise IOError("Missing arguments for the chosen distributed node task, please see code.")

                node_distributed_test(args.node_id, args.port, args.d, args.n, args.cores)

            elif args.task == "accuracy":
                # Format: role execution_mode accuracy node_id port cores n d m_out L_out m_in L_in alpha k

                if not (args.node_id and args.n and args.d and args.port and args.cores and args.m_out and args.L_out and args.m_in and args.L_in and args.alpha and args.k):
                    raise IOError("Missing arguments for the chosen distributed node task, please see code.")

                node_distributed_labeled_abp(args.node_id, args.n, args.d, args.port, args.cores, args.m_out, args.L_out, args.m_in, args.L_in, args.alpha, args.k, dataparallel=dataparallel)

        # Execute the worker node as a single node (it will generate the dataset locally).
        else:

            if args.task == "test":
                # Format: role execution_mode test cores n d
                if not (args.d and args.n and args.cores):
                    raise IOError("Missing arguments for the chosen local node task, please see code.")
                
                parallel_gaussian_test(args.d, args.n, args.cores)

            elif args.task == "accuracy":
                # Format: role execution_mode accuracy cores n d m_out L_out m_in L_in alpha k filename
                if not (args.filename and args.n and args.cores and args.m_out and args.L_out and args.m_in and args.L_in and args.alpha and args.k):
                    raise IOError("Missing arguments for the chosen local node task, please see code.")
            
                parallel_labeled_abp_test(args.filename, args.n, args.cores, args.m_out, args.L_out, args.m_in, args.L_in, args.alpha, args.k, dataparallel=dataparallel)

            elif args.task == "exhaustive-accuracy":
                # Format: role execution_mode exhaustive-accuracy cores n d k filename
                if not (args.filename and args.n and args.cores and args.k):
                    raise IOError("Missing arguments for the chosen local node task, please see code.")
                parallel_labeled_abp_test(args.filename, args.n, args.cores, 0, 0, 0, 0, 0, args.k, exhaustive=True)


    elif args.role == "orchestrator":

        if not args.synchronous or not args.nodes_list:
            raise IOError("Required synchronous and node_list arguments for orchestrator execution")
        synchro = (args.synchronous == "synchronous")
        nodes_list = parse_nodes_list(args.nodes_list)

        if args.task == "test":
            # Format: role test synchrony nodes_list cores n d
            if not (args.d and args.n and args.cores):
                raise IOError("Missing arguments for the chosen orchestrator task, please see code.")

            middleware_distributed_gaussian_test(args.d, args.n, nodes_list, args.cores, synchro)

        elif args.task == "accuracy":
            # Format: role accuracy synchrony nodes_list cores n d m_out L_out m_in L_in alpha k filename

            if not (args.filename and args.d and args.n and args.cores and args.m_out and args.L_out and args.m_in and args.L_in and args.alpha and args.k):
                raise IOError("Missing arguments for the chosen orchestrator task, please see code.")

            middleware_distributed_labeled_abp(args.filename, args.d, args.n, nodes_list, args.cores, args.m_out, args.L_out, args.m_in, args.L_in, args.alpha, args.k, dataparallel=dataparallel)
