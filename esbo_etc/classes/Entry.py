from typing import Union
import re
import xml.etree.ElementTree as eT
import astropy.units as u
from ..lib.helpers import error
import difflib
import os


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
                    error("unable to convert units in entry '" + xml.tag + "': " + getattr(self, var) + " " +
                          getattr(self, unit), exit_=False)
        # Convert boolean values
        if hasattr(self, "val") and type(self.val) == str and self.val.lower() in ["false", "true"]:
            self.val = (self.val.lower() == "true")

    def check_quantity(self, name: str, unit: u.Unit) -> Union[None, str]:
        if not hasattr(self, name):
            return "Parameter '" + name + "' not found."
        attr = getattr(self, name)
        if type(attr) != u.Quantity:
            if unit == u.dimensionless_unscaled:
                try:
                    self.__setattr__(name, float(attr) * u.dimensionless_unscaled)
                except ValueError:
                    return "Expected parameter '" + name + "' with unit '" + unit.to_string() + \
                           "' but got no unit and cannot convert '" + attr + "' to a numeric value."
            else:
                return "Expected parameter '" + name + "' with unit '" + unit.to_string() + "' but got no unit."
        if not attr.unit.is_equivalent(unit):
            return "Expected parameter '" + name + "' with unit equivalent to'" + unit.to_string() + \
                   "' but got unit '" + attr.unit.to_string() + "'."
        return None

    def check_selection(self, name, choices: list) -> Union[None, str]:
        if not hasattr(self, name):
            return "Parameter '" + name + "' not found."
        attr = getattr(self, name)
        if type(attr) != str:
            return "Expected parameter '" + name + "' to be of type string."
        if attr not in choices:
            # noinspection PyTypeChecker
            return "Value '" + attr + "' not allowed for parameter '" + name + "'. Did you mean '" +\
                   difflib.get_close_matches(attr, choices, 1)[0] + "'?"
        return None

    def check_file(self, name) -> Union[None, str]:
        if not hasattr(self, name):
            return "Parameter '" + name + "' not found."
        if not os.path.isfile(getattr(self, name)):
            return "File '" + getattr(self, name) + "' does not exist."

    def check_float(self, name) -> Union[None, str]:
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
