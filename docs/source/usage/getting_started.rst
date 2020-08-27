***************
Getting Started
***************
This chapter provides information on how to start using ESBO-ETC.

============
Installation
============
A Python 3 installation is required to run ESBO-ETC. You can get the latest python version
`here <https://www.python.org/downloads/>`_.

In order to get ESBO-ETC, clone the code from the IRS git server using

.. code-block:: bash
    :linenos:

    git clone https://egit.irs.uni-stuttgart.de/esbo_ds/ESBO-ETC.git

or download the code from the `IRS git server <https://egit.irs.uni-stuttgart.de/esbo_ds/ESBO-ETC>`_.

Python Virtual Environment
--------------------------

It is advisable to create a python virtual environment for ESBO-ETC where all necessary packages will be installed.
To create a virtual environment and install all packages, got to the project's root directory an run

Linux / MacOS
^^^^^^^^^^^^^

.. code-block:: bash
    :linenos:

    python3 -m venv venv
    source venv/bin/activate
    python venv/bin/pip install -r requirements.txt

Windows
^^^^^^^

It might be possible that you need to install `Microsoft Build Tools for C++ <https://visualstudio.microsoft.com/visual-cpp-build-tools/>`_ in order to compile astropy.

.. code-block:: bash
    :linenos:

    conda create -n venv
    conda activate venv
    conda install -c anaconda pip
    pip install -r requirements.txt

Global Python installation
--------------------------
Instead of a virtual environment, the global python installation can be used to run ESBO-ETC. Therefore, the necessary
packages need to be installed by running the following command from the project's root directory.

Linux / MacOS
^^^^^^^^^^^^^

.. code-block:: bash
    :linenos:

    pip install -r requirements.txt

Windows
^^^^^^^

.. code-block:: bash
    :linenos:

    conda install -c anaconda pip
    pip install -r requirements.txt

================
Running ESBO-ETC
================
ESBO-ETC can be run using in multiple ways as explained in the following subsections. However all methods provide the
same options which can be shown using the parameter ``-h`` or ``--help``.

The following options are available:

:-h, -\-help: Show the help.
:-c, -\-config: Specify the path to the configuration file. Default is esbo-etc_defaults.xml.
:-l, -\-logging: Specify the log level for the application. Possible levels are DEBUG, INFO, WARNING, ERROR.
:-v, -\-version: Print version information.
:-m, -\-manual: Print the manual.


Shell-Script
------------
The recommended way to run ESBO-ETC is to use the provided shell-script which will add the project's root directory to
the PATH-variable. However the shell-script only works for virtual environment installations with the virtual environment named ``venv``.

Linux / MacOS
^^^^^^^^^^^^^

.. code-block:: bash
    :linenos:

    ./run_esbo-etc [-h] [-c config.xml] [-l LOGGING] [-v] [-m]

Windows
^^^^^^^

.. code-block:: bash
    :linenos:

    run_esbo-etc.bat [-h] [-c config.xml] [-l LOGGING] [-v] [-m]

Python Interpreter
------------------
An alternative way to start ESBO-ETC is by using the python interpreter from the command line. This method works for
both a virtual environment as well as for the global python installation. Launching ESBO-ETC can be done using

.. code-block:: bash
    :linenos:

    python esbo_etc/esbo-etc.py [-h] [-c config.xml] [-l LOGGING] [-v] [-m]

==================
Component Overview
==================
ESBO-ETC offers many different components to model the path from the astronomical target to the detector. All components
can be divided into the three following classes.

Target
------
The component class *Target* models astronomical targets, defining the spectral flux density of their signal and their
shape (point source vs. extended source). Currently, two different target types are available:

* A target modelled as **black body** with a given temperature and apparent magnitude.
* A target with the signal's spectral flux density read from a **file**.

Optical Component
-----------------
Multiple optical components are available for modelling the signal and background flux propagation. The hot optical
components with a thermal grey body emission form a subclass of the optical components. Currently, the following optical
components are available

* An **atmosphere** component modelling the atmospheric transmittance and emission, both read from files.
* A **stray light** component for modelling generic background source like zodiacal light or earth stray light.
* A **cosmic background** component to model thermal black body background radiation like the 2.7 K cosmic background radiation.
* Hot optical components with thermal emission of a given temperature and emissivity:

    * A **mirror** component modelling the optical properties of a mirror like the mirror's reflectance.
    * A **lens** component the optical properties of a lens like the lens' transmittance.
    * A **beam splitter** component the optical properties of a beam splitter like the beam splitter's transmittance.
    * A **filter** component the optical properties of a filter like the filter's transmittance.

Sensor
------
Currently, two sensor components are available:

* The **imager** detector for generic imaging sensors like CCDs providing many parameters to adapt the component
  to the needs like the dark current, the read noise, pixel size, array size but also parameters for the photometric
  aperture like the percentage of contained energy or the shape of the photometric aperture.
* The **heterodyne** sensor for spectroscopy using the heterodyne principle providing also multiple parameters.
