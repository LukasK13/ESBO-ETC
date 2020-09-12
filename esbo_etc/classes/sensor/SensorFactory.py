from ..AFactory import AFactory
from ..IRadiant import IRadiant
from ..Entry import Entry
from .ASensor import ASensor
from ...classes import sensor as sensor
from ...lib.logger import logger


class SensorFactory(AFactory):
    """
    A Factory creating objects of the type ASensor
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

    def create(self, options: Entry, parent: IRadiant = None) -> ASensor:
        """
        Create a new sensor object

        Parameters
        ----------
        options : Entry
            The options to be used as parameters for the instantiation of the new object.
        parent : IRadiant
            The parent element of the object.
        Returns
        -------
        obj : ASensor
            The created sensor object
        """
        if parent is not None:
            opts = self.collectOptions(options)
            args = dict(parent=parent, **opts, common_conf=self._common_conf)
            if hasattr(sensor, options.type):
                class_ = getattr(sensor, options.type)
                return class_(**args)
            else:
                logger.error("Unknown sensor type: '" + options.type + "'")
        else:
            logger.error("Parent object is required for sensor.")
