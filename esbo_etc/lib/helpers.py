import logging
import sys
import traceback


def error(msg: str, exit_: bool = True):
    """
    Handle errors

    Parameters
    ----------
    msg : str
        Error message to show
    exit_ : bool
        Exit program

    Returns
    -------

    """
    logging.error(msg)
    if exit_:
        traceback.print_stack()
        sys.exit(1)


def isLambda(v: object):
    """
    Check if a object is of type lambda

    Parameters
    ----------
    v : object
        The object to check.

    Returns
    -------
    res : bool
        Result of the check
    """
    return isinstance(v, type(lambda: None)) and v.__name__ == (lambda: None).__name__
