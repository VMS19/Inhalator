#!/usr/bin/env python3
import abc
import argparse


class Script(object):
    def __init__(self):
        self._parser = argparse.ArgumentParser()

    @abc.abstractmethod
    def _main(self, args, pre_run_variables):
        """Main logic of the script."""
        pass

    def _pre_run(self, args):
        return {}

    def _post_run(self, args, pre_run_variables):
        pass

    def validate_parser_args(self, parser_args=None):
        self._parser.parse_args(args=parser_args)

    def run(self, parser_args=None):
        """Execution of the script with it's args."""
        args = self._parser.parse_args(args=parser_args)
        pre_run_variables = self._pre_run(args=args)
        try:
            self._main(args=args, pre_run_variables=pre_run_variables)
        finally:
            self._post_run(args=args, pre_run_variables=pre_run_variables)

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
