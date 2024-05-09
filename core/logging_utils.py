import logging
import logging.config
from logging_module import logging_module, constants
import threading
# import config
setup_logger_lock = threading.Lock()


def setup_logger(logger_name, log_file=None, level='DEBUG', use_stream_handler=0):
    config = logging_module.create_and_load_config_file()
    logging.config.dictConfig(config)

    if not use_stream_handler:
        my_logger = logging_module.create_logger(logger_name, [constants.CONST_ROTATING_FILE_HANDLER], logging_level=level)
    else:
        my_logger = logging_module.create_logger(logger_name, [constants.CONST_STREAM_HANDLER], logging_level=level)

    return my_logger
