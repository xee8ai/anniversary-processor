#!/usr/bin/env python3

from xeeTools import dd, ex_to_str


class BaseProcessor():
    '''This is the base class holding all methods re-used by derived classes.'''

    def __init__(self):
        pass

    def usage(self):
        pass


class ShellProcessor(BaseProcessor):
    '''This holds the functionality to get anniversaries to your shell – e.g. for calling from .bashrc.'''


if __name__ == '__main__':
    bp = BaseProcessor()
    bp.usage()
