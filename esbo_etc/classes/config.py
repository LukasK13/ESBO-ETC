import xml.etree.ElementTree as eT
import numpy as np
import astropy.units as u
import os
import logging
from ..lib.helpers import error
from typing import Union
import re


class Entry(object):
    """
    A class used to represent a configuration entry.
    Taken from ExoSim (https://github.com/ExoSim/ExoSimPublic)
    """
    val: Union[str, bool, u.Quantity]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key, value)

    def __call__(self):
        return self.val if hasattr(self, "val") else None

    def parse(self, xml: eT.Element):
        """
        Parse attributes of a XML element

        Parameters
        ----------
        xml : xml.etree.ElementTree.Element
            XML element to parse the attributes from
        """
        # Copy the XML attributes to object attributes
        for attrib in xml.attrib.keys():
            setattr(self, attrib, xml.attrib[attrib])
        # parse units
        attribs = list(xml.attrib.keys())
        units = list(filter(re.compile(".*_unit$").match, attribs))
        for unit in units:
            var = unit.replace("_unit", "")
            if hasattr(self, var):
                try:
                    val = u.Quantity(list(map(float, getattr(self, var).split(','))), getattr(self, unit))
                    if len(val) == 1:
                        val = val[0]
                    setattr(self, var, val)
                except (ValueError, LookupError):
                    error("unable to convert units in entry '" + xml.tag + "': " + getattr(self, var) + " "  +
                          getattr(self, unit),  exit_=False)
        # Convert boolean values
        if hasattr(self, "val") and type(self.val) == str and self.val.lower() in ["false", "true"]:
            self.val = (self.val.lower() == "true")


class Configuration(object):
    """
    A Class to parse the XML configuration file.
    Adapted from ExoSim (https://github.com/ExoSim/ExoSimPublic)

    Attributes
    ----------
    conf : Entry
        Parsed configuration file as Entry-tree
    """
    conf = None

    def __init__(self, file="esbo-etc_defaults.xml"):
        """
        Parse a XML configuration file.

        Parameters
        ----------
        file : str
            configuration file to parse
        """

        # Check if configuration file exists
        if not os.path.exists(file):
            error("Configuration file '" + file + "' doesn't exist.")

        # Read configuration file
        logging.info("Reading configuration from file '" + file + "'.")
        self.conf = self.parser(eT.parse(file).getroot())

        self.calc_metaoptions()

    def parser(self, parent: eT.Element):
        """
        Parse a XML element tree to an Entry-tree

        Parameters
        ----------
        parent : xml.etree.ElementTree.Element
            The parent XML tree to be parsed

        Returns
        -------
        obj : Entry
            The parsed XML tree
        """

        # Initialize empty Entry object
        obj = Entry()

        for child in parent:
            # recursively parse children of child element
            parsed_child = self.parser(child)
            # parse attributes of child element
            parsed_child.parse(child)

            # Add or append the parsed child to the prepared Entry object
            if hasattr(obj, child.tag):
                if isinstance(getattr(obj, child.tag), list):
                    getattr(obj, child.tag).append(parsed_child)
                else:
                    setattr(obj, child.tag, [getattr(obj, child.tag), parsed_child])
            else:
                setattr(obj, child.tag, parsed_child)
        return obj

    def calc_metaoptions(self):
        """
        Calculate additional attributes e.g. the wavelength grid
        """
        self.calc_metaoption_wl_delta()

    def calc_metaoption_wl_delta(self):
        """
        Calculate the wavelength grid used for the calculations.
        """
        if hasattr(self.conf.common, "wl_delta"):
            wl_delta = self.conf.common.wl_delta()
        else:
            wl_delta = self.conf.common.wl_min() / self.conf.common.res()
        setattr(self.conf.common, 'wl_bins',
                Entry(val=np.append(np.arange(self.conf.common.wl_min().to(u.nm).value,
                                              self.conf.common.wl_max().to(u.nm).value, wl_delta.to(u.nm).value),
                                    self.conf.common.wl_max().to(u.nm).value) << u.nm))
