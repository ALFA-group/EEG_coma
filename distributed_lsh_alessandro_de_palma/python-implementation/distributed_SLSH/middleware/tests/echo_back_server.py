"""
    This simple test is meant to measure the rtt time from the middleware to a node.
"""

import socket
from middleware.utils.networking import *
import unittest

class TestEchoBack(unittest.TestCase):

    def test_echo_back(self):
        # Echo back to the client.

        for i in range(50):

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Use IPv4, TCP.
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Avoid "address already in use" issues.
            sock.setblocking(True)  # Use blocking operations.
            sock.bind(('', 1025))  # Receive on all available interfaces, on port 1025.
            sock.listen(1)
            connection, address = sock.accept()

            data = read_data(connection)
            send_data(data, connection)

            connection.shutdown(1)
            connection.close()
            sock.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Use IPv4, TCP.
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Avoid "address already in use" issues.
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setblocking(True)  # Use blocking operations.
        sock.bind(('', 1025))  # Receive on all available interfaces, on port 1025.
        sock.listen(1)
        connection, address = sock.accept()

        for i in range(50):
            data = read_data(connection)
            send_data(data, connection)

        connection.shutdown(1)
        connection.close()
        sock.close()

        return