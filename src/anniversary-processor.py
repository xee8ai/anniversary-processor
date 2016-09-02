#!/usr/bin/env python3

import configparser
import os.path
from xeeTools import dd, ex_to_str
import sys

################################################################################
################################################################################
class BaseProcessor():
    '''This is the base class holding all methods re-used by derived classes.'''


################################################################################
    def __init__(self):
        self._set_env()
        self._readConfig()

        dd(self.config, self.config['yearly'].sections())


################################################################################
    def _set_env(self):
        self.config_dir = 'etc'


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
################################################################################
class ShellProcessor(BaseProcessor):
    '''This holds the functionality to get anniversaries to your shell.'''


################################################################################
    def run(self):
        print('TODO')



################################################################################
################################################################################
class BashProcessor(ShellProcessor):
    '''This holds the functionality to get anniversaries to your bash.'''


################################################################################
    def run(self):
        print('TODO')




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
