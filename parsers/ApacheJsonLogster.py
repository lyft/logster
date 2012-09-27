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

from logster_helper import MetricObject, LogsterParser
from logster_helper import LogsterParsingException

class ApacheJsonLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''
        self.metrics = {
            # Make sure we always report the number of 500 errors found
            "http.response.status.5xx.500": MetricObject(
                name="http.response.status.5xx.500",
                value=0, type='gauge'),
            "http.response.status.5xx": MetricObject(
                name="http.response.status.5xx",
                value=0, type='gauge'),
            # Always report the total number of requests
            "http.request.total": MetricObject(
                name="http.request.total",
                value=0, type='counter')
        }

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
        status_type = "%sxx" % (status[0])

        name = "http.response.status.%s" % (status_type)
        if name in self.metrics:
            self.metrics[name].value += 1
        else:
            self.metrics[name] = MetricObject(name=name, value=1, type='counter')

        name = "http.response.status.%s.%s" % (status_type, status)
        if name in self.metrics:
            self.metrics[name].value += 1
        else:
            self.metrics[name] = MetricObject(name=name, value=1, type='counter')

        self.metrics["http.request.total"].value += 1
        
    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''
        return self.metrics.values()
