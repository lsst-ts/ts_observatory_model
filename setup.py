from setuptools import setup
import setuptools_scm

setup(
    version=setuptools_scm.get_version(
        write_to="python/lsst/ts/observatory/model/version.py"
    )
)
