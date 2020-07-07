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
