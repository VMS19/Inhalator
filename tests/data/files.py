from os.path import join, dirname

DATA_DIR = dirname(__file__)


def path_to_file(name):
    return join(DATA_DIR, name)
