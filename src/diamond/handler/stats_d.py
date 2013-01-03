# coding=utf-8

"""
Implements the abstract Handler class, sending data to statsd.
This is a UDP service, sending datagrams.  They may be lost.
It's OK.

#### Dependencies

 * [python-statsd](http://pypi.python.org/pypi/python-statsd/)
 * [statsd](https://github.com/etsy/statsd) v0.1.1 or newer.

#### Configuration

Enable this handler

 * handlers = diamond.handler.stats_d.StatsdHandler


#### Notes

If your system has both
[python-statsd](http://pypi.python.org/pypi/python-statsd/)
and [statsd](http://pypi.python.org/pypi/statsd/) installed, you might
experience failues after python updates or pip updates that change the order of
importing. We recommend that you only have
[python-statsd](http://pypi.python.org/pypi/python-statsd/)
installed on your system if you are using this handler.

The handler file is named an odd stats_d.py because of an import issue with
having the python library called statsd and this handler's module being called
statsd, so we use an odd name for this handler. This doesn't affect the usage
of this handler.

"""

from Handler import Handler
import statsd
import logging


class StatsdHandler(Handler):

    def __init__(self, config=None):
        """
        Create a new instance of the StatsdHandler class
        """
        # Initialize Handler
        Handler.__init__(self, config)
        logging.debug("Initialized statsd handler.")
        # Initialize Options
        self.host = self.config['host']
        self.port = int(self.config['port'])

        # Connect
        self._connect()

    def process(self, metric):
        """
        Process a metric by sending it to statsd
        """
        # Just send the data as a string
        self._send(metric)

    def _send(self, metric):
        """
        Send data to statsd. Fire and forget.  Cross fingers and it'll arrive.
        """
        # Split the path into a prefix and a name
        # to work with the statsd module's view of the world.
        # It will get re-joined by the python-statsd module.
        (path, name) = metric.path.rsplit(".", 1)
        (prefix, hostname, metric_name) = metric.path.split(".", 2)
        logging.debug("Sending Hostname:{0}; Prefix:{1}; Metric_name:{2}; Value:{3}".format(hostname, prefix, metric_name, metric.value))
        statsd.Gauge("{0}.{1}".format(metric_name, prefix), self.connection).send(hostname, metric.value)

    def _connect(self):
        """
        Connect to the statsd server
        """
        # Create socket
        self.connection = statsd.Connection(
            host=self.host,
            port=self.port,
            sample_rate=1.0
        )
