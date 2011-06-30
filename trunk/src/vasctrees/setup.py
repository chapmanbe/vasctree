import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(name='vasctree',
      version='0.1.5',
      description='Python Vascular Tree',
      author='Brian Chapman and Holly Berty',
      author_email='brchapman@ucsd.edu',
      #py_modules = pyn,
      packages=find_packages('src'),
      package_dir={'':'src'},
      install_requires = ['python>=2.6','numpy>=1.3','scipy>=0.7','networkx>=1.0.dev1492'],      
     )
