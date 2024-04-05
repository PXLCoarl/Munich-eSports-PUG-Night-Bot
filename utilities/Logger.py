from logging import Logger, basicConfig, INFO, getLogger



def get_logger(name: str) -> Logger:
    basicConfig(
    level=INFO,
    format='%(asctime)s [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
    )
    return getLogger(name=name)