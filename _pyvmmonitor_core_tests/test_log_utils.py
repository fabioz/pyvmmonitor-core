from pyvmmonitor_core import log_utils
from pyvmmonitor_core.compat import unicode


def test_log_utils(tmpdir):
    import os
    logger = log_utils.get_logger('test_log_utils')
    log_filename = os.path.join(unicode(tmpdir.ensure_dir()), 'test_log_utils.log')

    os.environ['TEST_LOG_ENV_VAR'] = 'DEBUG'
    log_utils.config_rotating_file_handler_from_env_var(
        'TEST_LOG_ENV_VAR', log_filename, logger_name='test_log_utils')

    logger.warn('warn')
    logger.info('info')
    logger.debug('debug')
    try:
        raise RuntimeError('ThisException')
    except Exception:
        logger.exception('SomeException')

    # We have something as:
    # 2017-05-18 10:35:02,033 - test_log_utils - WARNING : warn
    # 2017-05-18 10:35:02,033 - test_log_utils - INFO : info
    # 2017-05-18 10:35:02,035 - test_log_utils - DEBUG : debug
    # 2017-05-18 10:35:02,035 - test_log_utils - ERROR : SomeException
    # Traceback (most recent call last):
    #   File "X:\pyvmmonitor-core\_pyvmmonitor_core_tests\test_log_utils.py", line 17, in test_log_utils
    #     raise RuntimeError('ThisException')
    # RuntimeError: ThisException

    # Let's compare the file endings.
    expected = '''- test_log_utils - WARNING : warn
- test_log_utils - INFO : info
- test_log_utils - DEBUG : debug
- test_log_utils - ERROR : SomeException
Traceback (most recent call last):
in test_log_utils
raise RuntimeError('ThisException')
RuntimeError: ThisException
'''

    with open(log_filename, 'r') as stream:
        lines = stream.read().splitlines()
        assert len(lines) == 8
        for expected_line, found_line in zip(expected.splitlines(), lines):
            assert found_line.endswith(expected_line)
