The tag ``common`` groups common configuration parameters and is therefore mandatory.

wl_min
------
The minimal wavelength to consider in the computations.

.. code-block:: xml

    <wl_min val="3" val_unit="um"/>

Attributes:
    * | **val:** float
      |   The value of the minimal wavelength.
    * | **val_unit:** str, *optional* = "m"
      |   The unit of the minimal wavelength. This has to be one of [``m``, ``cm``, ``mm``, ``um``, ``nm``, ``pm``, ``Hz``, ``kHZ``, ``MHz``, ``GHz``, ``THz``]. The default is ``m``.

wl_max
------
The maximal wavelength to consider in the computations.

.. code-block:: xml

    <wl_max val="5" val_unit="um"/>

Attributes:
    * | **val:** float
      |   The value of the maximal wavelength.
    * | **val_unit:** str, *optional* = "m"
      |   The unit of the maximal wavelength. This has to be one of [``m``, ``cm``, ``mm``, ``um``, ``nm``, ``pm``, ``Hz``, ``kHZ``, ``MHz``, ``GHz``, ``THz``]. The default is ``m``.

.. _wl_delta:

wl_delta
--------
*optional* -- The wavelength grid size to be used for the computations.

.. code-block:: xml

    <wl_delta val="5" val_unit="um"/>

Attributes:
    * | **val:** float
      |   The value of the wavelength grid size.
    * | **val_unit:** str, *optional* = "m"
      |   The unit of the wavelength grid size. This has to be one of [``m``, ``cm``, ``mm``, ``um``, ``nm``, ``pm``, ``Hz``, ``kHZ``, ``MHz``, ``GHz``, ``THz``]. The default is ``m``.

.. _res:

res
---
*optional* -- The spectral resolution to be used for the computations.
The central wavelength as defined by the average of the parameters `wl_min` and `wl_max` will be used to compute the wavelength grid size.


.. code-block:: xml

    <res val="1000" val_unit=""/>

Attributes:
    * | **val:** float
      |   The value of the spectral resolution.
    * | **val_unit:** str, *optional* = ""
      |   The unit of the spectral resolution. This has to be emtpy (dimensionless) or one of [``m/s``, ``km/s``].  The default is ``dimensionless``.

.. note::
   Either :ref:`wl_delta` or :ref:`res` must be given in the configuration.
   This parameters controls the accuracy of the integration of spectral quantities which is necessary for example for the imaging detector.
   Therefore, the user has to balance between computational effort and precision.

d_aperture
----------
The diameter of the telescope aperture.

.. code-block:: xml

    <d_aperture val="2.3" val_unit="m"/>

Attributes:
    * | **val:** float
      |   The value of the telescope aperture diameter.
    * | **val_unit:** str, *optional* = "m"
      |   The unit of the telescope aperture diameter. This has to be one of [``m``, ``cm``, ``mm``, ``um``, ``nm``, ``pm``]. The default is ``m``.

.. _psf:

psf
---
*optional* -- The PSF used for the computations.
This can be either read from a Zemax/FITS-file or approximated by a (obstructed) airy disk.
In case of a FITS-file, the PSF must be included as a 2D map.
The header keywords ``XPIXSZ`` and ``YPIXSZ`` can be used to define the grid size of the PSF in microns.
Otherwise, the keyword ``PSFSCALE`` can be used to define the FOV per PSF pixel in arcsec/pixel.
The keywords ``XPSFCTR`` and ``YPSFCTR`` can be used to define the center point of the PSF, if the PSF is not centered on the grid.

.. code-block:: xml

    <psf type="Airy" osf="10" osf_unit=""/>

.. code-block:: xml

    <psf type="FITS" val="data/psf.fits" osf="10" osf_unit=""/>

.. code-block:: xml

    <psf type="Zemax" val="data/psf.txt" osf="10" osf_unit=""/>

Attributes:
    * | **type:** str = "Airy"
      |   The PSF to be used for the computations. This can be either the path to a Zemax file or the keyword *Airy* to for an airy disk as PSF.
    * | **val:** str
      |   The path to the file to be read.
    * | **osf:** float = "10"
      |   The oversampling factor to be used to calculate the contained energy and the PSF with jitter.
    * | **osf_unit:** str, *optional* = ""
      |   The unit of the oversampling factor. This has to be emtpy (dimensionless). The default is ``dimensionless``.

.. _jitter_sigma:

jitter_sigma
------------
*optional* -- The pointing jitter sigma.

.. code-block:: xml

    <jitter_sigma val="2" val_unit="arcsec"/>

Attributes:
    * | **val:** float
      |   The value of the pointing jitter sigma.
    * | **val_unit:** str, *optional* = "arcsec"
      |   The unit of the pointing jitter sigma. This has to be one of [``arcsec``, ``arcmin``, ``degree``, ``radians``]. The default is ``arcsec``.

.. _output_dir:

output
------
*optional* -- Output settings for the results of the computation (see also :ref:`output`).

.. code-block:: xml

    <output path="output" format="fits"/>

Attributes:
    * | **path:** str = "."
      |   The path to the output directory.
    * | **format:** str = "CSV"
      |   The format to be used for outputting the signal and noise contributions. This has to be one of [``FITS``, ``CSV``].

.. _exposure_time:

exposure_time
-------------
*optional* -- The exposure time(s) for the computations.

.. code-block:: xml

    <exposure_time val="0.1" val_unit="s"/>

.. code-block:: xml

    <exposure_time val="0.1, 0.2, 0.3" val_unit="s"/>

.. code-block:: xml

    <exposure_time val="data/exposure_time.csv"/>

Attributes:
    * | **val:** (float, str)
      |   The exposure time(s) to be used for the computations. This can be either a single value, a comma separated list of values or the path to a CSV-file containing a single column of exposure time values. For details on the required file structure see also :ref:`reading_csv`.
    * | **val_unit:** str, *optional* = "s"
      |   The unit of the exposure time. This has to be one of [``ns``, ``us``, ``ms``, ``s``, ``min``, ``h``]. If the path to a file is provided, this parameter must be omitted. The default is ``s``.

.. _snr:

snr
---
*optional* -- The signal to noise ration (SNR) for the computations.

.. code-block:: xml

    <snr val="10" val_unit=""/>

.. code-block:: xml

    <snr val="10, 20, 30" val_unit=""/>

.. code-block:: xml

    <snr val="data/snr.csv"/>

Attributes:
    * | **val:** (float, str)
      |   The SNR(s) to be used for the computations. This can be either a single value, a comma separated list of values or the path to a CSV-file containing a single column of SNR values. For details on the required file structure see also :ref:`reading_csv`.
    * | **val_unit:** str, *optional* = ""
      |   The unit of the exposure time. This has to be emtpy (dimensionless). If the path to a file is provided, this parameter must be omitted. The default is ``dimensionless``.

.. note::
    The two parameters :ref:`exposure_time` and :ref:`snr` control the desired output of the computations.
    If only the exposure time is given, the corresponding signal to noise ration will be calculated and vice versa.
    If both the exposure time and the SNR is given as well as a black body target, the sensitivity will be calculated as limiting apparent magnitude.