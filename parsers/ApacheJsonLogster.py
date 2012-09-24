###  A sample logster parser file that can be used to count the number
###  of response codes found in an Apache access log.
###
###  For example:
###  sudo ./logster --dry-run --output=ganglia SampleLogster /var/log/httpd/access_log
###
###
###  Copyright 2011, Etsy, Inc.
###
###
###  Logster is free software: you can redistribute it and/or modify
###  it under the terms of the GNU General Public License as published by
###  the Free Software Foundation, either version 3 of the License, or
###  (at your option) any later version.
###
###  Logster is distributed in the hope that it will be useful,
###  but WITHOUT ANY WARRANTY; without even the implied warranty of
###  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
###  GNU General Public License for more details.
###
###  You should have received a copy of the GNU General Public License
###  along with Logster. If not, see <http://www.gnu.org/licenses/>.
###
import json

import statsd

from logster_helper import MetricObject, LogsterParser
from logster_helper import LogsterParsingException

class ApacheJsonLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
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
            status = str(data['statusCode'])
        except KeyError:
            raise LogsterParsingException, "statusCode not found"
        name = "http.response.status.%s" % (status)
        statsd.incr(name)
        if name in self.metrics:
            self.metrics[name].value += 1
        else:
            self.metrics[name] = MetricObject(name, 1)

        name_type = "http.response.status.%sxx" % (status[0])
        statsd.incr(name_type)
        if name_type in self.metrics:
            self.metrics[name_type].value += 1
        else:
            self.metrics[name_type] = MetricObject(name_type, 1)
        
    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        return self.metrics.values()
