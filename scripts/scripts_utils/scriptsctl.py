#!/usr/bin/env python3
"""Contain all the scripts control logic."""
import shlex

from scripts.scripts_utils.script import Script


def print_script_info(script):
    """
    Print the given script's name, description and usage.
    :param script: the script to print it's information.
    """
    print("+----Script----")
    print("| Script name: " + script.get_script_name())
    print("| Script description: " + script.get_script_description())
    print("| " + script.get_script_usage()[:-1])
    print("+--------------")


class ScriptsCTL(Script):
    """Script for giving information about different scripts and allowing to execute them all together."""
    def __init__(self, scripts):
        """
        :param scripts: a list of Script instances.
        """
        super(ScriptsCTL, self).__init__()

        self._scripts = scripts
        self._scripts_names = [script.get_script_name() for script in self._scripts]
        self._running_scripts_text = []

        self._parser.prog = "scripts-ctl"
        self._parser.description = "Control all scripts."
        self._parser_actions_group = self._parser.add_mutually_exclusive_group(required=True)
        self._parser_actions_group.add_argument('-ps', '--print_scripts', action='store_true',
                                                help='Show information about all available scripts.')
        self._parser_actions_group.add_argument('-ph', '--print_help', choices=self._scripts_names, metavar='script-name',
                                                help='Print the help information for a given script.')
        self._parser_actions_group.add_argument('-pu', '--print_usage', choices=self._scripts_names, metavar='script-name',
                                                help='Print the usage information for a given script.')
        self._parser_actions_group.add_argument('-rs', '--run_scripts', nargs='+', metavar='"script1 arg1 arg2 .." [..]',
                                                help='Run the given scripts - you can add arguments to the script'
                                                'as well.')
        self._parser.add_argument('-cargs', '--common_arguments', nargs='?', metavar='"arg1 [..]"',
                                  help='Run all of the given scripts with the given common arguments.'
                                            'Dependency: --rs/--run-scripts')

    def _parse_script_cmd(self, script_cmd, args):
        """
        Return the script instance to run and the arguments to run it with according
        to the script command and the parser's 'common_arguments' argument.
        Note: This function will raise an exception if the arguments are invalid
        according to the given script's argument parser.
        :param script_cmd: the current script command.
        :param args: the arguments got from the script's argument parser.
        :return: the script that was asked for and a list of the asked arguments to run it with.
        """
        # Split the script and divide it to the script's name and arguments.
        script_cmdline = shlex.split(script_cmd)
        script_name = script_cmdline[0]
        script_arguments = script_cmdline[1:] if len(script_cmdline) > 1 else []

        # Add the common arguments to the script's arguments.
        if args.common_arguments is not None:
            script_arguments = shlex.split(args.common_arguments) + script_arguments

        # Check if the script name is indeed in the list of available script's names.
        if script_name not in self._scripts_names:
            raise ValueError("Invalid script name was given.")

        # Save the current command line with all the arguments.
        self._running_scripts_text.append(" ".join([script_name] + script_arguments))
        script = self._scripts[self._scripts_names.index(script_name)]
        # Validate that the given arguments are parsed without exception for the script.
        script.validate_parser_args(parser_args=script_arguments)
        return script, script_arguments

    def _main(self, args, pre_run_variables):
        """
        Give information about different scripts or execute scripts all together according
        to the choice given in the arguments.
        Notes:
        * When executing the scripts, the common arguments variable will be prefixed to each of
          the scripts' arguments.
        * All the scripts will start running only if all of the scripts' arguments are valid
          according to their argument parser.
        :param args: the script's arguments passed from the argument parser.
        :param pre_run_variables: the script's variables set from the pre run function.
        """
        # 'common_arguments' argument is a dependency of 'run_scripts' argument.
        if args.common_arguments and not args.run_scripts:
            self._parser.error("-cargs argument depends on -rs argument.")

        if args.print_scripts:
            # Print all scripts' information.
            for script in self._scripts:
                print_script_info(script)
        elif args.print_help:
            # Print the given script's help message(if exists).
            script = self._scripts[self._scripts_names.index(args.print_help)]
            script.print_script_help()
        elif args.print_usage:
            # Print the given script's usage(if exists).
            script = self._scripts[self._scripts_names.index(args.print_usage)]
            script.print_script_usage()
        elif args.run_scripts:
            if isinstance(args.run_scripts, list):
                # Handle several scripts to run.
                run_scripts = []

                # Add all the scripts and their arguments(will fail if one is invalid)
                for script_cmd in args.run_scripts:
                    run_scripts.append(self._parse_script_cmd(script_cmd, args))

                # Run all the scripts after validating all the scripts' arguments.
                for i in range(len(run_scripts)):
                    print(f"Running: {self._running_scripts_text[i]}")
                    run_scripts[i][0].run(run_scripts[i][1])
            else:
                # Handle one scripts to run.
                script_cmd = args.run_scripts
                script, script_arguments = self._parse_script_cmd(script_cmd, args)
                script.run(parser_args=script_arguments)
