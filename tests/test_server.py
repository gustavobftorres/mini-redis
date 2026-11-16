import subprocess
import unittest

from src.client import client
from src.server import server


class TestServerConnection(unittest.TestCase):
    def setUp(self) -> None:
        subprocess.Popen(server("localhost", 8002))
        return super().setUp()

    def test_echo_short_message(self):
        answer = "test message"
        response = client("localhost", 8003, "test message")
        self.assertEqual(answer, response)


if __name__ == "__main__":
    unittest.main()
