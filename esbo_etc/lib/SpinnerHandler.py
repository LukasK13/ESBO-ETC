import logging
import halo


class SpinnerHandler(logging.Handler):
    """
    A handler for the logging-package to allow a spinner indicate an ongoing calculation.

    The spinner is started by a log-message with the extra-key 'spinning':
    logger.info("running...", extra={"spinning": True})
    logger.info("end", extra={"spinning": False})
    """

    def __init__(self, spinner: halo.Halo = halo.Halo(spinner="moon"), level: int = logging.NOTSET):
        """
        Initialize a new spinner handler

        Parameters
        ----------
        spinner : Halo
            The spinner to show.
        level : int
            The logging level of this handler.
        """
        # Initialize super class
        super(SpinnerHandler, self).__init__(level)
        # save spinner
        self._spinner = spinner
        # set variable of current spinning status to False
        self._spinning = False

    def filter(self, record):
        """
        Check if this handler should be applied on the given log record.

        Parameters
        ----------
        record : LogRecord
            The log record to be checked

        Returns
        -------
        res : bool
            True if this handler should be applied on the given log record, otherwise False.
        """
        if hasattr(record, 'spinning'):
            return True
        else:
            return self._spinning

    def emit(self, record):
        """
        Add a spinner to the given log record and emit the final record.

        Parameters
        ----------
        record : LogRecord
            The log record to be extended.

        Returns
        -------
        record : LogRecord
            The extended log record.
        """
        if hasattr(record, 'spinning'):
            # extra-key 'spinning' is given in the log record
            if getattr(record, "spinning") != self._spinning:
                # spinner state has to be changed
                if getattr(record, "spinning"):
                    # start spinner
                    self._spinning = True
                    self._spinner.start(record.msg)
                else:
                    # stop spinner
                    self._spinning = False
                    self._spinner.stop()
            elif getattr(record, "spinning"):
                # Change spinner text
                self._spinner.text = record.msg
        if self._spinning:
            # clear the spinner before emitting the record in order to avoid doubled messages
            self._spinner.clear()
            # record.msg = "\r\033[K" + record.msg
            return record
