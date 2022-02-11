#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='read_and_visualize_abscal-his',
      version='1.0',
      description='reads the ABSCAL.HIS fiel and visualizes the results of the absolute calibration of the microwave radiometer HATPRO with liquid nitrogen',
      author='Andreas Foth',
      author_email='andreas.foth@uni-leipzig.de',
      url='https://github.com/WillyWallace/read_and_visualize_abscal-his.git',
      license='MIT',
      packages=find_packages(),
      python_requires=>=3.6,
      install_requires=[numpy>=1.22.2, xarray>=0.21.1, datetime, matplotlib, collections],
      classifiers=[
        "Development Status :: 1 - Beta",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
    ],
     )
