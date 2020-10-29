ESBO-ETC is designed to be included as module in other Python scripts.
This is possible by importing the class ``esbo_etc`` from the module ``esbo_etc`` as shown below.

.. code-block:: python
    :linenos:

    from esbo_etc import esbo_etc

The class ``esbo_etc`` requires a path to the configuration file as initialization argument and some other optional paramaters.
The created object offers the method ``run()`` to trigger the computation.
The result of the computation is returned as Astropy quantity.
A Minimal example looks as follows:

.. code-block:: python
    :linenos:

    from esbo_etc import esbo_etc


    # Initialize a new ESBO-ETC object
    etc = esbo_etc("path_to_configuration_file.xml")

    # Run the calculations
    res = etc.run()

    print(res)
