import os
from configparser import ConfigParser
from pathlib import Path


BASE_PATH = Path(__file__).parent.parent
config_PATH = os.path.join(BASE_PATH, 'database.ini')


def config_parser(filename="database.ini", section="postgresql"):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, filename))
    return db


config = config_parser(config_PATH)
