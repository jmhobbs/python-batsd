import socket
import json


class DataType (object):
    """Abstract class for batsd datapoints."""
    prefix = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '<%s.%s "%s">' % (self.__class__.__module__, self.__class__.__name__, self.name)

    def __init__(self, name, connection=None):
        self.name = name
        if not connection:
            connection = Connection()
        self.connection = connection

    def keyname(self, subname=None, measure=None):
        names = [self.name]
        subname and names.append(subname)
        name = self.prefix + '.'.join(names)
        if measure:
            name = name + ':' + measure
        return name

    def get(self, start, end, subname=None, measure=None):
        return DataSet(self.connection.values(self.keyname(subname, measure), start, end), self, start, end, subname, measure)


class DataSet (object):
    """A collection of data points, iterable."""
    def __init__(self, raw, datatype, start, end, subname=None, measure=None):
        self.series = map(lambda x: (int(x['timestamp']), float(x['value'])), raw[datatype.keyname(subname, measure)])
        self.interval = raw['interval']
        self.datatype = datatype
        self.start = start
        self.end = end
        self.subname = subname
        self.measure = measure
        self.size = len(self.series)
        self._index = -1

    def export(self):
        """Get a dictionary representation of this data set."""
        return  {"interval": self.interval, "series": self.series,
                 "start": self.start, "end": self.end,
                 "name": self.datatype.name, "subname": self.subname,
                 "measure": self.measure, "type": self.datatype.__class__.__name__}

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return json.dumps(self.export())

    def __iter__(self):
        return self

    def next(self):
        self._index += 1
        if self._index < self.size:
            return self.series[self._index]
        else:
            raise StopIteration


class Counter (DataType):
    """
    A counter datapoint.

    Counters are summed up over the course of each retention interval. No information about the distribution of values received is retained.
    """
    prefix = 'counters:'


class Gauge (DataType):
    """
    A gague datapoint.

    Gauges are not aggregated or averaged in any way.
    """
    prefix = 'gauges:'


class Timer (DataType):
    """
    A timer datapoint.

    Timers are averaged and several measures are stored about the distribution:

    mean - the mean value of all measurements in that interval
    min - the minimum value of all measurements in that interval
    max - the maximum value of all measurements in that interval
    count - the total number of measurements in that interval
    upper_90 - the upper 90th percentile threshold that measurements in that interval all fall below
    standard deviation - the standard deviation of measurements in that interval
    """
    prefix = 'timers:'

    def get(self, start, end, subname='total', measure='mean'):
        """
        Get a timer value.

        measure can be: mean, min, max, count, upper_90, stddev
        """
        return DataSet(self.connection.values(self.keyname(subname, measure), start, end), self, start, end, subname, measure)

    def getmean(self, start, end, subname='total'):
        """Get the mean value of all measurements in a time period."""
        return self.get(start, end, subname, 'mean')

    def getmin(self, start, end, subname='total'):
        """Get the minimum value of all measurements in a time period."""
        return self.get(start, end, subname, 'min')

    def getmax(self, start, end, subname='total'):
        """Get the maximum value of all measurements in a time period."""
        return self.get(start, end, "max")

    def getcount(self, start, end, subname='total'):
        """Get the total number of measurements in a time period."""
        return self.get(start, end, subname, 'count')

    def getupper90(self, start, end, subname='total'):
        """Get the upper 90th percentile of all measurements in a time period."""
        return self.get(start, end, subname, 'upper_90')

    def getstddev(self, start, end, subname='total'):
        """Get the standard deviation of all measurements in a time period."""
        return self.get(start, end, subname, 'stddev')


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
        """Get the available datapoints, raw names."""
        return self._exchange('available')

    def counters(self):
        """Get a list of all available counters."""
        return map(lambda x: Counter(x[9:], self), filter(lambda x: 'counters:' == x[:9], self.available()))

    def gauges(self):
        """Get a list of all available gauges."""
        return map(lambda x: Gauge(x[7:], self), filter(lambda x: 'gauges:' == x[:7], self.available()))

    def timers(self):
        """Get a list of all available timers."""
        return map(lambda x: Timer(x[7:], self), filter(lambda x: 'timers:' == x[:7], self.available()))

    def counter(self, name):
        return Counter(name, self)

    def gauge(self, name):
        return Gauge(name, self)

    def timer(self, name):
        return Timer(name, self)

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
