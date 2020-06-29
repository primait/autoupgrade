# -*- coding: utf-8 -*-

import os
import re
import site
import sys
import subprocess
import requests
import pkg_resources


from subprocess import CalledProcessError


class Package(object):
    """
    AutoUpgrade class, holds one package.
    """

    __slots__ = ["pkg", "verbose"]

    def __init__(self, pkg, verbose=False):  # index=None,
        """
        Args:
            pkg (str): name of package
        """
        self.pkg = pkg
        self.verbose = verbose

    def upgrade(self, dependencies=True, prerelease=False, force=False):
        """
        Upgrade the package unconditionaly
        Args:
            dependencies: update package dependencies if True (see pip --no-deps)
            prerelease: update to pre-release and development versions
            force: reinstall all packages even if they are already up-to-date
        Returns True if pip was sucessful
        """
        pip_args = ["pip3", "install", self.pkg, "--upgrade"]

        if force:
            pip_args.append("--force-reinstall")

        if not dependencies:
            pip_args.append("--no-deps")

        if prerelease:
            pip_args.append("--pre")

        if self._is_user_installed():
            pip_args.append("--user")

        proxy = os.environ.get("http_proxy")
        if proxy:
            pip_args.extend(["--proxy", proxy])

        try:
            subprocess.run(pip_args, check=True)
        except (CalledProcessError) as e:
            print(f"Errore eseguendo il comando: {e}")
            sys.exit(-1)

    def restart(self):
        """
        Restart application with same args as it was started.
        Does **not** return
        """
        if self.verbose:
            print(f"Restarting {sys.executable} {sys.argv} ...")
        os.execl(sys.executable, *([sys.executable] + sys.argv))

    def _is_user_installed(self):
        """
        Return True if the package has been installed as an user package
        (pip's `--user` option) or False otherwise.
        """
        installation_path = pkg_resources.get_distribution(self.pkg).location
        try:
            user_site_directory = site.getusersitepackages()
            return installation_path.startswith(user_site_directory)
        except AttributeError:
            # Some versions of virtualenv ship with their own version of the
            # site module without the getusersitepacakges function.
            return False
