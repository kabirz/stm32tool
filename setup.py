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
    description="Python stm32 tools",
    version='0.0.5',
    author="Zhong huiping",
    author_email="jxwazxzhp@126.com",
    url="https://github.com/kabirz/stm32tool",
    packages=['stm32tool', 'stm32tool.entry'],
    license="MIT",
    install_requires=[
        'pyserial',
        'Pillow',
        'pygame',
        'numpy',
        'progressbar',
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
        'Topic :: Terminals :: Stm32 tool',
    ],
    platforms='linux',
    entry_points={
        'console_scripts': [
            'stmflash = stm32tool.entry.flash:main',
            'stmdevice = stm32tool.entry.get_devices:main',
            'openmvview = stm32tool.entry.priview:main',
            'pydfu = stm32tool.entry.pydfu:main',
            'mkdfu = stm32tool.entry.dfu:main',
            'stm32isp = stm32tool.isp:main',
        ],
    },
)
