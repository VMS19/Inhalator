#!/usr/bin/env python3
import argparse

from remote_wd_mute import RemoteWDMute
from upgrade_script import UpgradeScript
from rtc_update_script import RemoteRTCUpdate
from scp_transfer_script import ScpTransferScript


scripts = [
    RemoteWDMute(),
    RemoteRTCUpdate(),
    ScpTransferScript(),
    UpgradeScript()
]
scripts_names = [script.get_script_name() for script in scripts]
running_scripts_text = []


def parse_script_cmd(script_cmd, common_arguments=None):
    script_cmdline = script_cmd.split()
    script_name = script_cmdline[0]
    script_arguments = script_cmdline[1:] if len(script_cmdline) > 1 else []
    if common_arguments is not None:
        script_arguments = common_arguments.split() + script_arguments

    if script_name not in scripts_names:
        raise ValueError("Invalid script name was given.")

    running_scripts_text.append(" ".join([script_name] + script_arguments))
    script = scripts[scripts_names.index(script_name)]
    return script.new(parser_args=script_arguments)


def print_script_info(script):
        print("+----Script----")
        print("| Script name: " + script.get_script_name())
        print("| Script description: " + script.get_script_description())
        print("| " + script.get_script_usage()[:-1])
        print("+--------------")


def main():
    parser = argparse.ArgumentParser()
    parser_actions_group = parser.add_mutually_exclusive_group(required=True)
    parser_actions_group.add_argument('-ps', '--print_scripts', action='store_true',
                                      help='Show information about all available scripts.')
    parser_actions_group.add_argument('-ph', '--print_help', choices=scripts_names, metavar='script-name',
                                      help='Print the help information for a given script.')
    parser_actions_group.add_argument('-pu', '--print_usage', choices=scripts_names, metavar='script-name',
                                      help='Print the usage information for a given script.')
    parser_actions_group.add_argument('-rs', '--run_scripts', nargs='+', metavar='"script1 arg1 arg2 .." [..]',
                                   help='Run the given scripts - you can add arguments to the script'
                                                       'as well.')
    parser.add_argument('-cargs', '--common_arguments', nargs='?', metavar='"arg1 [..]"',
                                   help='Run all of the given scripts with the given common arguments.'
                                        'Dependency: --rs/--run-scripts')
    args = parser.parse_args()

    if args.common_arguments and not args.run_scripts:
        parser.error("-cargs argument depends on -rs argument.")

    if args.print_scripts:
        for script in scripts:
            print_script_info(script)
    elif args.print_help:
        script = scripts[scripts_names.index(args.print_help)]
        script.print_script_help()
    elif args.print_usage:
        script = scripts[scripts_names.index(args.print_usage)]
        script.print_script_usage()
    elif args.run_scripts:
        if isinstance(args.run_scripts, list):
            run_scripts = []

            for script_cmd in args.run_scripts:
                run_scripts.append(parse_script_cmd(script_cmd, args.common_arguments))

            for i in range(len(run_scripts)):
                print(f"Running: {running_scripts_text[i]}")
                run_scripts[i].run()
        else:
            script_cmd = args.run_scripts
            script = parse_script_cmd(script_cmd, args.common_arguments)
            script.run()


if __name__ == "__main__":
    main()
