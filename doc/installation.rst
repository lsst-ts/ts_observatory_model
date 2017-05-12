============
Installation
============

The installation of ``ts_observatory_model`` requires the use of the ``ts_dateloc`` package. Installation instructions for that package can be found `here <https://github.com/lsst-ts/ts_dateloc/blob/master/doc/installation.rst>`_. Once those instructions are complete, install the source code into your favorite location (called ``gitdir``) via::

	git clone https://github.com/lsst-ts/ts_observatory_model.git

With the stack environment setup as instructed, declare the package to EUPS::

	cd gitdir/ts_observatory_model
	eups declare ts_observatory_model git -r . -c
	setup ts_observatory_model git
	scons