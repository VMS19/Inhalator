#!/usr/bin/env python3
import abc
import argparse


class Script(object):
    def __init__(self, init=False, parser_args=None):
        self._parser = argparse.ArgumentParser()
        self._initiated = init
        if init:
            self._args = self._parser.parse_args(args=parser_args)

    @classmethod
    def new(cls, parser_args=None):
        return cls(init=True, parser_args=parser_args)

    @abc.abstractmethod
    def _main(self):
        """Main logic of the script."""
        pass

    def run(self):
        """Execution of the script with it's args."""
        if self._initiated:
            self._main()

    def get_script_name(cls):
        return cls._parser.prog

    def get_script_description(cls):
        return cls._parser.description

    def get_script_usage(cls):
        return cls._parser.format_usage()

    def print_script_usage(cls):
        return cls._parser.print_usage()

    def get_script_help(cls):
        return cls._parser.format_help()

    def print_script_help(cls):
        return cls._parser.print_help()
