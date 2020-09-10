from abc import abstractmethod
from .Entry import Entry
from .IRadiant import IRadiant
from ..lib.logger import logger
import copy
import re


class AFactory:
    """
    A Factory for creating objects of the radiation transportation pipeline
    """

    @abstractmethod
    def __init__(self, common_conf: Entry):
        """
        Instantiate a new factory object

        Parameters
        ----------
        common_conf : Entry
            The common configuration of the configuration file
        """
        self._common_conf = common_conf

    @abstractmethod
    def create(self, options: Entry, parent: IRadiant = None):
        """
        Create a new object of the radiation transportation pipeline

        Parameters
        ----------
        options : Entry
            The options to be used as parameters for the instantiation of the new object.
        parent : IRadiant
            The optional parent element of the object (necessary for subclasses of AOpticalComponent and ASensor).
        Returns
        -------
        obj
            The created object
        """
        pass

    def collectOptions(self, options: Entry) -> dict:
        """
        Collect all options from the configuration file as dictionary

        Parameters
        ----------
        options : Entry
            The options to be used as parameters for the instantiation of the new object.

        Returns
        -------
        opts : dict
            The collected options as dictionary
        """
        # if hasattr(options, "type"):
        # Copy custom attributes of the Entry to a dictionary
        opts = copy.copy(vars(options))

        for i in vars(options):
            obj = getattr(options, i)
            if isinstance(obj, Entry):
                opts.pop(i, None)
                additional_opts = self.collectOptions(obj)
                if len(additional_opts) == 1 and list(additional_opts.keys())[0] == "val":
                    additional_opts[i] = additional_opts.pop("val")
                opts.update(additional_opts)

        # Remove unnecessary keys
        for attrib in list(filter(re.compile(".*_unit$").match, opts)) + ["comment", "type"]:
            opts.pop(attrib, None)
        return opts
        # else:
        #     logger.error("Component needs to have a type specified.")
