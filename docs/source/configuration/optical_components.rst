Each optical component consists of the basic tag ``<optical_component>`` and the attribute ``type`` and possible other
component-specific attributes.

.. code-block:: xml

    <optical_component type="Mirror"/>

Attributes:
    * | **type:** str
      | The type of the optical component. This can be one of the following types.

Atmosphere
----------
This component models the behaviour of an atmosphere which has a spectral transmittance and a spectral emission.
It is possible to read the transmittance of the atmosphere from a CSV file, from an output file of ATRAN or call the webversion of ATRAN to compute the transmission profile.
The atmospheric emission can bei either read from a CSV file or computed as a grey body radiator of a given temperature and emissivity = 1 - transmission.

.. code-block:: xml

    <optical_component type="Atmosphere" transmittance="PathToTransmittanceFile" emission="PathToEmissionFile"/>

.. code-block:: xml

    <optical_component type="Atmosphere" transmittance="PathToATRANFile" temp="200" temp_unit="K"/>

.. code-block:: xml

    <optical_component type="Atmosphere" altitude="41000" altitude_unit="ft" wl_min="16" wl_min_unit="um"
                       wl_max="24" wl_max_unit="um" latitude="39" latitude_unit="degree" water_vapor="0"
                       water_vapor_unit="um" n_layers="2" zenith_angle="0" zenith_angle_unit="degree" resolution="0"
                       temp="240" temp_unit="K"/>

Attributes:
    * | **transmittance:** str
      | The path to the file containing the spectral transmittance coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **atran:** str
      | Path to a file containing the output of ATRAN.
    * | **altitude:** float
      | The observatory altitude for the call to ATRAN.
    * | **altitude_unit:** str, *optional* = "ft"
      | The unit of the observatory altitude for the call to ATRAN.
    * | **wl_min:** float
      | The minimum wavelength for the call to ATRAN.
    * | **wl_min_unit:** str, *optional* = "um"
      | The unit of the minimum wavelength for the call to ATRAN.
    * | **wl_max:** float
      | The maximum wavelength for the call to ATRAN.
    * | **wl_max_unit:** str, *optional* = "um"
      | The unit of the maximum wavelength for the call to ATRAN.
    * | **latitude:** float, *optional*
      | The observatory latitude for the call to ATRAN.
    * | **latitude_unit:** str, *optional* = "degree"
      | The unit of the observatory latitude for the call to ATRAN.
    * | **water_vapor:** float, *optional*
      | The water vapor overburden for the call to ATRAN.
    * | **water_vapor_unit:** str, *optional* = "um"
      | The unit of the water vapor overburden for the call to ATRAN.
    * | **n_layers:** float, *optional*
      | The number of atmospheric layers for the call to ATRAN.
    * | **zenith_angle:** float, *optional*
      | The zenith angle for the call to ATRAN.
    * | **zenith_angle_unit:** str, *optional* = "degree"
      | The unit of the zenith angle for the call to ATRAN (0 is towards the zenith).
    * | **resolution:** float, *optional*
      | The resolution for smoothing for the call to ATRAN (0 for no smoothing).
    * | **emission:** str, *optional*
      | The path to the file containing the spectral radiance of the emission. For details on the required file structure see also :ref:`reading_csv`.
    * | **temp:** float, *optional*
      | The atmospheric temperature used for grey body emission.
    * | **temp_unit:** str, *optional* = "K"
      | Unit of the atmospheric temperature used for black body emission using the complement of the transmittance.

StrayLight
----------
This component allows to model generic noise sources like stray light or zodiacal light from a file containing the spectral radiance of the emission.

.. code-block:: xml

    <optical_component type="StrayLight" emission="PathToEmissionFile"/>

Attributes:
    * | **emission:** str, *optional*
      | The path to the file containing the spectral radiance of the emission. For details on the required file structure see also :ref:`reading_csv`.

CosmicBackground
----------------
This component allows to model generic black body noise sources like the cosmic background.

.. code-block:: xml

    <optical_component type="CosmicBackground" temp="2.7" temp_unit="K" emissivity="1.0"/>

Attributes:
    * | **temp:** float
      | The temperature of the black body.
    * | **temp_unit:** str, *optional* = "K"
      | The unit of the black body's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **emissivity:** float, *optional*
      | The emissivity of the cosmic background.

Mirror
------
Model a mirror including the mirror's thermal emission as well as possible obstruction of the mirror and the thermal emission of the obstructing component.

.. code-block:: xml

    <optical_component type="Mirror" reflectance="PathToReflectance" emissivity="PathToEmissivity" temp="70" temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>

Attributes:
    * | **reflectance:** [str, float]
      | Either a floating point value for the reflectance or a path to the file containing the spectral reflectance coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **emissivity:** str, *optional*
      | The path to the file containing the spectral emissivity coefficients. For details on the required file structure see also :ref:`reading_csv`. If not given, 1 - reflectance is used.
    * | **temp:** float, *optional*
      | The temperature of the mirror for the thermal emission.
    * | **temp_unit:** str, *optional*
      | The unit of the mirror's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstruction:** float, *optional*
      | The obstruction factor of the mirror as ratio of the areas A\ :sub:`obstructor` / A\ :sub:`mirror`.
    * | **obstructor_temp:** float, *optional*
      | The temperature of the obstructing component for the thermal emission.
    * | **obstructor_temp_unit:** str, *optional*
      | The unit of the obstructing component's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstructor_emissivity:** float, *optional*
      | The emissivity of the obstructing component for the thermal emission. Valid ranges are 0.0 - 1.0. The default is 1.0.

