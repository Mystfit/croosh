import os
from setuptools import setup, find_packages

#readme = open('README.rst', 'r')
#README_TXT = readme.read()

setup(name='Croosh',
      version='0.0.1',
      description='MongoDB render queue library',
      # long_description=README_TXT,
      author='Byron Mallett',
      author_email='byronated@gmail.com',
      dependency_links = ['git+https://github.com/mystfit/mongoqueue.git#egg=mongoqueue-0.7.2'],
      install_requires=["pymongo", "mongoqueue>=0.7.2"],
      packages=find_packages(),
      scripts=['scripts/croosh-server.py', 'scripts/croosh-client.py']
      )
