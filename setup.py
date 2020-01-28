# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

requires = [

    # Core
    'six==1.11.0',
    'ttn<3',
    'influxdb==5.2.1',
    'pymongo==3.7.2',
]

extras = {
    'test': [
    ],
}

setup(name='ttnlogger',
      version='0.2.0',
      description='Converge TTN messages into InfluxDB and MongoDB and display in Grafana',
      long_description=README,
      license="AGPL 3, EUPL 1.2",
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "Topic :: Communications",
        "Topic :: Database",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Archiving",
        "Topic :: System :: Networking :: Monitoring",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS"
        ],
      author='Andreas Motl',
      author_email='andreas@hiveeyes.org',
      url='https://github.com/daq-tools/ttnlogger',
      keywords='data acquisition ' +
               'ttn mqtt mosquitto influxdb mongodb grafana',
      packages=find_packages(),
      include_package_data=True,
      package_data={
      },
      zip_safe=False,
      test_suite='ttnlogger.test',
      install_requires=requires,
      extras_require = extras,
      tests_require=extras['test'],
      dependency_links=[
      ],
      entry_points={
          'console_scripts': [
              'ttnlogger = ttnlogger.ttn_logger:run',
          ],
      },
)
