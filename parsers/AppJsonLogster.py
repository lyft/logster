import json

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
        for name in self.criticality_names.values():
            name = "app.events.crit.%s" % (name)
            self.metrics[name] = MetricObject(
                    name=name, value=0, type='gauge')
        # the total number of events we've seen
        name = 'app.events.total'
        self.metrics[name] = MetricObject(name=name, value=0, type='counter')
        # Store all emerg, alert, crit and err messages in one metric
        # so that we don't have to add rules for each one of them
        name = 'app.events.crit.allErrors'
        self.metrics[name] = MetricObject(name=name, value=0, type='gauge')
        
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

        if level not in self.criticality_names:
            logger.warn("Unknown criticality level: %s" % (level))
        else:
            name = "app.events.crit.%s" % (self.criticality_names[level])
            self.metrics[name].value += 1
            # Store all emerg, alert, crit and err messages in one metric
            # so that we don't have to add rules for each of them
            if level <= 3:
                self.metrics['app.events.crit.allErrors'] += 1
        self.metrics['app.events.total'].value += 1

    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        # Return a list of metrics objects
        return self.metrics.values()
