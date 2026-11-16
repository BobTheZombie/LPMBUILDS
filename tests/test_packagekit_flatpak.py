"""Regression tests for LPM PackageKit's explicit Flatpak namespace.

No installed PackageKit or Flatpak daemon is needed: the helper's PackageKit
protocol bindings are replaced with narrowly scoped stubs, and only commands
to the LPM subprocess facade are asserted.
"""
from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest import mock


HELPER = Path(__file__).resolve().parents[1] / "--KDE--/packagekit/lpmBackend.py"


class FakePackageKitBackend:
    def __init__(self, argv):
        self.packages = []
        self.errors = []
        self.statuses = []
        self.percentages = []
        self.details_results = []

    def status(self, value):
        self.statuses.append(value)

    def package(self, *args):
        self.packages.append(args)

    def percentage(self, value):
        self.percentages.append(value)

    def error(self, *args, **kwargs):
        self.errors.append((args, kwargs))

    def details(self, *args):
        self.details_results.append(args)


def load_helper():
    pkg = types.ModuleType("packagekit")
    pkg.__path__ = []
    backend = types.ModuleType("packagekit.backend")
    enums = types.ModuleType("packagekit.enums")
    backend.PackageKitBaseBackend = FakePackageKitBackend
    backend.get_package_id = lambda *parts: ";".join(parts)
    backend.split_package_id = lambda value: value.split(";")
    constants = [
        "INFO_INSTALLED", "INFO_AVAILABLE", "INFO_NORMAL", "STATUS_QUERY",
        "STATUS_INSTALL", "STATUS_REMOVE", "STATUS_UPDATE", "STATUS_REFRESH_CACHE",
        "ERROR_PACKAGE_NOT_FOUND", "ERROR_NOT_SUPPORTED", "ERROR_INTERNAL_ERROR",
        "GROUP_UNKNOWN",
    ]
    for constant in constants:
        setattr(enums, constant, constant)
    enums.__all__ = constants
    with mock.patch.dict(sys.modules, {
        "packagekit": pkg,
        "packagekit.backend": backend,
        "packagekit.enums": enums,
    }):
        spec = importlib.util.spec_from_file_location("lpm_pk_helper_under_test", HELPER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class PackageKitFlatpakTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_helper()

    def setUp(self):
        self.m = self.module
        self.backend = self.m.LPMBackend([])

    def test_flatpak_namespaced_resolve_does_not_read_native_catalog(self):
        def status(app, *, installed_only=False):
            return not installed_only
        with mock.patch.object(self.m, "flatpak_status", side_effect=status), \
             mock.patch.object(self.m, "available_packages", side_effect=AssertionError("native catalog accessed")):
            self.backend.resolve([], ["flatpak:org.mozilla.firefox"])
        self.assertEqual(self.backend.packages, [
            (self.m.flatpak_pkgid("org.mozilla.firefox"), "INFO_AVAILABLE",
             "Flathub Flatpak application")
        ])

    def test_install_routes_to_lpm_flatpak(self):
        ref = self.m.flatpak_pkgid("org.mozilla.firefox")
        with mock.patch.object(self.m, "flatpak_status", return_value=True), \
             mock.patch.object(self.m, "run_lpm", return_value=(0, "")) as command, \
             mock.patch.object(self.m, "available_packages", side_effect=AssertionError("native catalog accessed")):
            self.backend.install_packages([], [ref])
        self.assertEqual(command.call_args.args[0],
                         ["/usr/bin/lpm", "flatpak", "install", "--system",
                          "--yes", "org.mozilla.firefox"])
        self.assertEqual(self.backend.percentages, [0, 100])
        self.assertEqual(self.backend.errors, [])

    def test_remove_and_update_route_to_lpm_flatpak(self):
        ref = self.m.flatpak_pkgid("org.kde.krita", installed_state=True)
        with mock.patch.object(self.m, "flatpak_status", return_value=True), \
             mock.patch.object(self.m, "run_lpm", return_value=(0, "")) as command:
            self.backend.remove_packages([], [ref], False, False)
            self.assertEqual(command.call_args.args[0],
                             ["/usr/bin/lpm", "flatpak", "remove", "--system",
                              "--yes", "org.kde.krita"])
            self.backend.update_packages([], [ref])
            self.assertEqual(command.call_args.args[0],
                             ["/usr/bin/lpm", "flatpak", "update", "--system",
                              "--yes", "org.kde.krita"])

    def test_native_packages_preserved(self):
        pkg = {"name": "dolphin", "version": "26.08.2", "release": "1",
               "arch": "x86_64", "repo": "official"}
        ref = self.m.pkgid(pkg)
        with mock.patch.object(self.m, "available_packages", return_value={"dolphin": pkg}), \
             mock.patch.object(self.m, "installed", return_value={}), \
             mock.patch.object(self.m, "run_lpm", return_value=(0, "")) as command, \
             mock.patch.object(self.m, "flatpak_status", side_effect=AssertionError("Flatpak probed")):
            self.backend.install_packages([], [ref])
        self.assertEqual(command.call_args.args[0], ["/usr/bin/lpm", "install", "dolphin"])

    def test_mixed_ids_fail_closed(self):
        flatpak_id = self.m.flatpak_pkgid("org.mozilla.firefox")
        with mock.patch.object(self.m, "run_lpm") as command:
            self.backend.install_packages([], [flatpak_id, "dolphin;1;x86_64;official"])
        self.assertFalse(command.called)
        self.assertTrue(self.backend.errors)

    def test_spoofed_origin_and_invalid_app_are_rejected(self):
        for ref in [
            "flatpak:org.mozilla.firefox;0;noarch;official",
            "flatpak:org.mozilla.firefox;0;noarch;installed",
            "flatpak:org.mozilla.firefox;1;noarch;flathub",
            "flatpak:../evil;0;noarch;flathub",
            "flatpak:org.foo;rm;0;noarch;flathub",
        ]:
            with self.subTest(ref=ref), mock.patch.object(self.m, "run_lpm") as command:
                self.backend.install_packages([], [ref])
                self.assertFalse(command.called)
                self.assertTrue(self.backend.errors)

    def test_unavailable_flatpak_is_not_installed(self):
        with mock.patch.object(self.m, "flatpak_status", return_value=False), \
             mock.patch.object(self.m, "run_lpm") as command:
            self.backend.install_packages([], [self.m.flatpak_pkgid("org.kde.krita")])
        self.assertFalse(command.called)
        self.assertTrue(self.backend.errors)

    def test_flatpak_probe_is_read_only_and_bounded(self):
        with mock.patch.object(self.m.subprocess, "run",
                               return_value=types.SimpleNamespace(returncode=0)) as runner:
            self.assertTrue(self.m.flatpak_status("org.mozilla.firefox"))
        runner.assert_called_once_with(
            ["/usr/bin/flatpak", "remote-info", "--system", "flathub",
             "org.mozilla.firefox"],
            stdin=self.m.subprocess.DEVNULL,
            stdout=self.m.subprocess.DEVNULL,
            stderr=self.m.subprocess.DEVNULL,
            check=False, timeout=30,
        )

    def test_installed_probe_rejects_non_flathub_origin(self):
        with mock.patch.object(self.m.subprocess, "run",
                               return_value=types.SimpleNamespace(returncode=0, stdout=b"other\\n")) as runner:
            self.assertFalse(self.m.flatpak_status("org.mozilla.firefox", installed_only=True))
        self.assertEqual(runner.call_args.args[0],
                         ["/usr/bin/flatpak", "info", "--system", "--show-origin",
                          "org.mozilla.firefox"])
        self.assertEqual(runner.call_args.kwargs["stdout"], self.m.subprocess.PIPE)
        with mock.patch.object(self.m.subprocess, "run",
                               return_value=types.SimpleNamespace(returncode=0, stdout=b"flathub\\n")):
            self.assertTrue(self.m.flatpak_status("org.mozilla.firefox", installed_only=True))

    def test_unsupported_flags_rejected(self):
        with mock.patch.object(self.m, "run_lpm") as command:
            self.backend.install_packages(["simulate"], [self.m.flatpak_pkgid("org.kde.krita")])
        self.assertFalse(command.called)
        self.assertTrue(self.backend.errors)


if __name__ == "__main__":
    unittest.main()
