import logging.handlers
import os

# Note: both Logger and Handler has a log_level. The level set in the logger determines which 
#       severity of messages it will pass to its handlers. The level set in each handler 
#       determines which messages that handler will send on. So the level of Logger need to be
#       as low as the lowest handler.

# INITIALIZE ROOT LOGGER
_log_format = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
_log_formatter = logging.Formatter(_log_format)

logging.basicConfig(
    level=logging.DEBUG,  # Level of the Root logger (see the Note above)
    format=_log_format)
logging.info(f"Root logger initialized to console log (DEBUG level)")

_handlers = []
_logger_dict = dict()

# CONFIGURE THE CONSOLE HANDLER
_console_log_level = logging.getLevelName(
    os.environ['LOGGING_CONSOLE_LOG_LEVEL']) if 'LOGGING_CONSOLE_LOG_LEVEL' in os.environ else logging.DEBUG

_root = logging.getLogger()
logging.info(f'Handlers for the Root Logger: {_root.handlers}')
if len(_root.handlers) != 1:
    logging.error('The Root Logger has been initialized with a number of handlers different than 1')
else:
    _root.handlers[0].setLevel(_console_log_level)
    logging.info(f'Default handler for the Root Logger at severity {logging.getLevelName(_console_log_level)}')

_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_log_formatter)
_console_handler.setLevel(_console_log_level)
logging.info(f'Console Handler log level set to {logging.getLevelName(_console_log_level)}')

_handlers.append(_console_handler)

# CONFIGURE THE FILE HANDLER
if 'LOGGING_FILE_ENABLED' not in os.environ or os.environ['LOGGING_FILE_ENABLED'].lower() == 'true':

    _log_filename = os.environ['LOGGING_FILENAME'] if 'LOGGING_FILENAME' in os.environ else 'custom_exporter.log'
    _log_filesize = int(
        os.environ['LOGGING_ROTATION_FILESIZE']) if 'LOGGING_ROTATION_FILESIZE' in os.environ else 500 * 1024
    _log_retention = int(os.environ['LOGGING_ROTATION_RETENTION']) if 'LOGGING_ROTATION_RETENTION' in os.environ else 3
    logging.info(f'LOGGING_FILENAME={_log_filename} '
                 f'LOGGING_ROTATION_FILESIZE={_log_filesize} '
                 f'LOGGING_ROTATION_RETENTION={_log_retention}')
    # _file_handler = logging.FileHandler(_log_filename)
    _file_handler = logging.handlers.RotatingFileHandler(filename=_log_filename, maxBytes=_log_filesize,
                                                         backupCount=_log_retention)
    _file_handler.setFormatter(_log_formatter)
    _file_log_level = logging.getLevelName(
        os.environ['LOGGING_FILE_LOG_LEVEL']) if 'LOGGING_FILE_LOG_LEVEL' in os.environ else logging.DEBUG
    _file_handler.setLevel(_file_log_level)
    logging.info(f'File Handler log level set to {logging.getLevelName(_file_log_level)}')

    _handlers.append(_file_handler)

    _root.addHandler(_file_handler)
    logging.info(
        'Added the File Handler to the Root Logger: from now the messages from the Root Logger will be show in this file')
else:
    logging.info('File Handler for logs disabled (only console handler)')


def get_logger(logger_name):
    if logger_name not in _logger_dict:
        log = logging.getLogger(logger_name)
        log.setLevel(logging.DEBUG)  # Level of the logger (see the Note above)
        log.propagate = False
        for handler in _handlers:
            # for handler in _file_handler,:
            log.addHandler(handler)
        _logger_dict[logger_name] = log
        logging.info(f"Created logger '{logger_name}' with handlers {_logger_dict[logger_name].handlers}")
    return _logger_dict[logger_name]
