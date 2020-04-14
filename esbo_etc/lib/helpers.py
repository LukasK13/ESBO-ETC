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


@u.quantity_input(temp=[u.Kelvin, u.Celsius])
def gb_factory(temp: u.Quantity, em: Union[int, float] = 1):
    """
    Factory for a grey body lambda-function.

    Parameters
    ----------
    temp : Quantity in Kelvin / Celsius
        The temperature fo the grey body.
    em : Union[int, float]
        Emissivity of the the grey body

    Returns
    -------
    bb : Callable
        The lambda function for the grey body.
    """
    bb = BlackBody(temperature=temp * u.K, scale=em * u.W / (u.m ** 2 * u.nm * u.sr))
    return lambda wl: bb(wl)


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
