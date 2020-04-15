import logging
import sys
import traceback
import astropy.units as u
from astropy.modeling.models import BlackBody
from typing import Union


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
    LAMBDA = lambda: 0
    return isinstance(v, type(LAMBDA)) and v.__name__ == LAMBDA.__name__
