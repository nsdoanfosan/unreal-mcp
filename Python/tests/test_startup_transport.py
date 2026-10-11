import ast
import json
import logging
from pathlib import Path
import socket
import threading
from typing import Any, Dict, Optional
import unittest
SOURCE = Path(__file__).resolve().parents[1] / 'unreal_mcp_server.py'

def connection_type():
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    class_node = next((node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'UnrealConnection'))
    namespace = {'socket': socket, 'json': json, 'threading': threading, 'logger': logging.getLogger('unreal_transport_test'), 'Dict': Dict, 'Any': Any, 'Optional': Optional}
    exec(compile(ast.Module(body=[class_node], type_ignores=[]), str(SOURCE), 'exec'), namespace)
    return namespace['UnrealConnection']

class FakeSocket:

    def __init__(self, chunks):
        self.chunks = iter(chunks)
        self.sent = []
        self.closed = False

    def settimeout(self, value):
        pass

    def recv(self, size):
        value = next(self.chunks, b'')
        if isinstance(value, Exception):
            raise value
        return value

    def sendall(self, value):
        self.sent.append(value)

    def close(self):
        self.closed = True

class StartupTransportTests(unittest.TestCase):

    def setUp(self):
        self.connection = connection_type()()
        self.connect_calls = 0

    def send_with_socket(self, fake):

        def connect():
            self.connect_calls += 1
            self.connection.socket = fake
            self.connection.connected = True
            return True
        self.connection.connect = connect
        return self.connection.send_command('set_actor_property', {'name': '캐릭터'})

    def test_lazy_client_does_not_connect_or_send_startup_probe(self):
        tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
        func = next((node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'get_unreal_connection'))
        namespace = {'UnrealConnection': connection_type(), 'Optional': Optional, '_unreal_connection': None, '_unreal_connection_lock': threading.Lock()}
        exec(compile(ast.Module(body=[func], type_ignores=[]), str(SOURCE), 'exec'), namespace)
        client = namespace['get_unreal_connection']()
        self.assertIsNone(client.socket)
        self.assertFalse(client.connected)

        def must_not_connect():
            self.fail('retrieving a command client reserved an idle editor socket')
        client.connect = must_not_connect
        self.assertIs(namespace['get_unreal_connection'](), client)

    def test_two_commands_release_each_socket(self):
        first = FakeSocket([b'{"status":"success"}'])
        second = FakeSocket([b'{"status":"success"}'])
        self.send_with_socket(first)
        self.send_with_socket(second)
        self.assertTrue(first.closed and second.closed)
        self.assertIsNone(self.connection.socket)
        self.assertEqual(self.connect_calls, 2)
