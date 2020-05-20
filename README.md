# ESBO-ETC
A modular exposure time calculator for the ESBO telescope.

## Introduction
This repository contains the source code of the ESBO-ETC, a highly modular exposure time calculator.

ESBO-ETC aims on modelling the physical aspect of light coming from a target through optical components
(e.g. atmosphere, mirrors, lenses, ...) on the detector. The set up of this so called optical pipeline can be
individually defined using a configuration file. Additionally, the thermal emission of optical components, the
obstruction of components as well as different PSFs including pointing jitter can be considered.

Finally, ESBO-ETC allows the computation of either the necessary exposure time for a desired SNR, the SNR for a given
exposure time or, in case of a BlackBodyTarget, the sensitivity as the minimum apparent magnitude for a given exposure
time and SNR. All computations support a batch-mode, allowing to compute multiple scenarios at once.

### Features
ESBO-ETC offers many different optical components and features which will be explained in the following.

#### Targets
`<target type="" size=""/>`

Currently ESBO-ETC supports the following two different types of targets. A configuration can contain only one target
which has to be contained in the container `<astroscene>`. Each target consists of the basic tag
`<target>` and possible other target-type specific attributes.
* **`type`:** The type of the target. Currently, only `BlackBodyTarget` and `FileTarget` are supported.
* **`size`:** The size of the target which can be either `point` or `extended`. In case of a point-source, a PSF will be
used to determine the irradiance of each pixel. In case of a extended source, a uniform PSF is assumed, ignoring the
tags `<psf>`, `<jitter>`, and some instrument specific tags.

##### BlackBodyTarget
`<target type="BlackBodyTarget" temp="5778" temp_unit="K" mag="10" mag_unit="mag" band="B" size="point"/>`

Model a target as a black body of a given temperature and magnitude.
* **`temp`:** The temperature of the black body.
* **`temp_unit` _optional_:** The unit of the black body's temperature. This has to be one of [`K`, `Celsius`].
The default is `K`.
* **`mag`:** The apparent magnitude of the black body in magnitudes.
* **`mag_unit` _optional_:** The unit of the black body's magnitude. This has to be `mag`. The default is `mag`.
* **`band`:** The band used for fitting the black body's flux density to Vega's flux density. This has to be one of
[`U`, `B`, `V`, `R`, `I`, `J`, `H`, `K`, `L`, `M`, `N`].

##### FileTarget
`<target type="FileTarget" val="PathToFile" size="point"/>`

Create a target from a file containing the spectral flux densities of the target.
* **`val`:** The path to the file containing the spectral flux densities. For details on the required structure see
section _Reading spectral quantities from files_.

#### Optical Components
`<optical_component type=""/>`

Each optical component consists of the basic tag `<optical_component>` and the attribute `type` and possible other
component-specific attributes.
* **`type`:** The type of the optical component. This can be one of the following types.

##### Atmosphere
`<optical_component type="Atmosphere" transmittance="PathToTransmittanceFile" emission="PathToEmissionFile"/>`
                           
This component models the behaviour of an atmosphere which has a spectral transmittance and a spectral emission.
* **`transmittance`:** The path to the file containing the spectral transmittance coefficients. For details on the
required structure see section _Reading spectral quantities from files_.
* **`emission` _optional_:** The path to the file containing the spectral radiance of the emission. For details on the
required structure see section _Reading spectral quantities from files_.

##### StrayLight
`<optical_component type="StrayLight" emission="PathToEmissionFile"/>`

This component allows to model generic noise sources like stray light or zodiacal light from a file containing the
spectral radiance of the emission.
* **`emission` _optional_:** The path to the file containing the spectral radiance of the emission. For details on the
required structure see section _Reading spectral quantities from files_.

##### Mirror
`<optical_component type="Mirror" reflectance="PathToReflectance" emissivity="PathToEmissivity" temp="70" temp_unit="K"
obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>`

Model a mirror including the mirror's thermal emission as well as possible obstruction of the mirror and the thermal
emission of the obstructing component.
* **`reflectance`:** The path to the file containing the spectral reflectance coefficients. For details on the
required structure see section _Reading spectral quantities from files_.
* **`emissivity`:** The path to the file containing the spectral emissivity coefficients. For details on the
required structure see section _Reading spectral quantities from files_.
* **`temp` _optional_:** The temperature of the mirror for the thermal emission.
* **`temp_unit` _optional_:** The unit of the mirror's temperature. This has to be one of [`K`, `Celsius`].
The default is `K`.
* **`obstruction` _optional_:** The obstruction factor of the mirror as ratio of the areas
A<sub>obstructor</sub> / A<sub>mirror</sub>.
* **`obstructor_temp` _optional_:** The temperature of the obstructing component for the thermal emission.
* **`obstructor_temp_unit` _optional_:** The unit of the obstructing component's temperature. This has to be one of
[`K`, `Celsius`]. The default is `K`.
* **`obstructor_emissivity` _optional_:** The emissivity of the obstructing component for the thermal emission.
Valid ranges are 0.0 - 1.0. The default is 1.

##### Lens
`<optical_component type="Lens" transmittance="PathToTransmittance" emissivity="PathToEmissivity" temp="70"
temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>`

