#!/usr/bin/env python3
import abc
import argparse


class Script(object):
    def __init__(self, parser_args=None):
        self._args = self._parser.parse_args(args=parser_args)

    @classmethod
    def new(cls, parser_args=None):
        return cls(parser_args)

    @abc.abstractmethod
    def run(self):
        """Execution of the script with it's args."""
        pass

    @classmethod
    def get_script_name(cls):
        return cls._parser.prog

    @classmethod
    def get_script_description(cls):
        return cls._parser.description

    @classmethod
    def get_script_usage(cls):
        return cls._parser.format_usage()

    @classmethod
    def print_script_usage(cls):
        return cls._parser.print_usage()

    @classmethod
    def get_script_help(cls):
        return cls._parser.format_help()

    @classmethod
    def print_script_help(cls):
        return cls._parser.print_help()
