import socket
import json


class Connection (object):
    """A simple, raw interface to batsd's TCP data server."""

    def __init__(self, host='127.0.0.1', port=8127):
        self.host = host
        self.port = port
        self.connect()

    def connect(self):
        """Connects to the server. You should never need this unless you called quit or disconnect."""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(0.5)
        self.socket.connect((self.host, self.port))

    def disconnect(self):
        """Disconnect from the server without saying goodbye."""
        self.socket.close()
        self.socket = None

    def _exchange(self, send, isjson=True):
        sent = 0
        while sent < len(send):
            sent += self.socket.send(send[sent:])

        response = ""
        byte = self.socket.recv(1)
        while len(byte) and byte != "\n":
            response = response + byte
            byte = self.socket.recv(1)

        if isjson:
            return json.loads(response)
        else:
            return response

    def ping(self):
        """Use the built in ping to check if the server is there."""
        return 'PONG' == self._exchange('ping', False)

    def available(self):
        """Get the available datapoints."""
        return self._exchange('available')

    def values(self, name, start, end):
        """
        Get values from a datapoint, in a given time span.

        Parameters 'start' and 'end' are integer Unix timestamps.
        """
        return self._exchange('values %s %d %d' % (name, start, end))

    def quit(self):
        """Say goodbye and disconnect from the server."""
        self._exchange('quit')
        self.disconnect()


if '__main__' == __name__:
    from time import time

    c = Connection()
    print c.ping()
    print c.available()
    print c.values('counters:Test.counter', int(time()) - 60, int(time()))
