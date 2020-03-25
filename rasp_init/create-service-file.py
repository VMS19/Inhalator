from os.path import dirname, join, abspath, isfile

template = """\
[Unit]
Description=Inhalator Service

[Service]
ExecStart=/usr/bin/env python3 {main_path}
Restart=on-failure
Type=simple

[Install]
WantedBy=default.target
"""


def generate():
    main_path = join(dirname(dirname(abspath(__file__))), "main.py")
    if not isfile(main_path):
        raise FileNotFoundError(main_path)

    contents = template.format(main_path=main_path)
    with open("inhalator.service", "w") as f:
        f.write(contents)


if __name__ == '__main__':
    generate()
