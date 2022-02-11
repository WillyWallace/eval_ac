#!/usr/bin/env python

from setuptools import setup

setup(name='read_and_visualize_abscal-his',
      version='1.0',
      description='reads the ABSCAL.HIS fiel and visualizes the results of the absolute calibration of the microwave radiometer HATPRO with liquid nitrogen',
      author='Andreas Foth',
      author_email='andreas.foth@uni-leipzig.de',
      url='https://github.com/WillyWallace/read_and_visualize_abscal-his.git',
      license='MIT',
      packages=[],
      install_requires=[
          'torch', 
          'xarray',
          'rpgpy',
          'toml',
      ],
     )
