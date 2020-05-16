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
from typing import Union


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
        self.conf = self.__parser(eT.parse(file).getroot())

        self.__check_config()
        self.__calc_metaoptions()

    def __parser(self, parent: eT.Element):
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
            parsed_child = self.__parser(child)
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

    def __calc_metaoptions(self):
        """
        Calculate additional attributes e.g. the wavelength grid
        """
        self.__calc_metaoption_wl_delta()

    def __calc_metaoption_wl_delta(self):
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

    def __check_config(self):
        """
        Check and fix the parsed configuration file.
        """
        # Check common
        if not hasattr(self.conf, "common"):
            error("Configuration check: Missing required container 'common'.")
        if not hasattr(self.conf.common, "wl_min"):
            error("Configuration check: common: Missing required container 'wl_min'.")
        mes = self.conf.common.wl_min.check_quantity("val", u.m)
        mes is not None and error("Configuration check: common -> wl_min: " + mes)
        if not hasattr(self.conf.common, "wl_max"):
            error("Configuration check: common: Missing required container 'wl_max'.")
        mes = self.conf.common.wl_max.check_quantity("val", u.m)
        mes is not None and error("Configuration check: common -> wl_max: " + mes)
        if hasattr(self.conf.common, "wl_delta"):
            mes = self.conf.common.wl_delta.check_quantity("val", u.m)
            mes is not None and error("Configuration check: common -> wl_delta: " + mes)
        elif hasattr(self.conf.common, "res"):
            mes = self.conf.common.res.check_quantity("val", u.dimensionless_unscaled)
            mes is not None and error("Configuration check: common -> res: " + mes)
        else:
            error("Configuration check: common: Expected one of the containers 'wl_delta' or 'res' but got none.")
        if not hasattr(self.conf.common, "d_aperture"):
            error("Configuration check: common: Missing required container 'd_aperture'.")
        mes = self.conf.common.d_aperture.check_quantity("val", u.m)
        mes is not None and error("Configuration check: common -> d_aperture: " + mes)
        if not hasattr(self.conf.common, "psf"):
            setattr(self.conf.common, "psf", Entry(val="Airy"))
        else:
            if self.conf.common.psf().lower() != "airy":
                mes = self.conf.common.psf.check_file("val")
                mes is not None and error("Configuration check: common -> psf: " + mes)
            mes = self.conf.common.psf.check_float("osf")
            mes is not None and error("Configuration check: common -> psf: " + mes)
        if hasattr(self.conf.common, "jitter_sigma"):
            mes = self.conf.common.jitter_sigma.check_quantity("val", u.arcsec)
            mes is not None and error("Configuration check: common -> jitter_sigma: " + mes)
        if not hasattr(self.conf.common, "output_path"):
            setattr(self.conf.common, "output_path", Entry(val="."))
        if hasattr(self.conf.common, "exposure_time"):
            mes = self.conf.common.exposure_time.check_quantity("val", u.s)
            mes is not None and error("Configuration check: common -> exposure_time: " + mes)
        if hasattr(self.conf.common, "snr"):
            mes = self.conf.common.snr.check_quantity("val", u.dimensionless_unscaled)
            mes is not None and error("Configuration check: common -> snr: " + mes)
        if not (hasattr(self.conf.common, "exposure_time") or hasattr(self.conf.common, "snr")):
            error("Configuration check: common: Expected one of the containers 'exposure_time' or 'snr' but got none.")

        # Check astroscene
        if not hasattr(self.conf, "astroscene"):
            error("Configuration check: Missing required container 'astroscene'.")
        if not hasattr(self.conf.astroscene, "target"):
            error("Configuration check: astroscene: Missing required container 'target'.")
        if not hasattr(self.conf.astroscene.target, "type"):
            error("Configuration check: astroscene -> target: Missing required parameter 'type'.")
        if self.conf.astroscene.target.type not in dir(tg):
            # noinspection PyTypeChecker
            error("Configuration check: astroscene -> target: Target type '" + self.conf.astroscene.target.type +
                  "' does not exist. Did you mean '" + difflib.get_close_matches(self.conf.astroscene.target.type,
                                                                                 dir(tg), 1)[0] + "'?")
        mes = getattr(tg, self.conf.astroscene.target.type).check_config(self.conf.astroscene.target)
        mes is not None and error("Configuration check: astroscene -> target: " + mes)
        if hasattr(self.conf.common, "exposure_time") and hasattr(self.conf.common, "snr"):
            if self.conf.astroscene.target.type.lower() != "blackbodytarget":
                error("Configuration check: astroscene -> target: Sensitivity calculation only possible for " +
                      "a target of the type 'BlackBodyTarget'.")
        mes = self.__check_optical_components(self.conf.astroscene)
        mes is not None and error("Configuration check: astroscene -> " + mes)

        # Check common_optics
        if hasattr(self.conf, "common_optics"):
            mes = self.__check_optical_components(self.conf.common_optics)
            mes is not None and error("Configuration check: common_optics -> " + mes)

        # Check instrument
        if not hasattr(self.conf, "instrument"):
            error("Configuration check: Missing required container 'instrument'.")
        mes = self.__check_optical_components(self.conf.instrument)
        mes is not None and error("Configuration check: instrument -> " + mes)
        if not hasattr(self.conf.instrument, "sensor"):
            error("Configuration check: instrument: Missing required container 'sensor'.")
        if not hasattr(self.conf.instrument.sensor, "type"):
            error("Configuration check: instrument -> sensor: Missing required parameter 'type'.")
        if self.conf.instrument.sensor.type not in dir(sensor):
            # noinspection PyTypeChecker
            error("Configuration check: instrument -> sensor: Sensor type '" + self.conf.instrument.sensor.type +
                  "' does not exist. Did you mean '" + difflib.get_close_matches(self.conf.instrument.sensor.type,
                                                                                 dir(sensor), 1)[0] + "'?")
        mes = getattr(sensor, self.conf.instrument.sensor.type).check_config(self.conf.instrument.sensor, self.conf)
        mes is not None and error("Configuration check: instrument -> sensor -> " + mes)

    @staticmethod
    def __check_optical_components(conf: Union[Entry, list]):
        """
        Check list of optical components in the parsed configuration.

        Parameters
        ----------
        conf : Union[Entry, list]
            The configuration entry or the list of configuration entries of the optical components to be checked.

        Returns
        -------
        mes : Union[None, str]
            The error message of the check. This will be None if the check was successful.
        """
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