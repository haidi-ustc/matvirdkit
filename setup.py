#!/usr/bin/env python
# coding: utf-8

import sys
import platform
import datetime
from os import path
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext as _build_ext

readme_file = path.join(path.dirname(path.abspath(__file__)), 'README.md')
try:
    from m2r import parse_from_file
    readme = parse_from_file(readme_file)
except ImportError:
    with open(readme_file) as f:
         readme = f.read()

default_prefix='matvirdkit'
today = datetime.date.today().strftime("%b-%d-%Y")
with open(path.join(default_prefix, '_date.py'), 'w') as fp :
    fp.write('date = \'%s\'' % today)
install_requires=["pymatgen==2022.4.26",
                   "pydantic==1.9.0",
                   "pymongo==4.1.1",
                   "Flask==2.1.2",
                   "fastapi==0.75.2"],

setup(
    name="matvirdkit",
    packages=find_packages(),
#    use_scm_version={'write_to': 'maptool/_version.py'},
#    setup_requires=['setuptools_scm'],
    install_requires=install_requires,
    author="Matvird Team",
    author_email="",
    maintainer="haidi",
    maintainer_email="haidi@mail.ustc.edu.cn",
    url="https://github.com/haidi-ustc/matvirdkit",
    license="GNU Lesser General Public License v3 (LGPLv3)",
    description=default_prefix+" is a pre- and post-processing software for materials science"
                "This software is based on Pymatgen, ASe and  some open-source Python libraries.",
    long_description=readme,
    long_description_content_type="text/markdown",
    keywords=["database", "api", "mongoDB" , "drone" ],
    data_files=[ ( "matvirdkit/model/vasp/calc_types/", ["matvirdkit/model/vasp/calc_types/run_types.yaml",])],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Computer",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    entry_points={
          'console_scripts': []
#              'mvdkit = matvirdkit.builder.cli:main'],
 }
)
