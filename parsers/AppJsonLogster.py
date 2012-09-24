import json
import time

import statsd

from logster_helper import MetricObject, LogsterParser
from logster_helper import LogsterParsingException

class AppJsonLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.criticality_names = {
            0 : 'emerg',
            1 : 'alert',
            2 : 'crit',
            3 : 'err',
            4 : 'warning',
            5 : 'notice',
            6 : 'info',
            7 : 'debug' 
        }
        self.metrics = {}
        self.statsd = statsd.StatsClient()
        
    def parse_line(self, line):
        '''This function should digest the contents of one line at a time,
        updating object's state variables.

        Takes a single argument, the line to be parsed.'''

        try:
            data = json.loads(line)
        except Exception, e:
            raise LogsterParsingException, "Failing to decode line %s" % e

        try:
            level = int(data['criticality'])
        except KeyError:
            raise LogsterParsingException, "criticality not found"

        name = "app.events.crit.%s" % (self.criticality_name[level])
        self.statsd.incr(name)
        if name in self.metrics:
            self.metrics[name].value += 1
        else:
            self.metrics[name] = MetricObject(name, 1)

    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        # Return a list of metrics objects
        return self.metrics.values()
