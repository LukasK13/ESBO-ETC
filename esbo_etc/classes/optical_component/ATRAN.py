from .Atmosphere import Atmosphere
from ..IRadiant import IRadiant
from ..SpectralQty import SpectralQty
from ..Entry import Entry
from ...lib.logger import logger
from ...lib.cache import cache
import astropy.units as u
from astropy.io import ascii
from astropy.modeling.models import BlackBody
from astropy.table import QTable
from typing import Union
import re
import requests as req
import numpy as np


class ATRAN(Atmosphere):
    """
    A class to model the atmosphere including the atmosphere's spectral transmittance and emission.
    """

    # defining the ATRAN-endpoint
    ATRAN = "https://atran.arc.nasa.gov"

    @u.quantity_input(altitude="length", latitude="angle", water_vapor="length", zenith_angle="angle", wl_min="length",
                      wl_max="length", temp=[u.Kelvin, u.Celsius])
    def __init__(self, parent: IRadiant, transmittance: str = None, altitude: u.Quantity = None,
                 wl_min: u.Quantity = None, wl_max: u.Quantity = None, latitude: u.Quantity = 39 * u.degree,
                 water_vapor: u.Quantity = 0 * u.um, n_layers: int = 2, zenith_angle: u.Quantity = 0 * u.degree,
                 resolution: int = 0, temp: u.Quantity = 0 * u.K):
        """
        Initialize a new atmosphere model from ATRAN output

        Parameters
        ----------
        parent : IRadiant
            The parent element of the atmosphere from which the electromagnetic radiation is received.
        transmittance : str
            Path to the ATRAN output file containing the spectral transmittance-coefficients of the atmosphere.
        altitude : u.Quantity
            The observatory altitude in feet.
        wl_min : u.Quantity
            The minimal wavelength to consider in micrometer.
        wl_max : u.Quantity
            The maximal wavelength to consider in micrometer.
        latitude : u.Quantity
            The observatory's latitude in degrees.
        water_vapor : u.Quantity
            The water vapor overburden in microns (0 if unknown).
        n_layers : int
            The number of considered atmopsheric layers.
        zenith_angle : u.Quantity
            The zenith angle of the observation in degrees (0 is towards the zenith).
        resolution : int
            The resolution for smoothing (0 for no smoothing).
        temp : u.Quantity
            The atmospheric temperature for the atmosphere's black body radiation.
        """

        if transmittance is not None:
            data = self.__parse_ATRAN(transmittance)
        else:
            logger.info("Requesting ATRAN transmission profile.")
            data = self.__call_ATRAN(altitude, wl_min, wl_max, latitude, water_vapor, n_layers, zenith_angle,
                                     resolution)

        transmittance = SpectralQty(data["col2"].quantity, data["col3"].quantity)
        super().__init__(parent, transmittance, temp=temp)

    @u.quantity_input(altitude="length", latitude="angle", water_vapor="length", zenith_angle="angle", wl_min="length",
                      wl_max="length")
    @cache
    def __call_ATRAN(self, altitude: u.Quantity, wl_min: u.Quantity, wl_max: u.Quantity,
                     latitude: u.Quantity = 39 * u.degree, water_vapor: u.Quantity = 0 * u.um, n_layers: int = 2,
                     zenith_angle: u.Quantity = 0 * u.degree, resolution: int = 0):
        """
        Call the online version of ATRAN provided by SOFIA

        Parameters
        ----------
        altitude : u.Quantity
            The observatory altitude in feet.
        wl_min : u.Quantity
            The minimal wavelength to consider in micrometer.
        wl_max : u.Quantity
            The maximal wavelength to consider in micrometer.
        latitude : u.Quantity
            The observatory's latitude in degrees.
        water_vapor : u.Quantity
            The water vapor overburden in microns (0 if unknown).
        n_layers : int
            The number of considered atmopsheric layers.
        zenith_angle : u.Quantity
            The zenith angle of the observation in degrees (0 is towards the zenith).
        resolution : int
            The resolution for smoothing (0 for no smoothing).

        Returns
        -------
        data : QTable
            The ATRAN computation results
        """
        # Select closest latitude from ATRAN options
        latitude_ = min(np.array([9, 30, 39, 43, 59]) * u.degree, key=lambda x: abs(x - latitude.to(u.degree)))
        # Select closest number of layers from ATRAN options
        n_layers_ = min([2, 3, 4, 5], key=lambda x: abs(x - n_layers))
        # Assemble the data payload
        data = {'Altitude': altitude.to(u.imperial.ft).value,
                'Obslat': '%d deg' % latitude_.value,
                'WVapor': water_vapor.to(u.um).value,
                'NLayers': n_layers_,
                'ZenithAngle': zenith_angle.to(u.degree).value,
                'WaveMin': wl_min.to(u.um).value,
                'WaveMax': wl_max.to(u.um).value,
                'Resolution': resolution}
        # Send data to ATRAN via POST request
        res = req.post(url=self.ATRAN + "/cgi-bin/atran/atran.cgi", data=data)
        # Check if request was successful
        if not res.ok:
            logger.error("Error: Request returned status code " + str(res.status_code))

        # Extract the content of the reply
        content = res.text
        # Check if any ATRAN error occured
        match = re.search('<CENTER><H2>ERROR!!</H2></CENTER><CENTER>(.*)</CENTER>', content)
        if match:
            logger.error("Error: " + match.group(1))

        # Extract link to ATRAN result file
        match = re.search('href="(/atran_calc/atran.(?:plt|smo).\\d*.dat)"', content)
        # Check if link was found
        if not match:
            logger.error("Error: Link to data file not found.")

        # Request the ATRAN result via GET request
        res = req.get(self.ATRAN + match.group(1))
        # Check if request was successful
        if not res.ok:
            logger.error("Error: Request returned status code " + str(res.status_code))

        # Extract the content of the reply
        data = res.text
        # Check if result is empty
        if data == "":
            logger.error("Error: Request returned empty response.")
        return self.__parse_ATRAN(data)

    @staticmethod
    def __parse_ATRAN(table: str):
        """
        Parse an ATRAN result file and convert it to an astropy table

        Parameters
        ----------
        table : str
            Path to the file or content of the file.

        Returns
        -------
        data : astropy.Table
            The parsed table object.
        """
        # Read the file
        data = ascii.read(table, format=None)
        # Set units
        data["col2"].unit = u.um
        data["col3"].unit = u.dimensionless_unscaled
        return data

    @staticmethod
    @u.quantity_input(temp=[u.Kelvin, u.Celsius])
    def __gb_factory(temp: u.Quantity, em: Union[int, float] = 1):
        """
        Factory for a grey body lambda-function.

        Parameters
        ----------
        temp : Quantity in Kelvin / Celsius
            The temperature fo the grey body.
        em : Union[int, float]
            Emissivity of the the grey body

        Returns
        -------
        bb : Callable
            The lambda function for the grey body.
        """
        bb = BlackBody(temperature=temp, scale=em * u.W / (u.m ** 2 * u.nm * u.sr))
        return lambda wl: bb(wl)

    def __repr__(self):
        return "ATRAN Object"

    @staticmethod
    def check_config(conf: Entry) -> Union[None, str]:
        """
        Check the configuration for this class

        Parameters
        ----------
        conf : Entry
            The configuration entry to be checked.

        Returns
        -------
        mes : Union[None, str]
            The error message of the check. This will be None if the check was successful.
        """
        if hasattr(conf, "transmittance"):
            mes = conf.check_file("transmittance")
            if mes is not None:
                return mes
        else:
            mes = conf.check_quantity("altitude", u.imperial.ft)
            if mes is not None:
                return mes
            mes = conf.check_quantity("wl_min", u.um)
            if mes is not None:
                return mes
            mes = conf.check_quantity("wl_max", u.um)
            if mes is not None:
                return mes
            if hasattr(conf, "latitude"):
                mes = conf.check_quantity("latitude", u.degree)
                if mes is not None:
                    return mes
            if hasattr(conf, "water_vapor"):
                mes = conf.check_quantity("water_vapor", u.um)
                if mes is not None:
                    return mes
            if hasattr(conf, "n_layers"):
                mes = conf.check_float("n_layers")
                if mes is not None:
                    return mes
            if hasattr(conf, "zenith_angle"):
                mes = conf.check_quantity("zenith_angle", u.degree)
                if mes is not None:
                    return mes
            if hasattr(conf, "resolution"):
                mes = conf.check_float("resolution")
                if mes is not None:
                    return mes
        if hasattr(conf, "temp"):
            mes = conf.check_quantity("temp", u.K)
            if mes is not None:
                return mes
