.. :changelog:

History
-------

1.1.0 (2020-06-22)
~~~~~~~~~~~~~~~~~~

* Remove unused `__init__` files.
* Add license header to all files.
* Reformat code with black and add latest style configurations.
* Update import statements.
* Remove dependency on lsst_utils.
* Update import of version to work when there is no version file available.
* Add support for conda packaging.

1.0.6 (2018-11-21)
~~~~~~~~~~~~~~~~~~

* Update base parameters, (before they are updated by confdict)
* Use ConfigParser instead of deprecated SafeConfigParser
* Update parameters how we're supposed to
* Update unit test on model to account for parameters update.
* Set parameters so that unit test passes -- consider if these are correct parameters later!
* Make unit tests pass
* Updated follow_up and resume_angle to True (expected behavior); updated unit test

1.0.5 (2018-08-31)
~~~~~~~~~~~~~~~~~~

* Add note to target test string.

1.0.4 (2018-08-29)
~~~~~~~~~~~~~~~~~~

* Implement cold start:
  * Adds some necessary information to perform cold start.
    This is a temporary fix. A permanent solution will be implemented soon.
  * Add observation class which is a subclass of Target.
  * Add setters for some of the properties on Target.

1.0.3 (2018-03-24)
~~~~~~~~~~~~~~~~~~

* Fixed docstring.

1.0.2 (2018-03-08)
~~~~~~~~~~~~~~~~~~

* Fix dec - decl problem with SAL objects.

1.0.1 (2017-09-14)
~~~~~~~~~~~~~~~~~~

* Fixing Python 2 failing test

1.0.0 (2017-05-22)
~~~~~~~~~~~~~~~~~~

* Provides observatory model for slew calculations
* Fixes issue with double radian conversion in the closed loop optics correction altitude limits
* Added back filter for slew activities with delay equaling zero when all activities asked for
