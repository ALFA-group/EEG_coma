"""
    This simple test is meant to measure the rtt time from the middleware to a node.
"""

from time import time
import sys
from middleware.utils.networking import *

import unittest

class TestComputeRTT(unittest.TestCase):
    def test_compute_rtt(self):

        #Measure RTT to node

        #TODO: for some reason I don't get, it increases network latency of a factor 10 after the first send.
        #TODO: try UDP or a framework like uvloop.

        ip = "128.52.176.0"
        port = 1025

        print("close connection each time")
        for i in range(50):

            setup_start = time()
            temp = create_socket_connections([(ip, port)])
            server = temp[0]

            start_time = time()
            send_data("ping", server)

            data = read_data(server)
            end_time = time()

            print(end_time-start_time)
            print("message: ", data)

            server.close()
            setup_end = time()
            print(setup_end-setup_start)

        print("keep it open")

        temp = create_socket_connections([(ip, port)])
        server = temp[0]
        for i in range(50):
            start_time = time()
            send_data("ping", server)

            data = read_data(server)
            end_time = time()

            print(end_time - start_time)
            print("message: ", data)

        server.close()

        return