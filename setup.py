"""Setup file and install script for CMDBtools.

Version 1.0.0 (Nov 22, 2018)
Copyright (c) 2018 Shujia Huang
"""
import os
import sys

try:
    from setuptools import setup, find_packages
    _has_setuptools = True
except ImportError:
    from distutils.core import setup, find_packages


DESCRIPTION = "cmdbtools: A command line tools for CMDB variant browser."
DISTNAME = 'cmdbtools'
MAINTAINER = 'Shujia Huang (at) BGI'
MAINTAINER_EMAIL = 'huangshujia@bgi.com'
URL = 'https://github.com/ShujiaHuang/cmdbtools'
LICENSE = 'BSD (3-clause)'
DOWNLOAD_URL = 'https://github.com/ShujiaHuang/cmdbtools'
VERSION = "1.0.6.2"


if __name__ == "__main__":

    long_description = os.path.split(os.path.realpath(__file__))[0] + "/README.rst"
    #requirements_file = os.path.split(os.path.realpath(__file__))[0] + "/requirements.txt"

    #requirements = []
    #with open(requirements_file) as I:
    #  for line in I:
    #    requirements.append(line.strip())

    setup(name=DISTNAME,
          version=VERSION,
          author=MAINTAINER,
          author_email=MAINTAINER_EMAIL,
          maintainer=MAINTAINER,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          long_description=(open(long_description).read()),
          license=LICENSE,
          url=URL,
          download_url=DOWNLOAD_URL,
          packages=find_packages(),
          include_package_data=True,
          install_requires=[
            "PyYAML>=5.1.2"
          ],

          # scripts = ['cmdbtools/cmdbtools.py'],
          entry_points = {

             'console_scripts': [
                  'cmdbtools = cmdbtools.cmdbtools:main'
              ]
          },
          classifiers=[
              'Intended Audience :: Science/Research',
              'Programming Language :: Python :: 2.7',
              'License :: OSI Approved :: BSD License',
              'Topic :: Scientific/Engineering :: Bio-Informatics',
              'Operating System :: POSIX',
              'Operating System :: POSIX :: Linux',
              'Operating System :: MacOS'],
    )
