# setup.py for stmtool
#
# Direct install (all systems):
#   "python3 setup.py install"
#
# For Python 3.x use the corresponding Python executable,
# e.g. "python3 setup.py ..."
#
# (C) 2019 Zhong Huiping <jxwazxzhp@126.com>
#

from setuptools import setup
# from distutils.core import setup

setup(
    name="stmtool",
    description="Python openmv tool for stm32",
    version='0.0.1',
    author="Zhong huiping",
    author_email="jxwazxzhp@126.com",
    url="https://github.com/kabirz/openmv",
    packages=['openmv', 'openmv.entry'],
    license="GPL",
    install_requires=[
        'pyserial',
        'Pillow',
        'pygame',
        'numpy',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Communications',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Terminals :: Openmv',
    ],
    platforms='linux',
    entry_points={
        'console_scripts': [
            'stmflash = openmv.entry.flash:main',
            'stmdevice = openmv.entry.get_devices:main',
            'openmvview = openmv.entry.priview:main',
            'pydfu = openmv.entry.pyduf:main',
            'dfudl = openmv.entry.duf:main',
        ],
    },
)
