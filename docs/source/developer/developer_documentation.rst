***********************
Developer Documentation
***********************

The following section provides detailed information on the the software architecture and on the possibilities to extend ESBO-ETC.
The source code of ESBO-ETC and this documentation can be found on the `IRS Gitea-server <https://egit.irs.uni-stuttgart.de/esbo_ds/ESBO-ETC>`_.

.. note::
   In the following, methods of the source code may be mentioned without details on the required parameters or the return values. Please refer to the :ref:`api` for details.

Project Structure
=================

This project is structured into several folders as shown below. The three main folders are ``docs``, which contains the documentation,
``esbo_etc`` containing all source files and ``tests``, where all tests are located.

::

    root
    ├── docs                        Documentation files
    │   └── source                  Source files of the documentation
    │       ├── configuration       Configuration chapter of the documentation
    │       ├── developer           Developer chapter of the documentation
    │       └── usage               Usage chapter of the documentation
    ├── esbo_etc                    Source code of ESBO-ETC
    │   ├── classes                 Contains all classes of the source code
    │   │   ├── optical_component   Contains all class files of the optical components
    │   │   ├── psf                 Contains all class files to model the different types of PSF
    │   │   ├── sensor              Contains all class files of the sensors
    │   │   └── target              Contains all class files of the targets
    │   ├── lib                     Contains all library functions
    │   └── esbo-etc.py             This is the main file to run the application
    └──  tests                      Contains all tests
        ├── data                    Necessary data for all tests
        ├── optical_component       Tests of the optical components
        ├── psf                     Tests of the different PSF implementations
        ├── sensor                  Tests of all sensors
        └── target                  Tests of all targets

Software Architecture
=====================

For modelling the radiation transportation, the `decorator pattern <https://en.wikipedia.org/wiki/Decorator_pattern>`_ and the
`factory method pattern <https://en.wikipedia.org/wiki/Factory_method_pattern>`_ were used as shown in the figure below.

.. figure:: decorator_pattern.pdf
   :alt: Decorator Pattern
   :width: 100%

   The decorator pattern used for the radiation transportation.

The radiation transportation pipeline consists always of a single target emitting the signal radiation.
This target may be encapsulated by multiple optical components which manipulate the radiation by either adding their own background radiation or by decreasing the transmitted radiation.
The outermost part of the radiation transportation pipeline is formed by some kind of sensor component, detecting the radiation.
The quality of the detected signal can then be determined by calculating the signal to noise ration (SNR).

.. figure:: class_diagram.pdf
   :alt: Class Diagram

   Class diagram of the software architecture.

Radiant Interface
-----------------

In order to implement the aforementioned radiation transportation pipeline, a sophisticated software architecture has been designed.
As shown in the class diagram, the class ``IRadiant`` forms the backbone of the structure.
This interface class defines the two methods ``calcSignal()`` and ``calcBackground()`` and therefore the basic layout of all decorated classes.
All targets and optical components implement this interface in oder to allow the cascading calculation of the signal and background fluxes.
For both targets and optical components exists an abstract superclass which implements the required interface. This allows the actual
classes to focus on the initialization and calculation of their own properties, ignoring the implementation of the interface.



Target
------

The abstract class ``ATarget`` implements the interface provided by ``IRadiant`` and provides the abstract method ``checkConfig()`` which is used to check the relevant parts of the configuration file for this component.
All available target types must inherit from ``ATarget`` and therefore must implement the method ``checkConfig()``.
As the superclass ``ATarget`` implements the interface provided by ``IRadiant``, the compatibility to the radiation transportation pipeline is ensured.
All subclasses therefore only set up a ``SpectralQty``-object containing the emitted radiation and call the constructor of ``ATarget``.

Optical Component
-----------------

The abstract class ``AOpticalComponent`` implements the interface provided by ``IRadiant`` and thereby the two methods ``calcSignal()`` and ``calcBackground()``.
This includes the treatment of central obstruction of the components as well as transmittance / reflectance coefficients.
Additionally, ``AOpticalComponent`` provides the two methods ``propagate()`` for handling the propagation of incoming radiation through the optical component and ``ownNoise()`` for calculating the background radiation contribution of this component.
The two function may be overwritten by the subclasses, if a custom implementation is necessary.
Otherwise, the parameters ``transreflectivity`` and ``noise`` of the constructor method will be used for the calculations.
In order to check the relevant parts of the configuration file for this component, the class provides the abstract method ``checkConfig()`` which has to be implement by all subclasses.

According to the restrictions above, subclasses of ``AOpticalComponent`` can be implemented in two possible ways: either by providing the parameters ``transreflectivity`` and ``noise`` to the constructor of the superclass or by implementing the two methods ``propagate()`` and ``ownNoise()``.

Hot Optical Component
^^^^^^^^^^^^^^^^^^^^^

The abstract class ``AHotOpticalComponent`` extends the abstract superclass ``AOpticalComponent`` by implementing the method ``ownNoise()`` assuming grey body radiation in order to model optical components with a thermal background contribution.
This has the consequence, that every subclass of ``AHotOpticalComponent`` must implement the method ``propagate()``, which handles to propagation of the signal and backgroudn radiation through the component.
Like ``AOpticalComponent``, the class ``AHotOpticalComponent`` provides the abstract method ``checkConfig()`` for checking the configuration file.

Sensor
------



Classes
=======

All spectral quantities used for calculations, e.g. spectral flux densities, spectral reflectances, etc., are handled as ``SpectralQty``-objects, which support operations like additions, substractions, multiplications, divisions, etc.
Additionally, ESBO-ETC uses Astropy-units for all calculations in order to avoid any conversion errors.
The class ``Entry`` is used to represent the tags of the XML-configuration file.

Extending ESBO-ETC
==================

ESBO-ETC can be easily extended by adding new optical components or a new detector component.

Adding Targets
--------------



Adding Optical Components
-------------------------

Extending ESBO-ETC by a new optical component consists of two tasks.

First of all, the new optical component class has to be implemented in a separate file in the *classes*-folder.
The new class must inherit from the abstract class ``AOpticalComponent`` or, in case of an optical component with thermal emission, from the abstract class ``AHotOpticalComponent`` and implement all abstract methods.
In case of a cold optical component, the new class must implement the method ``checkConfig()`` and call the constructor of the super class.
In case of a hot optical component, the new class must implement the method ``checkConfig()`` as well as the method ``propagate()`` and call the constructor of the super class.

The method ``checkConfig()`` is used for checking the XML-configuration file and accepts as parameter the corresponding part of the configuration as ``Entry``-object.
In case of an configuration error, the method must return the corresponding error message.

The method ``propagate()`` is used to model the propagation of incoming radiation through the optical component.
Therefore, this method receives as parameter the incoming radiation as ``SpectralQty``-object and must return the manipulated radiation as ``SpectralQty``-object.

The second task consists of 

Adding Detector Components
--------------------------

