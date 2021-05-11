"""Setup file and install script for CMDBtools.

Version 1.0.0 (Nov 22, 2018)
Copyright (c) 2018 Shujia Huang
"""
import os
from argparse import Namespace

try:
    from setuptools import setup, find_packages

    _has_setuptools = True
except ImportError:
    from distutils.core import setup, find_packages

DESCRIPTION = "cmdbtools: A command line tools for CMDB variant browser."

meta = Namespace(
    __DISTNAME__="cmdbtools",
    __AUTHOR__="Shujia Huang",
    __AUTHOR_EMAIL__="huangshujia9@gmail.com",
    __URL__="https://github.com/ShujiaHuang/cmdbtools",
    __LICENSE__="BSD (3-clause)",
    __DOWNLOAD_URL__="https://github.com/ShujiaHuang/cmdbtools",
    __VERSION__="1.1.2",
)

if __name__ == "__main__":
    #long_description = os.path.split(os.path.realpath(__file__))[0] + "/README.md"
    THIS_PATH = os.path.abspath(os.path.dirname(__file__))
    long_description = os.path.join(THIS_PATH, "README.md")

    setup(name=meta.__DISTNAME__,
          version=meta.__VERSION__,
          author=meta.__AUTHOR__,
          author_email=meta.__AUTHOR_EMAIL__,
          maintainer=meta.__AUTHOR__,
          maintainer_email=meta.__AUTHOR_EMAIL__,
          description=DESCRIPTION,
          long_description=(open(long_description).read()),
          long_description_content_type="text/markdown",
          license=meta.__LICENSE__,
          url=meta.__URL__,
          download_url=meta.__URL__,
          packages=find_packages(),
          include_package_data=True,
          install_requires=[
              "PyYAML>=5.1.2"
          ],
          entry_points={
              "console_scripts": [
                  "cmdbtools = cmdbtools.cmdbtools:main"
              ]
          },
          classifiers=[
              "Intended Audience :: Science/Research",
              "Programming Language :: Python :: 3.7",
              "Programming Language :: Python :: 3.8",
              "License :: OSI Approved :: BSD License",
              "Topic :: Scientific/Engineering :: Bio-Informatics",
              "Operating System :: POSIX",
              "Operating System :: POSIX :: Linux",
              "Operating System :: MacOS"],
          )
