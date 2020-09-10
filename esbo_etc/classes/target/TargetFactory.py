import astropy.units as u
from ..ARadiantFactory import ARadiantFactory
from ..Entry import Entry
from ..IRadiant import IRadiant
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

    def create(self, options: Entry, parent: IRadiant = None) -> IRadiant:
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
        obj : IRadiant
            The created object
        """
        opts = self.collectOptions(options)
        if parent is None:
            # New component is of type target
            opts["wl_bins"] = self._common_conf.wl_bins.val
            if options.type == "BlackBodyTarget":
                # Black Body Target
                if "mag" in opts and type(opts["mag"]) == str:
                    opts["mag"] = float(opts["mag"]) * u.mag
                return tg.BlackBodyTarget(**opts)
            elif options.type == "FileTarget":
                # File Target
                return getattr(tg, options.type)(**opts)
            else:
                logger.error("Unknown target type: '" + options.type + "'")
        else:
            logger.error("No parent object allowed for target.")
