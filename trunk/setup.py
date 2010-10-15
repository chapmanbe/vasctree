import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(name='VascTree',
      version='0.1.1',
      description='Python Vascular Tree',
      author='Brian Chapman and Holly Berty',
      author_email='chapbe@pitt.edu',
      url='http://www.dbmi.pitt.edu/quiil',
      #py_modules = pyn,
      packages=find_packages('src'),
      package_dir={'':'src'},
      #install_requires = ['python>=2.5','numpy>=1.3','scipy>=0.7','networkx>=1.0.dev1492'],      
     )
