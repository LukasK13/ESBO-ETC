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

.. code-block:: xml

    <optical_component type="Atmosphere" transmittance="PathToTransmittanceFile" emission="PathToEmissionFile"/>

Attributes:
    * | **transmittance:** str
      | The path to the file containing the spectral transmittance coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **emission:** str, *optional*
      | The path to the file containing the spectral radiance of the emission. For details on the required file structure see also :ref:`reading_csv`.

StrayLight
----------
This component allows to model generic noise sources like stray light or zodiacal light from a file containing the spectral radiance of the emission.

.. code-block:: xml

    <optical_component type="StrayLight" emission="PathToEmissionFile"/>

Attributes:
    * | **emission:** str, *optional*
      | The path to the file containing the spectral radiance of the emission. For details on the required file structure see also :ref:`reading_csv`.

Mirror
------
Model a mirror including the mirror's thermal emission as well as possible obstruction of the mirror and the thermal emission of the obstructing component.

.. code-block:: xml

    <optical_component type="Mirror" reflectance="PathToReflectance" emissivity="PathToEmissivity" temp="70" temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>

Attributes:
    * | **reflectance:** str
      | The path to the file containing the spectral reflectance coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **emissivity:** str, *optional*
      | The path to the file containing the spectral emissivity coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **temp:** str, *optional*
      | The temperature of the mirror for the thermal emission.
    * | **temp_unit:** str, *optional*
      | The unit of the mirror's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstruction:** str, *optional*
      | The obstruction factor of the mirror as ratio of the areas A\ :sub:`obstructor` / A\ :sub:`mirror`.
    * | **obstructor_temp:** str, *optional*
      | The temperature of the obstructing component for the thermal emission.
    * | **obstructor_temp_unit:** str, *optional*
      | The unit of the obstructing component's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstructor_emissivity:** str, *optional*
      | The emissivity of the obstructing component for the thermal emission. Valid ranges are 0.0 - 1.0. The default is 1.0.

Lens
----
Model a lens including the lens' thermal emission as well as possible obstruction of the lens and the thermal emission of the obstructing component.

.. code-block:: xml

    <optical_component type="Lens" transmittance="PathToTransmittance" emissivity="PathToEmissivity" temp="70" temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>

Attributes:
    * | **transmittance:** str
      | The path to the file containing the spectral transmittance coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **emissivity:** str, *optional*
      | The path to the file containing the spectral emissivity coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **temp:** str, *optional*
      | The temperature of the lens for the thermal emission.
    * | **temp_unit:** str, *optional*
      | The unit of the lens' temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstruction:** str, *optional*
      | The obstruction factor of the lens as ratio of the areas A\ :sub:`obstructor` / A\ :sub:`lens`.
    * | **obstructor_temp:** str, *optional*
      | The temperature of the obstructing component for the thermal emission.
    * | **obstructor_temp_unit:** str, *optional*
      | The unit of the obstructing component's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstructor_emissivity:** str, *optional*
      | The emissivity of the obstructing component for the thermal emission. Valid ranges are 0.0 - 1.0. The default is 1.0.

BeamSplitter
------------
Model a beam splitter including the beam splitter's thermal emission as well as possible obstruction of the beam splitter and the thermal emission of the obstructing component.

.. code-block:: xml

    <optical_component type="BeamSplitter" transmittance="PathToTransmittance" emissivity="PathToEmissivity" temp="70" temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>

Attributes:
    * | **transmittance:** str
      | The path to the file containing the spectral transmittance coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **emissivity:** str, *optional*
      | The path to the file containing the spectral emissivity coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **temp:** str, *optional*
      | The temperature of the beam splitter for the thermal emission.
    * | **temp_unit:** str, *optional*
      | The unit of the beam splitter's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstruction:** str, *optional*
      | The obstruction factor of the beam splitter as ratio of the areas A\ :sub:`obstructor` / A\ :sub:`beam splitter`.
    * | **obstructor_temp:** str, *optional*
      | The temperature of the obstructing component for the thermal emission.
    * | **obstructor_temp_unit:** str, *optional*
      | The unit of the obstructing component's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstructor_emissivity:** str, *optional*
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
    * | **transmittance:** str
      | The path to the file containing the spectral transmittance coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **band:** str
      | The spectral Band of the filter. This has to be one of [``U``, ``B``, ``V``, ``R``, ``I``, ``J``, ``H``, ``K``, ``L``, ``M``, ``N``]
    * | **start:** str
      | The start wavelength of the pass band of the filter.
    * | **start_unit:** str
      | The unit of the start wavelength. This has to be one of [``m``, ``cm``, ``mm``, ``um``, ``nm``, ``pm``]. The default is ``m``.
    * | **end:** str
      | The end wavelength of the pass band of the filter.
    * | **end_unit:** str
      | The unit of the end wavelength. This has to be one of [``m``, ``cm``, ``mm``, ``um``, ``nm``, ``pm``]. The default is ``m``.
    * | **emissivity:** str, *optional*
      | The path to the file containing the spectral emissivity coefficients. For details on the required file structure see also :ref:`reading_csv`.
    * | **temp:** str
      | The temperature of the beam splitter for the thermal emission.
    * | **temp_unit:** str, *optional*
      | The unit of the beam splitter's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstruction:** str, *optional*
      | The obstruction factor of the beam splitter as ratio of the areas A\ :sub:`obstructor` / A\ :sub:`filter`.
    * | **obstructor_temp:** str, *optional*
      | The temperature of the obstructing component for the thermal emission.
    * | **obstructor_temp_unit:** str, *optional*
      | The unit of the obstructing component's temperature. This has to be one of [``K``, ``Celsius``]. The default is ``K``.
    * | **obstructor_emissivity:** str, *optional*
      | The emissivity of the obstructing component for the thermal emission. Valid ranges are 0.0 - 1.0. The default is 1.0.