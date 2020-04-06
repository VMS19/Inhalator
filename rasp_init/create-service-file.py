import sys
import os

from os.path import dirname, join, abspath, isfile

import argparse


template = """\
[Unit]
Description=Inhalator Service

[Service]
ExecStart={python3_executable} {main_path}
WorkingDirectory={main_dir}
Environment=DISPLAY={display}
Environment=XAUTHORITY={xauthority}
Restart=always
Type=simple

[Install]
WantedBy=default.target
"""


def generate(output_file, python):
    main_dir = dirname(dirname(abspath(__file__)))
    main_path = join(main_dir, "main.py")
    if not isfile(main_path):
        raise FileNotFoundError(main_path)

    contents = template.format(
        main_path=main_path,
        python3_executable="/home/pi/Inhalator/.inhalator_env/bin/python3",
        main_dir=main_dir,
        xauthority=os.environ["XAUTHORITY"],
        display=os.environ["DISPLAY"]
    )
    with open(output_file, "w") as f:
        f.write(contents)

    print("Created service file at %s:" % output_file)
    print()
    print(contents)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_file", "-o",
        help="The path of the generated service file")
    parser.add_argument(
        "--python", "-p",
        help="The name/path of the python interpreter that will be used to start the service",
        default="/usr/bin/env python3")
    args = parser.parse_args()

    generate(output_file=args.output_file, python=args.python)
