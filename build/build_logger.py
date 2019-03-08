import logging
import os
import sys

def create_logger(name):
    log_file = f"{name}.log"
    if os.path.exists(log_file):
        os.remove(log_file)

    logger = logging.getLogger('name')
    logger.setLevel(logging.DEBUG)

    log_format = logging.Formatter("%(asctime)s [%(levelname)-5.5s ] %(message)s")

    file_handler = logging.FileHandler('build.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

if __name__ == "__main__":
    create_logger()