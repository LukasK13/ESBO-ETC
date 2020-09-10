from ..RadiantFactory import RadiantFactory
from ..Entry import Entry
from ..IRadiant import IRadiant
from ...classes import optical_component as oc
from ...lib.logger import logger


class OpticalComponentFactory(RadiantFactory):
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
        if parent is not None:
            # New component is of type Optical Component
            opts["parent"] = parent
            class_ = getattr(oc, options.type)
            if options.type in ["Atmosphere", "StrayLight", "CosmicBackground", "Mirror", "Lens", "BeamSplitter"]:
                return class_(**opts)
            elif options.type == "Filter":
                if hasattr(options, "band"):
                    return oc.Filter.fromBand(**opts)
                elif hasattr(options, "transmittance"):
                    return oc.Filter.fromFile(**opts)
                elif hasattr(options, "start") and hasattr(options, "end"):
                    return oc.Filter.fromRange(**opts)
                else:
                    logger.error("Wrong parameters for filter.")
            else:
                logger.error("Unknown optical component type: '" + options.type + "'")
        else:
            logger.error("No parent given for optical component.")

    def fromConfigBatch(self, conf: Entry, parent: IRadiant) -> IRadiant:
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
        parent : IRadiant
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
