from logster_helper import MetricObject, LogsterParser

class HttpPhpErrorLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.phpErrorLinesMetric = MetricObject(name='http.php.errorLines',
                                                value=0,
                                                type='gauge')
        
    def parse_line(self, line):
        '''This function should digest the contents of one line at a time,
        updating object's state variables.

        Takes a single argument, the line to be parsed.'''

        self.phpErrorLinesMetric.value += 1

    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        # Return a list of metrics objects
        return [self.phpErrorLinesMetric]
