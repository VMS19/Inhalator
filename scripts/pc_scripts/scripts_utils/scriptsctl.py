#!/usr/bin/env python3
import shlex

from scripts_utils.script import Script


def print_script_info(script):
    print("+----Script----")
    print("| Script name: " + script.get_script_name())
    print("| Script description: " + script.get_script_description())
    print("| " + script.get_script_usage()[:-1])
    print("+--------------")


class ScriptsCTL(Script):
    def __init__(self, scripts):
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
        script_cmdline = shlex.split(script_cmd)
        script_name = script_cmdline[0]
        script_arguments = script_cmdline[1:] if len(script_cmdline) > 1 else []

        if args.common_arguments is not None:
            script_arguments = shlex.split(args.common_arguments) + script_arguments

        if script_name not in self._scripts_names:
            raise ValueError("Invalid script name was given.")

        self._running_scripts_text.append(" ".join([script_name] + script_arguments))
        script = self._scripts[self._scripts_names.index(script_name)]
        script.validate_parser_args(parser_args=script_arguments)
        return script, script_arguments

    def _main(self, args, pre_run_variables):
        if args.common_arguments and not args.run_scripts:
            self._parser.error("-cargs argument depends on -rs argument.")

        if args.print_scripts:
            for script in self._scripts:
                print_script_info(script)
        elif args.print_help:
            script = self._scripts[self._scripts_names.index(args.print_help)]
            script.print_script_help()
        elif args.print_usage:
            script = self._scripts[self._scripts_names.index(args.print_usage)]
            script.print_script_usage()
        elif args.run_scripts:
            if isinstance(args.run_scripts, list):
                run_scripts = []

                for script_cmd in args.run_scripts:
                    run_scripts.append(self._parse_script_cmd(script_cmd, args))

                for i in range(len(run_scripts)):
                    print(f"Running: {self._running_scripts_text[i]}")
                    run_scripts[i][0].run(run_scripts[i][1])
            else:
                script_cmd = args.run_scripts
                script = self._parse_script_cmd(script_cmd, args)
                script.run()
