from distutils.core import setup
from distutils.extension import Extension
from numpy.distutils.misc_util import get_numpy_include_dirs
from Cython.Distutils import build_ext

numpy_dirs = get_numpy_include_dirs()
  
ext_modules = [
  Extension("cmvtg", ["cmvtg.pyx"], include_dirs=numpy_dirs),
  #Extension("CSkeletonGraph", ["CSkeletonGraph.pyx"], include_dirs=numpy_dirs),  
  ]

setup(name='cmvtg',
      version='0.1.1',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)
