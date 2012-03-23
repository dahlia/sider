from __future__ import with_statement
import os.path
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from sider.version import VERSION


def readme():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
            return f.read()
    except (IOError, OSError):
        return ''


setup(name='Sider',
      packages=['sider', 'sidertests'],
      version=VERSION,
      description='A persistent object library based on Redis',
      long_description=readme(),
      license='MIT License',
      author='Hong Minhee',
      author_email='minhee' '@' 'dahlia.kr',
      maintainer='Hong Minhee',
      maintainer_email='minhee' '@' 'dahlia.kr',
      url='https://bitbucket.org/dahlia/sider',
      install_requires=['redis'],
      tests_require=['Attest'],
      test_loader='attest:auto_reporter.test_loader',
      test_suite='sidertests.tests',
      extras_require={'docs': ['Sphinx >= 1.1']},
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Database'
      ])

