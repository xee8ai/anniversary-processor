#!/usr/bin/env python3

import configparser
import datetime
import os.path
import re
import sys
from xeeTools import dd, ex_to_str

################################################################################
################################################################################
class BaseProcessor():
    '''This is the base class holding all methods re-used by derived classes.'''

    data = dict()


################################################################################
    def __init__(self):
        self._set_env()
        self._readConfig()
        self._prepare_data()


################################################################################
    def _set_env(self):
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.config_dir = os.path.join(script_dir[:-3], 'etc')


################################################################################
    def run(self):

        print('No output from BaseProcessor')


################################################################################
    def _readConfig(self):
        self.config = dict()
        self.config['monthly'] = configparser.ConfigParser()
        self.config['monthly'].read(os.path.join(self.config_dir, 'monthly.cfg'))
        self.config['yearly'] = configparser.ConfigParser()
        self.config['yearly'].read(os.path.join(self.config_dir, 'yearly.cfg'))


################################################################################
    def _prepare_data(self):

        this_year = datetime.datetime.now().year
        next_year = this_year + 1

        year_regex = re.compile('[12][0-9]{3}')

        for interval in self.config.keys():

            for section in self.config[interval].sections():

                if self.config[interval].has_option(section, 'symbol'):
                    symbol = self.config[interval].get(section, 'symbol')
                else:
                    symbol = '?'

                for option in self.config[interval].options(section):
                    if option ==  'symbol':
                        continue

                    tmp = self.config[interval].get(section, option)
                    cur_key = '{}'.format(this_year) + '-' + tmp[-5:]
                    next_key = '{}'.format(next_year) + '-' + tmp[-5:]

                    if cur_key not in self.data.keys():
                        self.data[cur_key] = []
                    if next_key not in self.data.keys():
                        self.data[next_key] = []

                    cur_data = symbol + '  {}'.format(option.upper())
                    next_data = symbol + '  {}'.format(option.upper())

                    if year_regex.match(tmp[:4]):
                        age = this_year - int(tmp[:4])
                        cur_data += ' ({})'.format(age)
                        next_data += ' ({})'.format(age + 1)

                    self.data[cur_key].append(cur_data)
                    self.data[next_key].append(next_data)



################################################################################
################################################################################
class ShellProcessor(BaseProcessor):
    '''This holds the functionality to get anniversaries to your shell.'''

    lines = []

################################################################################
    def run(self):
        self._build_lines()
        self._print()


################################################################################
    def _build_lines(self):

        last_week = (datetime.datetime.today() - datetime.timedelta(7)).strftime('%Y-%m-%d')
        today = (datetime.datetime.today()).strftime('%Y-%m-%d')
        next_week = (datetime.datetime.today() + datetime.timedelta(7)).strftime('%Y-%m-%d')
        next_month = (datetime.datetime.today() + datetime.timedelta(30)).strftime('%Y-%m-%d')

        self.lines.append('')

        last_time = ''

        for date, entries in sorted(self.data.items()):

            if date < last_week:
                continue

            if date > next_month:
                continue

            for entry in entries:

                if date < today:
                    cur_time = 'last_week'
                elif date == today:
                    cur_time = 'today'
                elif date <= next_week:
                    cur_time = 'next_week'
                else:
                    cur_time = 'next_month'

                if last_time and last_time != cur_time:
                    self.lines.append('')

                line = '{}:    {}'.format(date, entry)
                line = self._prepare_line(line, cur_time)

                self.lines.append(line)

                last_time = cur_time

        self.lines.append('')


################################################################################
    def _prepare_line(self, line, line_time):
        '''Use this method in your derived classes to e.g. colorize the lines.'''

        return line


################################################################################
    def _print(self):
        for line in self.lines:
            print(line)


################################################################################
    def test_output(self):

        testlines = []
        print(self._prepare_line('last_week', 'last_week'))
        print(self._prepare_line('today', 'today'))
        print(self._prepare_line('next_week', 'next_week'))
        print(self._prepare_line('next_month', 'next_month'))




################################################################################
################################################################################
class BashProcessor(ShellProcessor):
    '''This holds the functionality to get anniversaries to your bash.'''


################################################################################
    def _prepare_line(self, line, line_time):
        '''Use this method in your derived classes to e.g. colorize the lines.'''

        colors = {
                'last_week': '\033[0;31m',
                'today': '\033[1;31m',
                'next_week': '\033[0;32m',
                'next_month': '\033[0;36m',
                'clear': '\033[0m',
                }

        line = colors[line_time] + line + colors['clear']

        return line



################################################################################
################################################################################
################################################################################
if __name__ == '__main__':

    modes = ['base', 'bash']

    usage = [
            '',
            'Usage: {} [{}]'.format(sys.argv[0], ', '.join(modes)),
            '',
            '   base: reads the config',
            '   bash: output to bash',
            ]

    if len(sys.argv) != 2 or sys.argv[1] not in modes:
        for l in usage:
            print(l)
        sys.exit(1)

    if sys.argv[1] == 'base':
        processor = BaseProcessor()
    elif sys.argv[1] == 'bash':
        processor = BashProcessor()

    processor.run()
    # processor.test_output()
