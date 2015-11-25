============
INTRODUCTION
============

vasctree is a python package for generating representations of vascular trees in volumetric images.

========
Overview
========
Package for creating vascular graphs based in the `NetworkX <http://networkx.github.io/>`_ Package

This package was largely developed as part of NIH HBL R01??

Applications based on this package have been described in the following publications and presentations

* Berty JAMIA 2011
* Berty JAMIA 2012

The methodology is similar to that described in [REF]

------------
Dependencies
------------

* Numpy:  used for array representation
* scipy: used for least-squares spline fitting of centerlines
* NetworkX: the basic graph representation of the vascular structures
* cython: used for speeding up point mapping
* SimpleITK: used for reading volumetric image formats

^^^^^^^^^^^^^^^^^^^^^^^^^^
Visualization dependencies
^^^^^^^^^^^^^^^^^^^^^^^^^^

* matplotlib: used for basic visualization of graphs
* mayavi: used for editing graphs
"""

--------------
INSTALLATION
--------------

vasctree is currently not registered with the python package index, so installation is a bit tedious.

Use mercurial to check the code out from the Google Code repository.

^^^^^^^^^^^^^
INSTALL cmvtg
^^^^^^^^^^^^^

cmvtg requires cython to be installed.

Change directory to trunk/src/vasctrees/cmvtg

Install the cmvtg package by typing: *python setup.py install*

^^^^^^^^^^^^^^^^
INSTALL vasctree
^^^^^^^^^^^^^^^^

Change directory to trunk/
Install the vasctree package by typing: *python setup.py install*

**NOTE** If you are installing these pacakges system wide, you may need root privileges.


-----
USAGE
-----
