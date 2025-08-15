import logging

def setup_logger():
    logger = logging.getLogger("markitdown-converter")
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s | %(message)s')
    ch.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(ch)
    return logger
