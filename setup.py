import os
from setuptools import setup, find_packages

README = os.path.join(os.path.dirname(__file__), 'README.md')

REQUIREMENTS = os.path.join(os.path.dirname(__file__), 'requirements.txt')
REQUIREMENTS = open(REQUIREMENTS, 'r').read().splitlines()

VERSION = os.path.join(os.path.dirname(__file__), 'VERSION')
VERSION = open(VERSION, 'r').read().strip()

setup(
    name='ubernyc',
    version=VERSION,
    description="An exploration of uber pricing in NYC neighborhoods.",
    long_description=README,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    author='Brian Abelson',
    author_email='brianabelson@gmail.com',
    url='http://github.com/abelsonlive/ubernyc',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    install_requires=REQUIREMENTS,
    tests_require=['nose'],
    entry_points={
        'console_scripts': [
            'ubernyc = ubernyc:poll'
        ]
    },
)
