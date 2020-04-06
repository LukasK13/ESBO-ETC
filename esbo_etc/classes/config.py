import xml.etree.ElementTree as eT
import numpy as np
import quantities as pq
import os
import logging
import sys


class Entry(object):
    """
    A class used to represent a configuration entry.
    """

    val = None
    attrib = None
    xml_entry = None

    def __call__(self):
        return self.val

    def parse(self, xml):
        """
        Parse a XML tree element

        :param xml: XML element tree to parse
        """
        self.attrib = xml.attrib
        for attr in self.attrib.keys():
            setattr(self, attr, self.attrib[attr])

        if hasattr(self, 'units'):
            try:
                self.val = pq.Quantity(list(map(float, self.val.split(','))),
                                       self.units).simplified
                if self.units == 'deg':
                    self.val = [x * pq.rad for x in self.val]  # workaround for qt unit conversion
                if len(self.val) == 1:
                    self.val = self.val[0]
            except (ValueError, LookupError):
                logging.error('unable to convert units in entry [tag, units, value]: ',
                              xml.tag, self.units, self.val)


class Configuration(object):
    """
    A Class to parse the XML configuration file.

    Attributes
    ----------
    conf : str
        Parsed XML tree
    """
    conf = None

    def __init__(self, filename="esbo-etc_defaults.xml", default_path=None):
        """
        Parse a XML configuration file.

        Parameters
        ----------
        filename : str
            configuration file to parse
        default_path : str
            default path to use for relative paths
        """
        if not os.path.exists(filename):
            logging.error("Configuration file '" + filename + "' doesn't exist.")
            sys.exit(1)

        logging.info("Reading configuration from file '" + filename + "'.")
        self.conf = self.parser(eT.parse(filename).getroot())

        if default_path:
            setattr(self.conf, "__path__", default_path)
        elif hasattr(self.conf.common, "ConfigPath"):
            setattr(self.conf, "__path__",
                    os.path.expanduser(self.conf.common.ConfigPath().replace('__path__', os.getcwd())))
        else:
            logging.error("Path to config files not defined")

        self.validate_options()
        self.calc_metaoptions()

    def parser(self, root):
        """
        Parse a XML configuration file.

        Parameters
        ----------
        root : ElementTree
            The XML tree to be parsed

        Returns
        -------
        obj : Entry
            The parsed XML tree
        """
        obj = Entry()

        for ch in root:
            retval = self.parser(ch)
            retval.parse(ch)

            if hasattr(obj, ch.tag):
                if isinstance(getattr(obj, ch.tag), list):
                    getattr(obj, ch.tag).append(retval)
                else:
                    setattr(obj, ch.tag, [getattr(obj, ch.tag), retval])
            else:
                setattr(obj, ch.tag, retval)
        return obj

    def validate_options(self):
        self.validate_is_list()
        self.validate_True_False_spelling()

    def validate_is_list(self):
        if not isinstance(self.conf.common_optics.optical_component, list):
            self.conf.common_optics.optical_component = [self.conf.common_optics.optical_component]
        if not isinstance(self.conf.instrument, list):
            self.conf.instrument = [self.conf.instrument]

    def validate_True_False_spelling(self):
        accepted_values = ['True', 'False']
        test_cases = [
            'noise/EnableJitter',
            'noise/EnableShotNoise',
            'noise/EnableReadoutNoise',
        ]
        for item in test_cases:
            if hasattr(self.conf, item.split('/')[0]):
                if not self.conf.__getattribute__(item.split('/')[0]).__dict__[item.split('/')[1]]() in accepted_values:
                    raise ValueError("Accepted values for [%s] are 'True' or 'False'" % item)

    def calc_metaoptions(self):
        self.calc_metaoption_wl_delta()

    def calc_metaoption_wl_delta(self):
        wl_delta = self.conf.common.wl_min() / self.conf.common.logbinres()
        setattr(self.conf.common, 'common_wl', (np.arange(self.conf.common.wl_min(),
                                                          self.conf.common.wl_max(),
                                                          wl_delta) * wl_delta.units).rescale(pq.um))


if __name__ == "__main__":
    conf = Configuration()
