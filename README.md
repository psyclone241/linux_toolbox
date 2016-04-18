linux_toolbox
===========

Linux Toolbox for CTS-IT
-----------------------------

A collection of tools for administering various linux boxen
* ProcessWatch - Watch the processes on a system and record the top X to a sqlite
database for analyzing the system's performance

Installation
------------

* Currently no formal install process, simply setup VirtualEnv or run manually
* Follow these steps to setup your virtualenv
    * `virtualenv venv`
    * `venv/bin/pip install -r requirements.txt`
* Or install manually with `pip install -r requirements.txt`
* Or use `make setup`

Package Contents
----------------

* Nothing is installed at this time,

Usage Instructions
------------------

* To copy the config example, run `make config`
* To install the virtualenv environment, run `make setup`
* Manually run, `python processwatch.py`
* Or, use make, `make watch`

Input data
----------

* No input at this time

Output data
-----------

* A list of the top X processes

Requirements
------------

* Python library 'psutil'
* `pip install psutil`

Contributions
-------------

We welcome contributions to this project. Please fork
and send pull requests with your revisions.
