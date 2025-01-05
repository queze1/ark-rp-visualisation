import logging


def get_logger(name: str):
    if not logging.root.hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

    return logging.getLogger(name)
