`python-batsd` is a thin wrapper for getting data out of a [batsd](https://github.com/noahhl/batsd) server.

`batsd` exposes a TCP interface, on port 8127 by default, where you can access the data values that you store into it.  This library provides a simple(-ish) way to get at that data.

# Installation

```console
$ git clone https://github.com/jmhobbs/python-batsd.git && cd python-batsd && python setup.py install
```

# Usage

```python
>>> from time import time
>>> from batsd import Connection
>>> c = Connection()
>>> c.ping()
True
>>> c.counters()
[<batsd.Counter "Test">, <batsd.Counter "Sample.tick">]
>>> sample = c.counter('Sample')
>>> dataset = sample.get(int(time())-60, int(time()), 'tick')
>>> print dataset.size
24
>>> print dataset.interval
1
>>> for point in dataset:
...     print point[1]
... 
17.0
17.0
20.0
30.0
20.0
20.0
20.0
20.0
4.0
10.0
9.0
15.0
5.0
31.0
13.0
3.0
18.0
4.0
5.0
13.0
23.0
17.0
1.0
2.0
>>> 
```

# Alpha

I'm still playing with the API, especially where top level names meet subnames and access patterns around that.

Expect the API to be in flux a bit.

