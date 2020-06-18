import astropy.units as u
from .Entry import Entry
from .IRadiant import IRadiant
from ..classes import optical_component as oc
from ..classes import target as tg
from ..lib.logger import logger
import copy
import re


class RadiantFactory:
    """
    A Factory creating objects of the type IRadiant
    """

    @u.quantity_input(wl_bins="length")
    def __init__(self, wl_bins: u.Quantity):
        """
        Instantiate a new factory object

        Parameters
        ----------
        wl_bins : Quantity
            Wavelengths used for binning
        """
        self.__wl_bins = wl_bins

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
        if hasattr(options, "type"):
            # Copy custom attributes of the Entry to a dictionary
            attribs = copy.copy(vars(options))
            # Remove unnecessary keys
            for attrib in list(filter(re.compile(".*_unit$").match, attribs)) + ["comment", "type"]:
                attribs.pop(attrib, None)
            if parent is None:
                # New component is of type target
                attribs["wl_bins"] = self.__wl_bins
                if options.type == "BlackBodyTarget":
                    # Black Body Target
                    if "mag" in attribs and type(attribs["mag"]) == str:
                        attribs["mag"] = float(attribs["mag"]) * u.mag
                    return tg.BlackBodyTarget(**attribs)
                elif options.type == "FileTarget":
                    # File Target
                    return getattr(tg, options.type)(**attribs)
                else:
                    logger.error("Unknown target type: '" + options.type + "'")
            else:
                # New component is of type Optical Component
                attribs["parent"] = parent
                if "obstruction" in attribs:
                    attribs["obstruction"] = float(attribs["obstruction"])
                class_ = getattr(oc, options.type)
                if options.type in ["Atmosphere", "StrayLight", "CosmicBackground", "Mirror", "Lens", "BeamSplitter"]:
                    return class_(**attribs)
                elif options.type == "Filter":
                    if hasattr(options, "band"):
                        return oc.Filter.fromBand(**attribs)
                    elif hasattr(options, "transmittance"):
                        return oc.Filter.fromFile(**attribs)
                    elif hasattr(options, "start") and hasattr(options, "end"):
                        return oc.Filter.fromRange(**attribs)
                    else:
                        logger.error("Wrong parameters for filter.")
                else:
                    logger.error("Unknown optical component type: '" + options.type + "'")
        else:
            logger.error("Optical component needs to have a type specified.")

    def fromConfigBatch(self, conf: Entry) -> IRadiant:
        """
        Initialize a decorated target from a configuration.

        Parameters
        ----------
        conf : Entry
            The configuration defining the target and the decorators.

        Returns
        -------
        parent : IRadiant
            The decorated target.
        """
        parent = self.create(conf.astroscene.target)
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
