import logging.handlers


'''
Same thing as logging.getLogger, but with a pep-8 alias.
'''
get_logger = logging.getLogger


def config_rotating_file_handler_from_env_var(env_var, log_filename, logger_name=''):
    '''
    :param env_var:
        The name of the environment variable to check. Valid values for it are:
        'CRITICAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG'

        it may also be preceded by:
        'ONLY_STDOUT:', in which case the file won't be put in log_filename and will only be
        logged to stdout/stderr streams with a StreamHandler.

    :param log_filename:
        The place where the log filename should be set.

    :param logger_name:
        The name of the logger to which the handler should be added.
    '''
    import os
    logging_level = os.environ.get(env_var, 'WARN').upper()

    only_stdout = False
    if logging_level.startswith('ONLY_STDOUT:'):
        only_stdout = True
        logging_level = logging_level[len('ONLY_STDOUT:'):]

    valid_levels = set(['CRITICAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG'])
    msg = ''
    if logging_level not in valid_levels:
        msg = 'Invalid logging level on env var: %s: %s' % (env_var, logging_level)
        logging_level = 'WARN'

    logger = get_logger(logger_name)
    logger.setLevel(logging_level)

    if only_stdout:
        handler = logging.StreamHandler()
    else:
        handler = logging.handlers.RotatingFileHandler(
            log_filename, maxBytes=1024 * 1024, backupCount=5, encoding='utf-8')

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    if msg:
        get_logger(__name__).warn(msg)
