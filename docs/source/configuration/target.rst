Currently ESBO-ETC supports the following two different types of targets. A configuration can contain only one target
which has to be contained in the container ``<astroscene>``. Each target consists of the basic tag
``<target>`` and possible other target-type specific attributes.
Each target can be either modelled as a point source or as an infinitely extended target. In case of a point-source,
a PSF will be used to determine the irradiance of each pixel. In case of a extended source, a uniform PSF is assumed,
ignoring the parameters :ref:`psf`, :ref:`jitter_sigma`, and some instrument specific parameters.

.. code-block:: xml

    <target type="BlackBodyTarget"/>

Attributes:
    * | **type:** str
      |   The type of the target. Currently, only :ref:`blackbodytarget` and :ref:`filetarget` are supported.

.. _blackbodytarget:

BlackBodyTarget
---------------
Model a target as a black body of a given temperature and apparent magnitude.

.. code-block:: xml

    <target type="BlackBodyTarget" temp="5778" temp_unit="K" mag="10" mag_unit="mag" band="B" size="point" law="Planck"/>

Attributes:
    * | **temp:** float
      |   The temperature of the black body.
    * | **temp_unit:** str, *optional* = "K"
      |   The unit of the black body's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **mag:** float, *optional* = None
      |   The apparent magnitude of the black body in magnitudes. In case of None or magnitude per solid angle, an extended target is assumed.
    * | **mag_unit:** str, *optional* = "mag"
      |   The unit of the black body's magnitude. This has to be [``mag``, ``mag / arcsec**2``, ``mag / sr``]. The default is ``mag``.
    * | **band:** str, *optional*
      |   The band used for fitting the black body's flux density to Vega's flux density. This has to be one of [``U``, ``B``, ``V``, ``R``, ``I``, ``J``, ``H``, ``K``, ``L``, ``M``, ``N``].
    * | **law:** str, *optional*
      |   The law used for the black body emission. This can be either ``Planck`` for using Planck's law or ``RJ`` for using the Rayleigh-Jeans approximation of Planck's law.

.. _filetarget:

FileTarget
----------
Create a target from a file containing the spectral flux densities or, in case of an extended source, the spectral radiance of the target.

.. code-block:: xml

    <target type="FileTarget" val="PathToFile" size="point"/>

Attributes:
    * | **val:** str
      |   The path to the file containing the spectral flux densities / radiances. For details on the required file structure see also :ref:`reading_csv`.
