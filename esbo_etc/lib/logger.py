import logging
import sys
import traceback


def error(self, msg: str, exit_: bool = True):
    """
    Handle errors

    Parameters
    ----------
    self : Logger
        The logger-object
    msg : str
        Error message to show
    exit_ : bool
        Exit program

    Returns
    -------

    """
    self._error(msg)
    if exit_:
        traceback.print_stack()
        sys.exit(1)


logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s', stream=sys.stdout)
logger = logging.getLogger('etc')
logger._error = logger.error
logger.error = error.__get__(logger, logging.Logger)
