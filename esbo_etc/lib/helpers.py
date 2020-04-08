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
