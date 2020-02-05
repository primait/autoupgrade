# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="autoupgrade-prima",
    version="0.5.1",
    author="Walter Purcaro",
    author_email="vuolter@gmail.com",
    description="Automatic upgrade of PyPI packages",
    long_description=open('README.rst').read(),
    keywords=['autoupgrade', 'pip-upgrade', 'pip'],
    packages=['autoupgrade'],
    include_package_data=True,
    url="https://github.com/primait/autoupgrade",
    download_url="https://github.com/primait/autoupgrade/releases",
    install_requires=['requests'],
    obsoletes=['autoupgrade'],
    license='MIT License',
    zip_safe=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Other Environment",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities"
    ]
)
