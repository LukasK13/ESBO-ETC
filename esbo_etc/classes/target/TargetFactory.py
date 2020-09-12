from ..ARadiantFactory import ARadiantFactory
from ..Entry import Entry
from ..IRadiant import IRadiant
from .ATarget import ATarget
from ...classes import target as tg
from ...lib.logger import logger


class TargetFactory(ARadiantFactory):
    """
    A Factory creating objects of the type IRadiant
    """

    def __init__(self, common_conf: Entry):
        """
        Instantiate a new factory object

        Parameters
        ----------
        common_conf : Entry
            The common configuration of the configuration file
        """
        super().__init__(common_conf)

    def create(self, options: Entry, parent: IRadiant = None) -> ATarget:
        """
        Create a new object of the type IRadiant

        Parameters
        ----------
        options : Entry
            The options to be used as parameters for the instantiation of the new object.
        parent : IRadiant
            The optional parent element of the object (necessary for subclasses of AOpticalComponent).
        Returns
        -------
        obj : ATarget
            The created target object
        """

        if parent is None:
            opts = self.collectOptions(options)
            opts["wl_bins"] = self._common_conf.wl_bins.val
            if hasattr(tg, options.type):
                class_ = getattr(tg, options.type)
                return class_(**opts)
            else:
                logger.error("Unknown target type: '" + options.type + "'")
        else:
            logger.error("No parent object allowed for target.")
