=====
Usage
=====

The main class for use in this package is :py:class:`.ObservatoryModel`. Many of the other classes are used as internal support to the model class. Those that are necessary for use outside the model will be detailed in the examples. Begin by creating an instance of the :py:class:`.ObservatoryModel`. The default location used within the model is the LSST observing site. 

.. code-block:: python

  from lsst.ts.observatory.model import ObservatoryModel
  obmod = ObservatoryModel()

In order for the model to function correctly, it needs to be configures and updated to a given timestamp. The class provides many functions for configuring the various sub-systems, but most will want to use the stored defaults. The following runs through this procedure. The instance can be printed to show the state of the observatory model.

.. code-block:: python

  obmod.configure_from_module()
  obmod.update_state(1672542000)
  print(obmod)
  t=1672542000.0 ra=74.765 dec=-26.744 ang=180.000 filter=r track=False alt=86.500 az=0.000 pa=180.000 rot=0.000 telaz=0.000 telrot=0.000 mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']

Now, calculate the slew delay in seconds to the South Celestial Pole field (RA=0.0, Dec=-90.0). The field will be observed in the r band filter currently in front of the camera. The observing cadence for the field will be two 15 second exposures.

.. code-block:: python

  from lsst.ts.observatory.model import Target
  import numpy
  target = Target(0, 1, "r", numpy.radians(0.0), numpy.radians(-90.0), 0.0, 2, [15.0, 15.0])
  delay = obmod.get_slew_delay(target)
  delay
  142.99999999999997

Now, observe that target. This call will slew the telescope and perform the camera cadence.

.. code-block:: python

  obmod.observe(target)
  print(obmod)
  t=1672542177.0 ra=0.000 dec=-90.000 ang=74.765 filter=r track=True alt=30.244 az=180.000 pa=75.505 rot=0.740 telaz=180.000 telrot=0.740 mounted=['g', 'r', 'i', 'z', 'y'] unmounted=['u']

See the API documentation for :py:class:`.ObservatoryModel`.