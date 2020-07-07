In the following, the most important classes that are used by the software but not part of the radiation transportation pipeline are explained.

Spectral Quantity
-----------------

.. figure:: images/SpectralQty.pdf
   :alt: Class Diagram

   Class diagram of the Spectral Quantity.

All spectral quantities used for calculations, e.g. spectral flux densities, spectral reflectances, etc., are handled as ``SpectralQty``-objects.
They can be set up either by providing the two arrays wavelength bins and the corresponding spectral quantity as parameters to the constructor or by reading them from a file using the class method ``fromFile()``.
In the latter case, the file must be readable by astropy and the units of the columns may be contained in the column header in square brackets.
``SpectralQty``-objects natively support mathematical operations like addition (``__add__()``), substraction (``__sub__()``), multiplication (``__mul__()``) as well as true division (``__truediv__()``) and comparison (``__eq__()``).
Additionally, the two methods ``rebin()`` and ``integrate()`` allow to change the spectral grid or integrate the quantity on the grid.

.. _configuration:

Configuration
-------------

.. figure:: images/Configuration.pdf
   :alt: Class Diagram

   Class diagram of the Configuration.

The class ``Configuration`` contains all methods necessary to parse the XML-configuration file and convert it into a tree of :ref:`entry`-objects.
This conversion is triggered in the beginning of the program flow.
Additionally, the check of the parsed configuration is preformed by this class (``check_config()``, ``check_optical_components()``).
In detail, the static ``checkConfig()``-method of the corresponding class is called on each Entry-object to perform the checks.
Finally, this class also computes some meta options like the array containing the wavelength bins.

.. _entry:

Entry
-----

.. figure:: images/Entry.pdf
   :alt: Class Diagram

   Class diagram of the Entry.

The class ``Entry`` is used to represent the tags of the XML-configuration file and provide basic test mechanisms.
Each XML-tag is parsed by the :ref:`configuration` and converted into an ``Entry``-object.
Thereby each attribute of the XML-tag is converted into an attribute of the corresponding ``Entry``-object.
In case another attribute with the same name and the postfix *_unit* exists, both attributes are converted to an Astropy-Quantity object.
In case a parameter is called ``val``, this parameter is returned if the ``Entry``-object is called.

In order to allow checks on the attributes of an ``Entry``-object, the methods ``check_quantity()``, ``check_selection()``, ``check_file()``, ``check_path()`` and ``check_float()`` take the attribute name and possible a default value and return a string as check result.
If the check is passed, ``None`` will be returned.
