#!python
# -*- coding: utf-8 -*-

"""
This is the setup for the biosim package
"""

__author__ = 'Therese Knapskog and Astrid Moum'
__email__ = 'therese.knapskog@nmbu.no and astridmo@nmbu.no'

from setuptools import setup
import codecs
import os


def read_readme():
    current_path = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(current_path, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


setup(
      # Basic information
      name='BIOSIM G19',
      version='0.1.0',

      # Packages to include
      packages=['biosim'],
      # Metadata
      description='A Simulation of the Ecosystem of Rossumoya written in Python',
      long_description=read_readme(),
      author='Therese Knapskog and Astrid Moum, NMBU',
      author_email='therese.knapskog@nmbu.no and astridmo@nmbu.no',
      url='https://gitlab.com/nmbu.no/emner/inf200/h2020/januaryblock/dga5/g19_knapskog_moum',
      keywords='biosim simulation',
      requires=['numpy', 'matplotlib', 'math', 'operator', 'os', 'pytest', 'random', 'scipy.stats', 'subprocess'],
      license='MIT License',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Science :: Stochastic processes',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        ]
)