Model a lens including the lens' thermal emission as well as possible obstruction of the lens and the thermal
emission of the obstructing component.
* **`transmittance`:** The path to the file containing the spectral transmittance coefficients. For details on the
required structure see section _Reading spectral quantities from files_.
* **`emissivity`:** The path to the file containing the spectral emissivity coefficients. For details on the
required structure see section _Reading spectral quantities from files_.
* **`temp` _optional_:** The temperature of the lens for the thermal emission.
* **`temp_unit` _optional_:** The unit of the lens' temperature. This has to be one of [`K`, `Celsius`].
The default is `K`.
* **`obstruction` _optional_:** The obstruction factor of the lens as ratio of the areas
A<sub>obstructor</sub> / A<sub>lens</sub>.
* **`obstructor_temp` _optional_:** The temperature of the obstructing component for the thermal emission.
* **`obstructor_temp_unit` _optional_:** The unit of the obstructing component's temperature. This has to be one of
[`K`, `Celsius`]. The default is `K`.
* **`obstructor_emissivity` _optional_:** The emissivity of the obstructing component for the thermal emission.
Valid ranges are 0.0 - 1.0. The default is 1.

##### BeamSplitter
`<optical_component type="BeamSplitter" transmittance="PathToTransmittance" emissivity="PathToEmissivity" temp="70"
temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>`

Model a beam splitter including the beam splitter's thermal emission as well as possible obstruction of the beam
splitter and the thermal emission of the obstructing component.
* **`transmittance`:** The path to the file containing the spectral transmittance coefficients. For details on the
required structure see section _Reading spectral quantities from files_.
* **`emissivity`:** The path to the file containing the spectral emissivity coefficients. For details on the
required structure see section _Reading spectral quantities from files_.
* **`temp` _optional_:** The temperature of the beam splitter for the thermal emission.
* **`temp_unit` _optional_:** The unit of the beam splitter's temperature. This has to be one of [`K`, `Celsius`].
The default is `K`.
* **`obstruction` _optional_:** The obstruction factor of the beam splitter as ratio of the areas
A<sub>obstructor</sub> / A<sub>beam splitter</sub>.
* **`obstructor_temp` _optional_:** The temperature of the obstructing component for the thermal emission.
* **`obstructor_temp_unit` _optional_:** The unit of the obstructing component's temperature. This has to be one of
[`K`, `Celsius`]. The default is `K`.
* **`obstructor_emissivity` _optional_:** The emissivity of the obstructing component for the thermal emission.
Valid ranges are 0.0 - 1.0. The default is 1.

##### Filter
`<optical_component type="Filter" transmittance="PathToTransmittance" emissivity="PathToEmissivity"
temp="70" temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>`

`<optical_component type="Filter" band="M" emissivity="PathToEmissivity" temp="70"
temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>`

`<optical_component type="Filter" start="400" start_unit="nm" end="480" end_unit="nm" emissivity="PathToEmissivity"
temp="70" temp_unit="K" obstruction="0.2" obstructor_temp="70" obstructor_temp_unit="K" obstructor_emissivity="0.9"/>`

Model a beam splitter including the beam splitter's thermal emission as well as possible obstruction of the beam
splitter and the thermal emission of the obstructing component.
* **`transmittance`:** The path to the file containing the spectral transmittance coefficients. For details on the
required structure see section _Reading spectral quantities from files_.
* **`band`:** The spectral Band of the filter. This has to be one of [`U`, `B`, `V`, `R`, `I`, `J`, `H`, `K`, `L`, `M`,
`N`]
* **`start`:** The start wavelength of the pass band of the filter.
* **`start_unit`:** The unit of the start wavelength. This has to be one of [`m`, `cm`, `mm`, `um`, `nm`, `pm`].
The default is `m`.
* **`end`:** The end wavelength of the pass band of the filter.
* **`end_unit`:** The unit of the end wavelength. This has to be one of [`m`, `cm`, `mm`, `um`, `nm`, `pm`].
The default is `m`.
* **`emissivity`:** The path to the file containing the spectral emissivity coefficients. For details on the
required structure see section _Reading spectral quantities from files_.
* **`temp` _optional_:** The temperature of the beam splitter for the thermal emission.
* **`temp_unit` _optional_:** The unit of the beam splitter's temperature. This has to be one of [`K`, `Celsius`].
The default is `K`.
* **`obstruction` _optional_:** The obstruction factor of the beam splitter as ratio of the areas
A<sub>obstructor</sub> / A<sub>beam splitter</sub>.
* **`obstructor_temp` _optional_:** The temperature of the obstructing component for the thermal emission.
* **`obstructor_temp_unit` _optional_:** The unit of the obstructing component's temperature. This has to be one of
[`K`, `Celsius`]. The default is `K`.
* **`obstructor_emissivity` _optional_:** The emissivity of the obstructing component for the thermal emission.
Valid ranges are 0.0 - 1.0. The default is 1.

#### Detectors

#### Other Features
##### Reading spectral quantities from files
The format of a file has to be either structured text (e.g. CSV) or astropy ECSV and will be automatically detected.
In case of structured text, the units of the columns have to be defined in the column header within square brackets
(e.g. "wavelength [nm]"). The file must contain two columns with units: wavelength and the spectral quantity:

| wavelength [nm] | emission [W/(nm\*m^2\*sr)] |
|-----------------|--------------------------|
| 200             | 1.345e-15                |
| 201             | 2.234e-15                |
| ...             | ...                      |

## Running ESBO-ETC

## Configuration File

## Extending ESBO-ETC