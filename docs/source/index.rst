.. BioSim documentation master file, created by
   sphinx-quickstart on Thu Jan  7 09:58:13 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to BioSim's documentation
=================================

**BioSim is a simulation of an island's ecosystem.**

   - The ecosystem is evaluated by the population of two animal species.
   - The island consist of one or several cells of landscape.
   - The landscape cells can contain fodder and animal populations.

Package content
###############
The package consist of five modules.

**The module island constructs an island:**

   - with landscapes and animals,
   - by implementing the modules animal and landscape.

**The module simulation constructs a simulation**

   - with visualisation of an island
   - by implementing the modules island and graphics.

Module documentation
====================

.. toctree::
   :maxdepth: 3

   base_modules
   simulation

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
