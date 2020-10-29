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