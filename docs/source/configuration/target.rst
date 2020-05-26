Currently ESBO-ETC supports the following two different types of targets. A configuration can contain only one target
which has to be contained in the container ``<astroscene>``. Each target consists of the basic tag
``<target>`` and possible other target-type specific attributes.

.. code-block:: xml

    <target type="BlackBodyTarget" size="point"/>

Attributes:
    * | **type:** str
      |   The type of the target. Currently, only :ref:`blackbodytarget` and :ref:`filetarget` are supported.
    * | **size:** str
      |   The size of the target which can be either ``point`` or ``extended``. In case of a point-source, a PSF will be used to determine the irradiance of each pixel. In case of a extended source, a uniform PSF is assumed, ignoring the parameters :ref:`psf`, :ref:`jitter_sigma`, and some instrument specific parameters.

.. _blackbodytarget:

BlackBodyTarget
---------------
Model a target as a black body of a given temperature and apparent magnitude.

.. code-block:: xml

    <target type="BlackBodyTarget" temp="5778" temp_unit="K" mag="10" mag_unit="mag" band="B" size="point"/>

Attributes:
    * | **temp:** str
      |   The temperature of the black body.
    * | **temp_unit:** str, *optional* = "K"
      |   The unit of the black body's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **mag:** str
      |   The apparent magnitude of the black body in magnitudes.
    * | **mag_unit:** str, *optional* = "mag"
      |   The unit of the black body's magnitude. This has to be ``mag``. The default is ``mag``.
    * | **band:** str
      |   The band used for fitting the black body's flux density to Vega's flux density. This has to be one of [``U``, ``B``, ``V``, ``R``, ``I``, ``J``, ``H``, ``K``, ``L``, ``M``, ``N``].

.. _filetarget:

FileTarget
----------
Create a target from a file containing the spectral flux densities of the target.

.. code-block:: xml

    <target type="FileTarget" val="PathToFile" size="point"/>

Attributes:
    * | **val:** str
      |   The path to the file containing the spectral flux densities. For details on the required file structure see also :ref:`reading_csv`.
