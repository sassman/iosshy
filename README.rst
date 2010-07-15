IOSSHy - SSH tunnel spawner
===========================
IOSSHy provides an easy to use desktop tool to quickly create and destroy SSH tunnels and launch commands based on a preconfigured setup.

Password are stored in the keyring provided by the operating system (ES: gnome's keyring, kde's kwallet, osx keychain, etc...)

.. contents::

Usage
-----
When the program is launched, the main interface is hidden and only the icon in the system tray is shown.
By clicking the tray icon, a configuration dialog will appear which allows to specify the tunnel configurations.

A tunnel configuration consists of a name, the remote port that has to be forwarded locally, the local port (leaving this value to 0 will let IOSSHy choose a free high numbered port), an optional command to execute, and the ssh server details (host, port, and username). The password will be asked when needed.

The command line may contain a special string "{port}" (without quotes) that will be replaced by the local port used for the tunnel, making it possible to write commands like::

	rdesktop localhost:{port}

SSH public key authentication methods are supported through the ssh agents provided by each operating system (putty's pageant is supported).

Example use case
''''''''''''''''
Create a SSH tunnel to a remote host on the MySQL port (3306) and launch a program that uses the tunnel to access the database as if it was installed locally.
When the program terminates the tunnel is automatically closed.

Installation
------------
The application should work reasonably well on all the platforms where the dependencies can be satisfied (Linux, \*BSD, OSX, Windows, ...),
but at this point has only been tested on Linux operating systems and Windows XP 32bit.

Packages
''''''''
The following packages are available:

 * `Windows 32bit installer <http://cloud.github.com/downloads/mtorromeo/iosshy/iosshy-win32-1.2.exe>`_
 * `Arch Linux <http://aur.archlinux.org/packages.php?ID=34495>`_
 * `Source tarball <http://github.com/mtorromeo/iosshy/tarball/v1.2>`_

The code is hosted on `github <http://github.com/mtorromeo/iosshy>`_

Clone command::

	git clone git://github.com/mtorromeo/iosshy.git

Dependencies
''''''''''''
IOSSHy is a **python 2.6** application and it also depends upon the following external libraries:

 * PyKDE4 (Optional for better KDE4 integration)
 * PyQt4 (4.6+)
 * python-paramiko
 * python-keyring

Build instructions
''''''''''''''''''
Before using this applications the Qt forms and icon resources must be compiled.
There is a unix shell script in the root of the distribution package named *build.sh* that takes care of this process::

	cd [SOURCE FOLDER]
	sh build.sh
	chmod 755 bin/iosshy
	bin/iosshy

CHANGELOG
---------

Since version 1.1

 * Called required Random.atfork in tunnel thread, to ensure RNG thread safety
 * Suppressed RandomPool deprecation warning (paramiko should fix this)

LICENSE
-------
Copyright (c) 2010 Massimiliano Torromeo

IOSSHy is free software released under the terms of the BSD license.

See the LICENSE file provided with the source distribution for full details.

Contacts
--------

* Massimiliano Torromeo <massimiliano.torromeo@gmail.com>