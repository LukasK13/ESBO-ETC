import astropy.units as u
from .config import Entry
from .IRadiant import IRadiant
from ..classes import optical_component as oc
from ..classes import target as tg
from ..lib.helpers import error
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
                    if "mag" in attribs:
                        attribs["mag"] = float(attribs["mag"]) * u.mag
                    return tg.BlackBodyTarget(**attribs)
                elif options.type == "FileTarget":
                    # File Target
                    return getattr(tg, options.type)(**attribs)
                else:
                    error("Unknown target type: '" + options.type + "'")
            else:
                # New component is of type Optical Component
                attribs["parent"] = parent
                class_ = getattr(oc, options.type)
                if options.type in ["Atmosphere", "StrayLight", "Mirror", "Lens", "BeamSplitter"]:
                    return class_(**attribs)
                elif options.type == "Filter":
                    if hasattr(options, "band"):
                        return oc.Filter.fromBand(**attribs)
                    elif hasattr(options, "transmittance"):
                        return oc.Filter.fromFile(**attribs)
                    elif hasattr(options, "start") and hasattr(options, "end"):
                        return oc.Filter.fromRange(**attribs)
                    else:
                        error("Wrong parameters for filter.")
                else:
                    error("Unknown optical component type: '" + options.type + "'")
        else:
            error("Optical component needs to have a type specified.")
