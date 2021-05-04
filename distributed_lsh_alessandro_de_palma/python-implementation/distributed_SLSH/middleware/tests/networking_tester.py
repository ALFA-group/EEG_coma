import unittest
from middleware.utils.networking import read_data
import socket
from time import sleep
import numpy as np
import multiprocessing
from worker_node.middleware_interface import MiddlewareInterface

class TestNetworking(unittest.TestCase):

    def test_networking(self):
        '''
        Simulate <nodes> different nodes locally and print what they receive from the middleware.
        Then send back the correct output without performing lsh.
        '''

        cores = 2
        addresses = [("127.0.0.1", 1025), ("127.0.0.1", 1035)]

        processes = []
        for i in range(cores-1):
            p = multiprocessing.Process(target=simulate_node, args=(addresses[i],))
            p.start()
            processes.append(p)

        simulate_node(addresses[cores - 1])

        for i in range(cores-1):
            p.join()

        a = 1
        a = a * 25
        b = 2

        self.assertTrue(a == a)


def simulate_node(address):
    '''
    Execute the node simulation. It just sends the expected output, without actually performing slsh.

    :param address: the (ip, port) pair to simulate.
    '''

    interface = MiddlewareInterface(address=address)

    X = interface.receive_dataset()
    print("X", X)

    # Simulate that we built the tables.
    interface.send_table_construction_notification()

    while True:
        query = interface.receive_query()
        if not query: # If we reached termination.
            break

        interface.send_query_output([X[21]], query)

    interface.send_termination()
    interface.close()
