from logging import basicConfig, ERROR, getLogger
from datetime import datetime
from functools import wraps
from filetools import cfg_path

basicConfig(filename=cfg_path('log.ini'), level=ERROR, format='%(levelname)s %(asctime)s - %(message)s')
logger = getLogger()


def log(func):
    """
    basic logging decorator
    :param func: decorated function
    :return: the return of the decorated function
    """
    @wraps(func)
    def call(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f'\n+', '-'*17, '+', '-'*81,
              f'\n|\tTime:\t\t\t|\t{datetime.now().strftime("%H:%M:%S")}\n'
              f'|\tSync:\t\t\t|\tTrue\n'
              f'|\tFunction:\t\t|\t{func.__name__}\n'
              f'|\targs:\t\t\t|\t{args}\n'
              f'|\tkwargs:\t\t\t|\t{kwargs}\n'
              f'|\tResult:\t\t\t|\t{result}',
              f'\n+', '-' * 17, '+', '-' * 81)
        if type(result) is str:
            if result.startswith('Error: ') is True:
                logger.error(f'Function: {func.__name__}, args: {args}, kwargs {kwargs}, Result: {result[7:]}')
        return result
    return call


def async_log(func):
    """
    basic logging decorator for asynchronous Functions
    :param func: decorated function
    :return: the return of the decorated function
    """
    @wraps(func)
    async def call(*args, **kwargs):
        result = await func(*args, **kwargs)
        print(f'\n+', '-'*17, '+', '-'*81,
              f'\n|\tTime:\t\t\t|\t{datetime.now().strftime("%H:%M:%S")}\n'
              f'|\tSync:\t\t\t|\tFalse\n'
              f'|\tFunction:\t\t|\t{func.__name__}\n'
              f'|\targs:\t\t\t|\t{args}\n'
              f'|\tkwargs:\t\t\t|\t{kwargs}\n'
              f'|\tResult:\t\t\t|\t{result}',
              f'\n+', '-' * 17, '+', '-' * 81)
        if type(result) is str:
            if result.startswith('Error: ') is True:
                logger.error(f'Function: {func.__name__}, args: {args}, kwargs {kwargs}, Result: {result[7:]}')
        return result
    return call
