**************************
Building the Configuration
**************************
ESBO-ETC has to be configured by a XML-file. For basic information on XML and how to edit XML-files, have a look at
`this tutorial <https://www.w3schools.com/xml/default.asp>`_. During the initialization of the program,
the configuration is checked and possible errors reported with recommendations on how to fix the errors.
The given attributes are the minimal attributes. This means, that additional attributes like *comment* can be added
without breaking the configuration. This can be helpful to document tags as shown in the example below.

Basic Structure
===============
The basic structure of the configuration file is shown in the following tree. The configuration structure starts with a
root element which is divided into common paramaters, astroscene, common_optics and instrument. This basic structure has
to be used and must not be changed.

::

    root
    ├── common
    │   └── Common configuration parameters
    ├── astroscene
    │   └── Components outside of the telescope like target, atmosphere, ...
    ├── common_optics
    │   └── Common components for all sensors like mirrors, lenses, ...
    └── instrument
        └── The sensor and its configuration parameters

Common
======

.. include:: common.rst

.. _target:

Target
======

.. include:: target.rst

Optical components
==================

.. include:: optical_components.rst

Sensor
======

.. include:: sensor.rst

.. _reading_csv:

Reading CSV-Files
=================

The format of a file has to be either structured text (e.g. CSV) or astropy ECSV. The format of the file will be automatically detected during read.
In case of structured text, the units of the columns have to be defined in the column header within square brackets
(e.g. "wavelength [nm]"). The file must contain two columns with units: wavelength and the spectral quantity:

+-----------------+------------------------------+
| wavelength [nm] | emission [W/(nm\*m^2\*sr)]   |
+=================+==============================+
|             200 |                    1.345e-15 |
+-----------------+------------------------------+
|             201 |                   1.364e-15  |
+-----------------+------------------------------+
|             ... |                          ... |
+-----------------+------------------------------+

Example Configuration
=====================

.. code-block:: xml
    :linenos:

    <root>
        <common>
            <wl_min val="3" val_unit="um" comment="Shortest wavelength used for binning input spectra"/>
            <wl_max val="5" val_unit="um" comment="Shortest wavelength used for binning input spectra"/>
            <wl_delta val="1" val_unit="nm" comment="Wavelength increment used for binning input spectra"/>
            <d_aperture val="0.5" val_unit="m" comment="Diameter of the telescope aperture"/>
            <psf val="Airy" osf="10" osf_unit="" comment="PSF of the optical system. Can be Airy or a file"/>
            <jitter_sigma val="10" val_unit="arcsec" comment="Sigma of the telescope jitter"/>
            <output path="output" format="fits" comment="Output directory to store output files"/>
            <exposure_time val="0.1, 1.2" val_unit="s" comment="The exposure time"/>
        </common>

        <astroscene>
            <target type="BlackBodyTarget" temp="5778" temp_unit="K" mag="10" mag_unit="mag" band="B" size="point"
                    comment="Modeling the sun as mag 10 star. Size can be point or extended"/>
            <optical_component type="Atmosphere" transmittance="data/atmosphere/ESBO-DS_transmittance.txt"
                               emission="data/atmosphere/ESBO-DS_emission.txt" comment="Including the atmosphere"/>
        </astroscene>

        <common_optics>
            <optical_component type="Mirror" reflectance="data/mirror/Reflectance_UV-enhanced-aluminium-mirror.txt"
                               emissivity="0" temp="70" temp_unit="K" obstruction="0.0" comment="M1"/>
            <optical_component type="Mirror" reflectance="data/mirror/Reflectance_UV-enhanced-aluminium-mirror.txt"
                               emissivity="0" temp="70" temp_unit="K" comment="M2"/>
            <optical_component type="Mirror" reflectance="data/mirror/Reflectance_UV-enhanced-aluminium-mirror.txt"
                               emissivity="0" temp="70" temp_unit="K" comment="M3"/>
           <optical_component type="Filter" band="M"
                               emissivity="data/filter/emissivity.csv" temp="70" temp_unit="K" comment="Filter wheel"/>
        </common_optics>

        <instrument>
            <optical_component type="Mirror" reflectance="data/lens/Reflectance_UV-enhanced-aluminium-mirror.txt"
                               emissivity="0" temp="70" temp_unit="K" comment="M4"/>
            <sensor type="Imager">
                <f_number val="13" val_unit="" comment="The working f/#"/>
                <pixel_geometry val="1024, 1024" val_unit="pix" comment="Pixel geometry"/>
                <center_offset val="0.0, 0.0" val_unit="pix" comment="Shift of the array center"/>
                <pixel>
                    <quantum_efficiency val="data/ccd/QE.txt" comment="Quantum efficiency of the detector"/>
                    <pixel_size val="6.5" val_unit="um"/>
                    <dark_current val="0.6" val_unit="electron / (pix * s)" comment="Detector dark current"/>
                    <sigma_read_out val="1.4" val_unit="electron(1/2) / pix" comment="Detector readout noise in e-rms"/>
                    <well_capacity val="30000" val_unit="electron" comment="Well capacity of a pixel"/>
                </pixel>
                <photometric_aperture comment="The photometric aperture used to calculate signal and noise.">
                    <shape val="circle" comment="Shape of the photometric aperture. Can be square / circle"/>
                    <contained_energy val="80" comment="Contained energy for calculating the SNR"/>
                </photometric_aperture>
            </sensor>
        </instrument>
    </root>