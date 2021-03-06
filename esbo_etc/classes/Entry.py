from typing import Union
import re
import xml.etree.ElementTree as eT
import astropy.units as u
from ..lib.logger import logger
import difflib
import os
import numpy as np


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
            # enable imperial units
            u.imperial.enable()
            var = unit.replace("_unit", "")
            if hasattr(self, var):
                try:
                    val = u.Quantity(list(map(float, getattr(self, var).split(','))), getattr(self, unit))
                    if len(val) == 1:
                        val = val[0]
                    setattr(self, var, val)
                except (ValueError, LookupError):
                    logger.error("unable to convert units in entry '" + xml.tag + "': " + getattr(self, var) + " " +
                                 getattr(self, unit), exit_=False)
        # Convert boolean values
        if hasattr(self, "val") and type(self.val) == str and self.val.lower() in ["false", "true"]:
            self.val = (self.val.lower() == "true")

    def check_quantity(self, name: str, unit: u.Unit, use_default: bool = True) -> Union[None, str]:
        """
        Check a parameter as type quantity

        Parameters
        ----------
        name : str
            The name of the parameter to be checked.
        unit : Quantity
            The default quantity to be used for conversion and equality checking.
        use_default : bool
            Use the given unit as default unit and try to convert strings to Quantities with this unit.

        Returns
        -------
        mes : Union[None, str]
            The error message of the check. This will be None if the check was successful.
        """
        u.imperial.enable()
        if not hasattr(self, name):
            return "Parameter '" + name + "' not found."
        attr = getattr(self, name)
        if type(attr) != u.Quantity:
            if unit == u.dimensionless_unscaled or use_default:
                try:
                    self.__setattr__(name, float(attr) * unit)
                except ValueError:
                    try:
                        val = list(map(u.Quantity, attr.split(',')))
                        if len(val) == 1:
                            val = val[0]
                        else:
                            val = np.array(val[:(len(val)-1)] + [val[-1].value]) << val[-1].unit
                        self.__setattr__(name, val)
                        mes = self.check_quantity(name, unit, use_default)
                        if mes is not None:
                            return mes
                    except (ValueError, TypeError):
                        return "Expected parameter '" + name + "' with unit '" + unit.to_string() + \
                               "' but got no unit and cannot convert '" + attr + "' to a numeric value."
            else:
                return "Expected parameter '" + name + "' with unit '" + unit.to_string() + "' but got no unit."
        elif not attr.unit.is_equivalent(unit):
            if unit == u.K and attr.unit == u.Celsius:
                setattr(self, name, attr.to(unit, equivalencies=u.temperature()))
                setattr(self, name + '_unit', unit.to_string())
            elif unit.is_equivalent(u.m) and attr.unit.is_equivalent(u.Hz):
                setattr(self, name, attr.to(unit, equivalencies=u.spectral()))
                setattr(self, name + '_unit', unit.to_string())
            else:
                return "Expected parameter '" + name + "' with unit equivalent to '" + unit.to_string() + \
                   "' but got unit '" + attr.unit.to_string() + "'."
        return None

    def check_selection(self, name: str, choices: list) -> Union[None, str]:
        """
        Check a parameter against a list of possible choices. In case of a mismatch, a recommendation will be given.

        Parameters
        ----------
        name : str
            The name of the parameter to be checked.
        choices : list
            List of choices to be used for checking.

        Returns
        -------
        mes : Union[None, str]
            The error message of the check. This will be None if the check was successful.
        """
        if not hasattr(self, name):
            return "Parameter '" + name + "' not found."
        attr = getattr(self, name)
        if type(attr) != str:
            return "Expected parameter '" + name + "' to be of type string."
        if attr not in choices:
            match = difflib.get_close_matches(attr, choices, 1)
            if len(match) > 0:
                # noinspection PyTypeChecker
                return "Value '" + attr + "' not allowed for parameter '" + name + "'. Did you mean '" + \
                       match[0] + "'?"
            else:
                return "Value '" + attr + "' not allowed for parameter '" + name + "'."
        return None

    def check_file(self, name) -> Union[None, str]:
        """
        Check a parameter to be a valid path to a file.

        Parameters
        ----------
        name : str
            The name of the parameter to be checked.

        Returns
        -------
        mes : Union[None, str]
            The error message of the check. This will be None if the check was successful.
        """
        if not hasattr(self, name):
            return "Parameter '" + name + "' not found."
        if not os.path.isfile(getattr(self, name)):
            return "File '" + getattr(self, name) + "' does not exist."

    def check_path(self, name) -> Union[None, str]:
        """
        Check a parameter to be a valid path to a file.

        Parameters
        ----------
        name : str
            The name of the parameter to be checked.

        Returns
        -------
        mes : Union[None, str]
            The error message of the check. This will be None if the check was successful.
        """
        if not hasattr(self, name):
            return "Parameter '" + name + "' not found."
        if not os.path.isdir(getattr(self, name)):
            return "Path '" + getattr(self, name) + "' does not exist."

    def check_float(self, name) -> Union[None, str]:
        """
        Check a parameter to be a floating point value

        Parameters
        ----------
        name : str
            The name of the parameter to be checked.

        Returns
        -------
        mes : Union[None, str]
            The error message of the check. This will be None if the check was successful.
        """
        if not hasattr(self, name):
            return "Parameter '" + name + "' not found."
        attr = getattr(self, name)
        if type(attr) == float:
            return None
        elif type(attr) == u.Quantity:
            setattr(self, name, attr.value)
        elif type(attr) == str:
            try:
                setattr(self, name, float(attr))
            except ValueError:
                return "Cannot convert parameter '" + name + "' with value '" + attr + "' to a numeric value."
        elif type(attr) == int:
            setattr(self, name, float(attr))
        else:
            return "Expected parameter '" + name + "' to be numeric but got '" + type(attr) + "' instead."