Lens
----
Model a lens including the lens' thermal emission as well as possible obstruction of the lens and the thermal emission of the obstructing component.

.. code-block:: xml

    <optical_component type="Lens" transmittance="PathToTransmittance" emissivity="PathToEmissivity" temp="70" temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>

Attributes:
    * | **transmittance:** [str, float]
      | Either a floating point value for the transmittance or a path to the file containing the spectral transmittance coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **emissivity:** str, *optional*
      | The path to the file containing the spectral emissivity coefficients. For details on the required file structure see also :ref:`reading_csv`. If not given, 1 - transmittance is used.
    * | **temp:** float, *optional*
      | The temperature of the lens for the thermal emission.
    * | **temp_unit:** str, *optional*
      | The unit of the lens' temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstruction:** float, *optional*
      | The obstruction factor of the lens as ratio of the areas A\ :sub:`obstructor` / A\ :sub:`lens`.
    * | **obstructor_temp:** float, *optional*
      | The temperature of the obstructing component for the thermal emission.
    * | **obstructor_temp_unit:** str, *optional*
      | The unit of the obstructing component's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstructor_emissivity:** float, *optional*
      | The emissivity of the obstructing component for the thermal emission. Valid ranges are 0.0 - 1.0. The default is 1.0.

BeamSplitter
------------
Model a beam splitter including the beam splitter's thermal emission as well as possible obstruction of the beam splitter and the thermal emission of the obstructing component.

.. code-block:: xml

    <optical_component type="BeamSplitter" transmittance="PathToTransmittance" emissivity="PathToEmissivity" temp="70" temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>

Attributes:
    * | **transmittance:** [str, float]
      | Either a floating point value for the transmittance or a path to the file containing the spectral transmittance coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **emissivity:** str, *optional*
      | The path to the file containing the spectral emissivity coefficients. For details on the required file structure see also :ref:`reading_csv`. If not given, 1 - transmittance is used.
    * | **temp:** float, *optional*
      | The temperature of the beam splitter for the thermal emission.
    * | **temp_unit:** str, *optional*
      | The unit of the beam splitter's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstruction:** float, *optional*
      | The obstruction factor of the beam splitter as ratio of the areas A\ :sub:`obstructor` / A\ :sub:`beam splitter`.
    * | **obstructor_temp:** float, *optional*
      | The temperature of the obstructing component for the thermal emission.
    * | **obstructor_temp_unit:** str, *optional*
      | The unit of the obstructing component's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstructor_emissivity:** float, *optional*
      | The emissivity of the obstructing component for the thermal emission. Valid ranges are 0.0 - 1.0. The default is 1.0.

Filter
------
Model a beam splitter including the beam splitter's thermal emission as well as possible obstruction of the beam splitter and the thermal emission of the obstructing component.

.. code-block:: xml

    <optical_component type="Filter" transmittance="PathToTransmittance" emissivity="PathToEmissivity" temp="70" temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>

.. code-block:: xml

    <optical_component type="Filter" band="M" emissivity="PathToEmissivity" temp="70" temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>

.. code-block:: xml

    <optical_component type="Filter" start="400" start_unit="nm" end="480" end_unit="nm" emissivity="PathToEmissivity" temp="70" temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>

Attributes:
    * | **transmittance:** [str, float]
      | Either a floating point value for the transmittance or a path to the file containing the spectral transmittance coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **band:** str
      | The spectral Band of the filter. This has to be one of [``U``, ``B``, ``V``, ``R``, ``I``, ``J``, ``H``, ``K``, ``L``, ``M``, ``N``]
    * | **start:** float
      | The start wavelength of the pass band of the filter.
    * | **start_unit:** str
      | The unit of the start wavelength. This has to be one of [``m``, ``cm``, ``mm``, ``um``, ``nm``, ``pm``]. The default is ``m``.
    * | **end:** float
      | The end wavelength of the pass band of the filter.
    * | **end_unit:** str
      | The unit of the end wavelength. This has to be one of [``m``, ``cm``, ``mm``, ``um``, ``nm``, ``pm``]. The default is ``m``.
    * | **emissivity:** str, *optional*
      | The path to the file containing the spectral emissivity coefficients. For details on the required file structure see also :ref:`reading_csv`. If not given, 1 - transmittance is used.
    * | **temp:** float
      | The temperature of the beam splitter for the thermal emission.
    * | **temp_unit:** str, *optional*
      | The unit of the beam splitter's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstruction:** float, *optional*
      | The obstruction factor of the beam splitter as ratio of the areas A\ :sub:`obstructor` / A\ :sub:`filter`.
    * | **obstructor_temp:** float, *optional*
      | The temperature of the obstructing component for the thermal emission.
    * | **obstructor_temp_unit:** str, *optional*
      | The unit of the obstructing component's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstructor_emissivity:** float, *optional*
      | The emissivity of the obstructing component for the thermal emission. Valid ranges are 0.0 - 1.0. The default is 1.0.