import logging


def setup_logger():
    logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(name=__name__) 