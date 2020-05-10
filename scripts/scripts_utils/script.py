#!/usr/bin/env python3
"""Contains the abstract class to describe a script."""
import abc
import argparse


class Script(object):
    """Abstract class to describe a script."""
    def __init__(self):
        # First initiailization of the script's argument parser.
        self._parser = argparse.ArgumentParser()

    @abc.abstractmethod
    def _main(self, args, pre_run_variables):
        """
        Main logic of the script.
        :param args: the script's arguments passed from the argument parser.
        :param pre_run_variables: the script's variables set from the pre run function.
        """
        pass

    def _pre_run(self, args):
        """
        Return variables that will be passed to the script's main.
        :param args: the script's arguments passed from the argument parser.
        :return: dict of variables set before running the script's main.
        """
        return {}

    def _post_run(self, args, pre_run_variables):
        """
        Free all the allocated memory/opened connections/other that was done in the pre run function.
        :param args: the script's arguments passed from the argument parser.
        :param pre_run_variables: the script's variables set from the pre run function.
        """
        pass

    def validate_parser_args(self, parser_args=None):
        """
        Try to parse the given arguments with the script's argument parser.
        :param parser_args: the arguments to parser.
        """
        self._parser.parse_args(args=parser_args)

    def run(self, parser_args=None):
        """
        Execute the script's logic with the given arguments.
        :param parser_args: the arguments to pass to the script's argument parser.
        """
        # The arguments passed from the script's argument parser.
        args = self._parser.parse_args(args=parser_args)
        # The variables set from the script's pre run function.
        pre_run_variables = self._pre_run(args=args)
        try:
            # Execute the main logic with the arguments and variables.
            self._main(args=args, pre_run_variables=pre_run_variables)
        finally:
            # Free anything if needed in the post run function.
            self._post_run(args=args, pre_run_variables=pre_run_variables)

    def get_script_name(cls):
        """
        Return the script's name according to the argument parser.
        :return: str - the script's name.
        """
        return cls._parser.prog

    def get_script_description(cls):
        """
        Return the script's description according to the argument parser.
        :return: str - the script's description.
        """
        return cls._parser.description

    def get_script_usage(cls):
        """
        Return the script's usage according to the argument parser.
        :return: str - the script's usage.
        """
        return cls._parser.format_usage()

    def print_script_usage(cls):
        """
        Print the script's usage.
        """
        cls._parser.print_usage()

    def get_script_help(cls):
        """
        Return the script's help message according to the argument parser.
        :return: str - the script's help message.
        """
        return cls._parser.format_help()

    def print_script_help(cls):
        """
        Print the script's help message.
        """
        cls._parser.print_help()
