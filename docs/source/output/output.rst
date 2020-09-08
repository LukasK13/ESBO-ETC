.. _output:

******
Output
******

The results of the computation is printed as table to the command line after each run of ESBO-ETC.
An exemplary output is shown below for the calculation of the SNR::

    ┏━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
    ┃  #   ┃ Exposure Time ┃        SNR ┃
    ┡━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
    │  1   │  2.3000e+03 s │ 2.3838e-02 │
    └──────┴───────────────┴────────────┘

Depending on the computed quantity (SNR, exposure time, sensitivity), the layout may vary.

Besides the general output of the computation result, some more information is written to files in the output directory (see also :ref:`output_dir`).
The structure depends on the used detector type.

Imager Detector
===============
The signal, background, read noise and dark current in number of collected electrons are written as matrices to separate files.
These files can be either CSV-files or fits files depending on the settings in the configuration file.
The data written to these files is reduced to the relevant region containing the photometric aperture.
Nevertheless, the reduction strategy is written to the file header to allow a lossless restoration of the original pixel matrix.
An exemplary CSV file may look like this::

    # Signal in electrons
    # Range reduced to nonzero values.
    # The origin is in the top left corner, starting with 0.
    # Column index range: 507 - 516
    # Row index range: 507 - 516
    #
    1.804512872189814043e-01, 1.807562922319483345e-01, ...
    1.807562922319483345e-01, 1.810618127424260260e-01, ...
    ...                     , ...                     , ...


Heterodyne Instrument
=====================

In case of the heterodyne instrument, the spectral signal temperature, background temperature, RMS noise temperature and SNR are written to a CSV file in the output directory.
An exemplary output file is shown below.

+--------------------+------------------------+----------------------------+---------------------------+----------------------+
|  wavelength [nm]   | Signal Temperature [K] | Background Temperature [K] | RMS Noise Temperature [K] |       SNR [-]        |
+====================+========================+============================+===========================+======================+
| 207499.99999999997 | 0.002272235573155022   | 133.25311622347617         | 0.09403710578848441       | 0.024163180636656255 |
+--------------------+------------------------+----------------------------+---------------------------+----------------------+
| 207500.15818541934 | 0.002272264945847538   | 133.25312130031648         | 0.09403717788245403       | 0.02416347445781345  |
+--------------------+------------------------+----------------------------+---------------------------+----------------------+
|                ... |                    ... |                        ... |                       ... |                  ... |
+--------------------+------------------------+----------------------------+---------------------------+----------------------+
