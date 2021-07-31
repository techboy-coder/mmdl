from setuptools import setup, find_packages
import codecs
import os
with open('requirements.txt') as f:
    required = f.read().splitlines()

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.1'
DESCRIPTION = 'MDL [Music Downloader] - A tool to easily download music.'
LONG_DESCRIPTION = 'Music Downloading Cli Tool. Downloads audio and metadata from YouTube.'

# Setting up
setup(
    name="mdl",
    version=VERSION,
    author="techboy-coder",
    # author_email="",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=[],
    install_requires=required,
    keywords=['python', 'audio', 'download', 'youtube', 'cli', 'tool'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9"
        "Topic :: Multimedia :: Sound/Audio"
    ]
)