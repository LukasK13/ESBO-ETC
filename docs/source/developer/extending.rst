ESBO-ETC can be easily extended by adding new targets, new optical components or a new detector component.
In the following, only the minimal required changes in the source code are described.
Of course, the documentation must be edited as well if new components are added.


Adding Targets
--------------

Adding a new target type to ESBO-ETC is the easiest extension.

In the first place, the new target component must be defined in a new file *classes*-folder.
Thereby, the new component must subclass ``ATarget`` in order to be decoratable by other optical components.
The class must provide a constructor which accepts all attributes of the configuration tag as parameters and initializes the superclass passing the emitted radiation as parameter.
Additionally, the class must implement the method ``checkConfig()`` in order to check the configuration.
In case of an configuration error, the method must return the corresponding error message.

Optionally, the factory method ``create()`` of the class ``RadiantFactory`` has to be modified, if the constructor of the new component requires more parameters than the configuration tag attributes.


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

The optional second task consists of modifying the factory method ``create()`` of the class ``RadiantFactory`` in order to properly initialize the new optical component from the configuration.
This is only necessary if the new optical component needs additional parameters besides the attributes of the corresponding configuration tag of if the new component provides multiple constructors (see class ``Filter``).

Adding Detector Components
--------------------------

In order to add a new detector component, two tasks must be completed.

The new detector component must be implemented in a designated file in the *classes*-folder, subclassing ``ASensor``.
Thereby, the new class must implement the three methods ``calcSNR()``, ``calcExpTime()`` and ``calcSensitivity()``.
All three methods obtain the incoming background and signal radiation as well as the obstruction factor as parameters apart from some specific parameters and must return the corresponding calculated value.
Additionally, all three methods must be able to calculate multiple SNRs, exposure times or sensitivities at once if an array of specific parameters is provided.

Besides the implementation of the detector, the factory method ``create()`` of the class ``SensorFactory`` must be modified.
In detail, a new if-branch must be added which assembles all necessary parameters for the constructor of the new component and calls the constructor.
