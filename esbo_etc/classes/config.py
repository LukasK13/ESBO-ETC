import xml.etree.ElementTree as eT
import numpy as np
import astropy.units as u
import os
import logging
from ..lib.helpers import error
from typing import Union


class Entry(object):
    """
    A class used to represent a configuration entry.
    Taken from ExoSim (https://github.com/ExoSim/ExoSimPublic)
    """
    val: Union[str, bool, u.Quantity]

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

        # Convert to python datatype and apply the corresponding unit (if applicable)
        if hasattr(self, 'units'):
            try:
                self.val = u.Quantity(list(map(float, self.val.split(','))),
                                      self.units)
                if len(self.val) == 1:
                    self.val = self.val[0]
            except (ValueError, LookupError):
                error("unable to convert units in entry '" + xml.tag + "': " + self.val + " " + self.units, exit_=False)
        elif hasattr(self, "val") and self.val.lower() in ["false", "true"]:
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

    def __init__(self, filename="esbo-etc_defaults.xml"):
        """
        Parse a XML configuration file.

        Parameters
        ----------
        filename : str
            configuration file to parse
        """

        # Check if configuration file exists
        if not os.path.exists(filename):
            error("Configuration file '" + filename + "' doesn't exist.")

        # Read configuration file
        logging.info("Reading configuration from file '" + filename + "'.")
        self.conf = self.parser(eT.parse(filename).getroot())

        self.calc_metaoptions()

    def parser(self, parent):
        """
        Parse a XML element tree to an Entry-tree

        Parameters
        ----------
        parent : ElementTree
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
        setattr(self.conf.common, 'wl_bins', np.arange(self.conf.common.wl_min().to(u.micron).value,
                                                       self.conf.common.wl_max().to(u.micron).value,
                                                       wl_delta.to(u.micron).value) * u.micron)
