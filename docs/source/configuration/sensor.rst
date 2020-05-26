Currently, ESBO-ETC only supports detectors of the type :ref:`imager`.

.. code-block:: xml

    <sensor type="">

Attributes:
    * | **type:** str
      |   The type of the detector. Has to be one of [``Imager``].

.. _imager:

Imager
------
The Imager sensor type allows to model a generic imaging sensor which uses a pixel based array to create only spatially resolved images. The imager-component contains several parameters which are explained in the following.

.. code-block:: xml
    :linenos:

    <sensor type="Imager">
        <f_number val="13" val_unit=""/>
        <pixel_geometry val="1024, 1024" val_unit="pix"/>
        <center_offset val="0.0, 0.0" val_unit="pix"/>
        <pixel>
            <quantum_efficiency val="data/ccd/QE.txt"/>
            <pixel_size val="6.5" val_unit="um"/>
            <dark_current val="0.6" val_unit="electron / (pix * s)"/>
            <sigma_read_out val="1.4" val_unit="electron(1/2) / pix"/>
            <well_capacity val="30000" val_unit="electron"/>
        </pixel>
        <photometric_aperture/>
            <shape val="circle"/>
            <contained_energy val="80"/>
            <contained_pixels val="100" val_unit="pix"/>
        </photometric_aperture>
    </sensor>

f_number
^^^^^^^^
The working focal number of the instrument.

.. code-block:: xml

    <f_number val="13" val_unit=""/>

Attributes:
    * | **val:** str
      |   The value of the working focal number of the instrument.
    * | **val_unit:** str, *optional* = ""
      |   The unit of the working focal number of the instrument. This has to be emtpy (dimensionless).

.. _pixel_geometry:

pixel_geometry
^^^^^^^^^^^^^^
The geometry of the sensor's pixel array.

.. code-block:: xml

    <pixel_geometry val="1024, 1024" val_unit="pix"/>

Attributes:
    * | **val:** str
      |   The geometry of the sensor's pixel array as a comma separated list of the number of pixels per dimension (X, Y).
    * | **val_unit:** str, *optional* = "pix"
      |   The unit of the geometry of the sensor's pixel array. This has to be ``pix``.

.. _center_offset:

center_offset
^^^^^^^^^^^^^
The PSF's center offset from the arithmetical center of the detector array which is defined as half of the number of pixels per dimension as defined in :ref:`pixel_geometry`

.. code-block:: xml

    <center_offset val="0.0, 0.0" val_unit="pix"/>

Attributes:
    * | **val:** str
      |   PSF's center offset as a comma separated list of the offset in pixels per dimension (X, Y).
    * | **val_unit:** str, *optional* = "pix"
      |   The unit of the PSF's center offset. This has to be ``pix``.

pixel
^^^^^
The pixel-container contains parameters which apply to all pixels of the sensor array.

.. code-block:: xml
    :linenos:

    <pixel>
        <quantum_efficiency val="data/ccd/QE.txt"/>
        <pixel_size val="6.5" val_unit="um"/>
        <dark_current val="0.6" val_unit="electron / (pix * s)"/>
        <sigma_read_out val="1.4" val_unit="electron(1/2) / pix"/>
        <well_capacity val="30000" val_unit="electron"/>
    </pixel>

quantum_efficiency
""""""""""""""""""
The quantum efficiency of a detector pixel.

.. code-block:: xml

    <quantum_efficiency val="data/ccd/QE.txt"/>

Attributes:
    * | **val:** str
      |   The path to the file containing the quantum efficiency values. For details on the required file structure see also :ref:`reading_csv`.

pixel_size
""""""""""
The spatial size of each detector pixel. Each pixel is assumed to be of quadratic.

.. code-block:: xml

    <pixel_size val="6.5" val_unit="um"/>

Attributes:
    * | **val:** str
      |   The value of the edge length of a detector pixel.
    * | **val_unit:** str, *optional* = "m"
      |   The unit of the edge length of a detector pixel. This has to be one of [``m``, ``cm``, ``mm``, ``um``, ``nm``, ``pm``]. The default is ``m``.

dark_current
""""""""""""
The dark current of a detector pixel.

.. code-block:: xml

    <dark_current val="0.6" val_unit="electron / (pix * s)"/>

Attributes:
    * | **val:** str
      |   The value of the dark current of a detector pixel.
    * | **val_unit:** str, *optional* = "electron / (pix * s)"
      |   The unit of the dark current of a detector pixel. This has to be ``electron / (pix * s)``.

sigma_read_out
""""""""""""""
The read out noise of a detector pixel.

.. code-block:: xml

    <sigma_read_out val="1.4" val_unit="electron(1/2) / pix"/>

Attributes:
    * | **val:** str
      |   The value of the read out noise of a detector pixel.
    * | **val_unit:** str, *optional* = "electron(1/2) / pix"
      |   The unit of the read out noise of a detector pixel. This has to be ``electron(1/2) / pix``.

well_capacity
"""""""""""""
The well capacity of a detector pixel.

.. code-block:: xml

    <well_capacity val="30000" val_unit="electron"/>

Attributes:
    * | **val:** str
      |   The value of the well capacity of a detector pixel.
    * | **val_unit:** str, *optional* = "electron"
      |   The unit of the well capacity of a detector pixel. This has to be ``electron``.

photometric_aperture
^^^^^^^^^^^^^^^^^^^^
*optional*

The photometric_aperture-container contains parameters for the photometric aperture of the observation. This container is only required, if the :ref:`target` has the shape ``point``.

.. code-block:: xml
    :linenos:

    <photometric_aperture/>
        <shape val="circle"/>
        <contained_energy val="80"/>
        <contained_pixels val="100" val_unit="pix"/>
    </photometric_aperture>

shape
"""""
The shape of the photometric aperture which will be placed around the center of the PSF which is defined by :ref:`center_offset`. After the radius of the photometric aperture was calculated using a disk for the given :ref:`contained_energy`, this radius will be used as radius or edge length of the photometric aperture shape.

.. code-block:: xml

    <shape val="circle"/>

Attributes:
    * | **val:** str
      |   The shape of the photometric aperture. This has to be one of [``circle``, ``square``].

.. _contained_energy:

contained_energy
""""""""""""""""
*optional*

The energy to be contained within the photometric aperture. This value will used for the computation of the radius of the photometric aperture.

.. code-block:: xml

    <contained_energy val="80"/>

Attributes:
    * | **val:** str
      |   The energy to be contained within the photometric aperture. This can be either the percentage of contained energy or one of [``Peak``, ``FWHM``, ``Min``].

contained_pixels
""""""""""""""""
*optional*

The number of pixels to be contained within the photometric aperture. If this parameter is given, the :ref:`contained_energy` parameter will be ignored. The square root of this value will be used as the radius of the photometric aperture.

.. code-block:: xml

    <contained_pixels val="100" val_unit="pix"/>

Attributes:
    * | **val:** str
      |   The number of pixels to be contained within the photometric aperture.
    * | **val_unit:** str, *optional* = "pix"
      |   The unit of the number of pixels to be contained within the photometric aperture. This has to be ``pix``.