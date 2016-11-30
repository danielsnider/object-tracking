import logging
import argparse

def getLogger(name, description, level=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-l','--log', help='Prints more logging', required=False)
    args = vars(parser.parse_args())

    loglevel = args['log'] or level or 'critical'

    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level, format="%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s")
    log = logging.getLogger(name)
    return log
