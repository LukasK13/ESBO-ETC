from ..ARadiantFactory import ARadiantFactory
from ..Entry import Entry
from ..IRadiant import IRadiant
from .AOpticalComponent import AOpticalComponent
from ...classes import optical_component as oc
from ...lib.logger import logger


class OpticalComponentFactory(ARadiantFactory):
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

    def create(self, options: Entry, parent: IRadiant = None) -> AOpticalComponent:
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
        obj : AOpticalComponent
            The created optical component
        """
        if parent is not None:
            opts = self.collectOptions(options)
            opts["parent"] = parent
            if hasattr(oc, options.type):
                class_ = getattr(oc, options.type)
                return class_(**opts)
            else:
                logger.error("Unknown optical component type: '" + options.type + "'")
        else:
            logger.error("Parent object is required for optical component.")

    def fromConfigBatch(self, conf: Entry, parent: IRadiant) -> AOpticalComponent:
        """
        Initialize a decorated target from a configuration.

        Parameters
        ----------
        conf : Entry
            The configuration defining the target and the decorators.
        parent : IRadiant
            The optional parent element of the object

        Returns
        -------
        parent : AOpticalComponent
            The decorated parent object.
        """
        if hasattr(conf.astroscene, "optical_component"):
            for entry in conf.astroscene.optical_component if type(conf.astroscene.optical_component) == list else\
                    [conf.astroscene.optical_component]:
                parent = self.create(entry, parent)
        if hasattr(conf, "common_optics") and hasattr(conf.common_optics, "optical_component"):
            for entry in conf.common_optics.optical_component if type(conf.common_optics.optical_component) == \
                                                                 list else [conf.common_optics.optical_component]:
                if isinstance(entry, Entry):
                    parent = self.create(entry, parent)
        if hasattr(conf, "instrument") and hasattr(conf.instrument, "optical_component"):
            for entry in conf.instrument.optical_component if type(conf.instrument.optical_component) == list else\
                    [conf.instrument.optical_component]:
                if isinstance(entry, Entry):
                    parent = self.create(entry, parent)
        return parent
