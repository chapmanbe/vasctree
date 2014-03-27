"""
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
# vasctree
__version__='0.1.8.2'
