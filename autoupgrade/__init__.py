# -*- coding: utf-8 -*-

import os
import re
import semver
import site
import sys
import subprocess
import pkg_resources

from subprocess import CalledProcessError


class Package(object):
    """
    AutoUpgrade class, holds one package.
    """

    __slots__ = ["pkg", "verbose", "regex", "version_before"]

    def __init__(self, pkg, verbose=False):  # index=None,
        """
        Args:
            pkg (str): name of package
        """
        self.pkg = pkg
        self.verbose = verbose
        self.regex = r"Version\: ([0-9\.]+)"
        self.version_before = self._get_installed_version()

    def upgrade(self, dependencies=True, prerelease=False, force=False):
        """
        Upgrade the package unconditionaly
        Args:
            dependencies: update package dependencies if True (see pip --no-deps)
            prerelease: update to pre-release and development versions
            force: reinstall all packages even if they are already up-to-date
        Returns True if pip was sucessful
        """
        restart = False

        pip_args = ["pip3", "install", self.pkg, "--upgrade"]

        if not self.verbose:
            pip_args.append("--quiet")

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
            version_after = self._get_installed_version()

            if semver.compare(version_after, self.version_before) == 1:
                restart = True

        except (CalledProcessError) as e:
            print(f"Errore eseguendo il comando: {e}")
            sys.exit(-1)

        if restart:
            self.restart()

    def restart(self):
        """
        Restart application with same args as it was started.
        Does **not** return
        """
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

    def _get_installed_version(self):
        try:
            output = subprocess.run(
                ["pip3", "show", self.pkg], check=True, stdout=subprocess.PIPE
            ).stdout.decode("utf-8")

            return re.search(self.regex, output).group(1)
        except (CalledProcessError) as e:
            print(f"Errore eseguendo il comando: {e}")
            sys.exit(-1)
