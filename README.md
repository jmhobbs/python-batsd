`python-batsd` is a thin wrapper for getting data out of a [batsd](https://github.com/noahhl/batsd) server.

`batsd` exposes a TCP interface, on port 8127 by default, where you can access the data values that you store into it.  This library provides a simple(-ish) way to get at that data.

# Installation

```console
$ git clone https://github.com/jmhobbs/python-batsd.git && cd python-batsd && python setup.py install
```

# Usage

```python
from batsd import Connection
from time import time


c = Connection() # defaults to host=127.0.0.1, port=8127

if c.ping():
    print 'The server is alive!'
    print c.available() # list of datapoints
    print c.values('counters:Test.counter', int(time()) - 60, int(time())) # hash of counter values
```

# Alpha

This is super-alpha right now.  I want to make the API a bit cleaner, introduce some object that ease lookup and reference, and just generally move a step farther up from this fairly "raw" level.

Expect the API to be in flux a bit.

