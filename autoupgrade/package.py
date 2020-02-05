# -*- coding: utf-8 -*-

import os
import re
import site
import sys
import subprocess
import pkg_resources
import requests

from .exceptions import NoVersionsError, PkgNotFoundError
from subprocess import CalledProcessError
from .utils import ver_to_tuple


class Package(object):
    """
    AutoUpgrade class, holds one package.
    """

    __slots__ = ['__index', 'index', 'pkg', 'verbose']

    def __init__(self, pkg, index=None, verbose=False):
        """
        Args:
            pkg (str): name of package
            index (str): alternative index, if not given default for *pip* will be used. Include
                         full index url, e.g. https://example.com/simple
        """
        self.pkg = pkg
        self.verbose = verbose
        if index:
            self.index = index.rstrip('/')
            self.__index = True
        else:
            self.index = "https://pypi.python.org/simple"
            self.__index = False

    def upgrade_if_needed(self, *args, **kwargs):
        return self.smartupgrade(*args, **kwargs)

    def smartupgrade(self, restart=True, dependencies=True, prerelease=False):
        """
        Upgrade the package if there is a later version available.
        Args:
            restart: restart app if True
            dependencies: update package dependencies if True (see pip --no-deps)
            prerelease: update to pre-release and development versions
        """
        if not self.check():
            if self.verbose:
                print("Package {} already up-to-date!".format(self.pkg))
            return
        if self.verbose:
            print("Upgrading {} ...".format(self.pkg))
        self.upgrade(dependencies, prerelease, force=False)
        if restart:
            self.restart()

    def upgrade(self, dependencies=True, prerelease=False, force=False):
        """
        Upgrade the package unconditionaly
        Args:
            dependencies: update package dependencies if True (see pip --no-deps)
            prerelease: update to pre-release and development versions
            force: reinstall all packages even if they are already up-to-date
        Returns True if pip was sucessful
        """
        pip_args = ['pip3', 'install', self.pkg]

        found = self._get_current() != (-1)
        if found:
            pip_args.append("--upgrade")

        if force:
            pip_args.append(
                "--force-reinstall" if found else "--ignore-installed")

        if not dependencies:
            pip_args.append("--no-deps")

        if prerelease:
            pip_args.append("--pre")

        if self._is_user_installed():
            pip_args.append('--user')

        proxy = os.environ.get('http_proxy')
        if proxy:
            pip_args.extend(['--proxy', proxy])

        if self.__index:
            pip_args.extend(['-i', self.index])

        try:
            subprocess.run(pip_args, check=True)
        except (CalledProcessError) as e:
            print("Errore eseguendo il comando: {}".format(e))
            sys.exit(-1)

    def restart(self):
        """
        Restart application with same args as it was started.
        Does **not** return
        """
        if self.verbose:
            print("Restarting {} {} ...".format(sys.executable, sys.argv))
        os.execl(sys.executable, *([sys.executable] + sys.argv))

    def check(self):
        """
        Check if pkg has a later version
        Returns true if later version exists
        """
        current = self._get_current()
        highest = self._get_highest_version()
        return highest > current

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

    def _get_current(self):
        try:
            current = ver_to_tuple(
                pkg_resources.get_distribution(self.pkg).version)
        except pkg_resources.DistributionNotFound:
            current = (-1,)
        return current

    def _get_highest_version(self):
        url = "{}/{}/".format(self.index, self.pkg)
        r = requests.get(url)
        if r.status_code != 200:
            raise PkgNotFoundError
        pattr = r'>{}-((?:\d+\D*)(?:\.\d+\D*)*)-'.format(self.pkg)
        versions = map(ver_to_tuple,
                       re.findall(pattr, r.text, flags=re.I))
        if not versions:
            raise NoVersionsError
        return max(versions)
