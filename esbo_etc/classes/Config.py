import xml.etree.ElementTree as eT
import numpy as np
import astropy.units as u
import os
import logging
from ..lib.helpers import error
from .Entry import Entry
from ..classes import target as tg
from ..classes import optical_component as oc
from ..classes import sensor as sensor
import difflib
import os.path


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

        self.check_config(self.conf)
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

    @staticmethod
    def check_config(conf: Entry):
        # Check common
        if not hasattr(conf, "common"):
            error("Configuration check: Missing required container 'common'.")
        if not hasattr(conf.common, "wl_min"):
            error("Configuration check: common: Missing required container 'wl_min'.")
        mes = conf.common.wl_min.check_quantity("val", u.m)
        mes is not None and error("Configuration check: common -> wl_min: " + mes)
        if not hasattr(conf.common, "wl_max"):
            error("Configuration check: common: Missing required container 'wl_max'.")
        mes = conf.common.wl_max.check_quantity("val", u.m)
        mes is not None and error("Configuration check: common -> wl_max: " + mes)
        if hasattr(conf.common, "wl_delta"):
            mes = conf.common.wl_delta.check_quantity("val", u.m)
            mes is not None and error("Configuration check: common -> wl_delta: " + mes)
        elif hasattr(conf.common, "res"):
            mes = conf.common.res.check_quantity("val", u.dimensionless_unscaled)
            mes is not None and error("Configuration check: common -> res: " + mes)
        else:
            error("Configuration check: common: Expected one of the containers 'wl_delta' or 'res' but got none.")
        if not hasattr(conf.common, "d_aperture"):
            error("Configuration check: common: Missing required container 'd_aperture'.")
        mes = conf.common.d_aperture.check_quantity("val", u.m)
        mes is not None and error("Configuration check: common -> d_aperture: " + mes)
        if not hasattr(conf.common, "psf"):
            setattr(conf.common, "psf", Entry(val="Airy"))
        else:
            if conf.common.psf().lower() != "airy":
                mes = conf.common.psf.check_file("val")
                mes is not None and error("Configuration check: common -> psf: " + mes)
        if hasattr(conf.common, "jitter_sigma"):
            mes = conf.common.jitter_sigma.check_quantity("val", u.arcsec)
            mes is not None and error("Configuration check: common -> jitter_sigma: " + mes)
        if not hasattr(conf.common, "output_path"):
            setattr(conf.common, "output_path", Entry(val="."))

        # Check astroscene
        if not hasattr(conf, "astroscene"):
            error("Configuration check: Missing required container 'astroscene'.")
        if not hasattr(conf.astroscene, "target"):
            error("Configuration check: astroscene: Missing required container 'target'.")
        if not hasattr(conf.astroscene.target, "type"):
            error("Configuration check: astroscene -> target: Missing required parameter 'type'.")
        if conf.astroscene.target.type not in dir(tg):
            # noinspection PyTypeChecker
            error("Configuration check: astroscene -> target: Target type '" + conf.astroscene.target.type +
                  "' does not exist. Did you mean '" + difflib.get_close_matches(conf.astroscene.target.type,
                                                                                 dir(tg), 1)[0] + "'?")
        mes = getattr(tg, conf.astroscene.target.type).check_config(conf.astroscene.target)
        mes is not None and error("Configuration check: astroscene -> target: " + mes)

        def check_optical_components(conf: Entry):
            if hasattr(conf, "optical_component"):
                for component in (conf.optical_component if type(conf.optical_component) == list else
                                  [conf.optical_component]):
                    if not hasattr(component, "type"):
                        return "optical_component: Missing required parameter 'type'."
                    if component.type not in dir(oc):
                        # noinspection PyTypeChecker
                        return "optical_component: optical component type '" + component.type + \
                               "' does not exist. Did you mean '" + \
                               difflib.get_close_matches(component.type, dir(tg), 1)[0] + "'?"
                    mes = getattr(oc, component.type).check_config(component)
                    if mes is not None:
                        print(component.type)
                        print(mes)
                        return "optical_component -> " + component.type + ": " + mes

        mes = check_optical_components(conf.astroscene)
        mes is not None and error("Configuration check: astroscene -> " + mes)

        # Check common_optics
        if hasattr(conf, "common_optics"):
            mes = check_optical_components(conf.common_optics)
            mes is not None and error("Configuration check: common_optics -> " + mes)

        # Check instrument
        if not hasattr(conf, "instrument"):
            error("Configuration check: Missing required container 'instrument'.")
        mes = check_optical_components(conf.instrument)
        mes is not None and error("Configuration check: instrument -> " + mes)
        if not hasattr(conf.instrument, "sensor"):
            error("Configuration check: instrument: Missing required container 'sensor'.")
        if not hasattr(conf.instrument.sensor, "type"):
            error("Configuration check: instrument -> target: Missing required parameter 'type'.")
        if conf.instrument.sensor.type not in dir(sensor):
            # noinspection PyTypeChecker
            error("Configuration check: sensor -> target: Sensor type '" + conf.instrument.sensor.type +
                  "' does not exist. Did you mean '" + difflib.get_close_matches(conf.instrument.sensor.type,
                                                                                 dir(sensor), 1)[0] + "'?")
        mes = getattr(sensor, conf.instrument.sensor.type).check_config(conf.instrument.sensor)
        mes is not None and error("Configuration check: instrument -> sensor -> " + mes)
