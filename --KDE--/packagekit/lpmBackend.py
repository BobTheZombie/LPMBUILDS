#!/usr/bin/python3
"""PackageKit spawn helper for LPM Linux.

All mutations delegate to LPM's own SAT transaction engine.  The read side
uses LPM's published repository index and read-only installed SQLite database.
No shell, no sudo, no bypass of signature checks, force installs or fallback.
"""
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import stat
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlsplit

from packagekit.backend import PackageKitBaseBackend, get_package_id, split_package_id
from packagekit.enums import *

STATE = Path(os.environ.get('LPM_STATE_DIR', '/var/lib/lpm'))
VALID_NAME = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9+_.-]*$')
VERSION = re.compile(r'^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:[-+~].*)?$')


def version_key(value):
    # Same three-component version comparison as LPM's parse_semver().
    m = VERSION.match(str(value))
    return tuple(int(x or 0) for x in m.groups()) if m else (0, 0, 0)


def safe(text):
    return str(text or '').replace('\t', ' ').replace('\r', ' ').replace('\n', ' ')


def installed():
    db = STATE / 'state.db'
    if not db.is_file():
        return {}
    con = sqlite3.connect(f'file:{db}?mode=ro', uri=True, timeout=15)
    try:
        rows = con.execute('SELECT name,version,release,arch,manifest FROM installed').fetchall()
        return {r[0]: {'name': r[0], 'version': r[1], 'release': r[2],
                       'arch': r[3], 'manifest': r[4], 'repo': 'installed'} for r in rows}
    finally:
        con.close()


def catalog():
    repos_file = STATE / 'repos.json'
    repos = json.loads(repos_file.read_text()) if repos_file.is_file() else []
    result = {}
    for repo in sorted(repos, key=lambda x: int(x.get('priority', 10)), reverse=True):
        url = repo.get('url', '').rstrip('/') + '/index.json'
        parsed = urlsplit(url)
        if parsed.scheme not in ('https', 'file'):
            continue
        try:
            with urlopen(url, timeout=15) as fd:
                data = json.loads(fd.read(32 * 1024 * 1024))
            for pkg in data.get('packages', []):
                name = pkg.get('name', '')
                arch = pkg.get('arch', 'any')
                if (not VALID_NAME.fullmatch(name) or arch not in ('any', 'noarch', os.uname().machine)):
                    continue
                item = dict(pkg)
                item['repo'] = repo['name']
                result[name] = item
        except (OSError, ValueError, KeyError) as err:
            print(f'LPM repository unavailable {safe(repo.get("name"))}: {safe(err)}', file=sys.stderr)
    return result



def recipe_checkout():
    """Use only an administrator-owned Git recipe checkout for source builds."""
    setting = '/var/cache/lpm/git/packages'
    config = Path('/etc/lpm/lpm.conf')
    if config.is_file():
        for line in config.read_text(errors='replace').splitlines():
            if line.startswith('LPMBUILD_RECIPE_LOCAL_PATH='):
                setting = line.partition('=')[2].strip()
    root = Path(setting)
    try:
        info = root.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            return None
        if not (root / '.git').is_dir():
            return None
    except OSError:
        return None
    return root


def source_catalog():
    """Index source recipes without sourcing/evaluating their Bash contents.

    Source builds are explicitly selected as packages with origin 'lpm-source'.
    Never accept untrusted paths in the PackageKit request; only the trusted
    recipe checkout is eligible for high-privilege build execution.
    """
    root = recipe_checkout()
    if root is None:
        return {}
    result = {}
    for file in root.rglob('*.lpmbuild'):
        try:
            relative = file.relative_to(root)
            if len(relative.parts) not in (2, 3):
                continue
            if file.stem != file.parent.name or not VALID_NAME.fullmatch(file.stem):
                continue
            info = file.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
                continue
            # Source files are data here, not executable code.
            content = file.read_text(errors='replace')[:16384]
            fields = {}
            for key in ('NAME', 'VERSION', 'RELEASE', 'SUMMARY'):
                match = re.search(r'^' + key + r'=(["\'])([^"\'\n]*)\1\s*$', content, re.M)
                if match:
                    fields[key] = match.group(2)
            if fields.get('NAME') != file.stem or not VERSION.fullmatch(fields.get('VERSION', '')):
                continue
            result[file.stem] = {
                'name': file.stem, 'version': fields['VERSION'],
                'release': fields.get('RELEASE') or '1',
                'arch': os.uname().machine, 'repo': 'lpm-source',
                'recipe': str(file), 'summary': fields.get('SUMMARY') or file.stem,
            }
        except (OSError, ValueError):
            continue
    return result


def available_packages():
    # Prefer binary packages; source builds only for names absent in indexes.
    return source_catalog() | catalog()


def clean_transaction_flags(flags):
    """Fail closed on options not implemented by the LPM bridge."""
    return not any(flag in flags for flag in
                   ('simulate', 'only-download', 'only-trusted=false', 'allow-downgrade',
                    'just-reinstall'))


def run_lpm(argv, *, input_newlines=False, timeout=3600):
    """Use a bounded log file and no shell. No untrusted environment overrides."""
    env = os.environ.copy()
    env['LPM_NO_VERIFY'] = '0'
    env.pop('LPMBUILD_RECIPE_GIT_URL', None)
    with tempfile.TemporaryFile(mode='w+b') as logfile:
        with subprocess.Popen(argv, stdin=subprocess.PIPE if input_newlines else subprocess.DEVNULL,
                              stdout=logfile, stderr=subprocess.STDOUT, env=env) as proc:
            try:
                # LPM buildpkg asks for each dependency install, even with
                # --install-default=y; empty answers select that explicit default.
                if input_newlines:
                    proc.communicate(input=b'\n' * 8192, timeout=timeout)
                else:
                    proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
                raise
            status = proc.returncode
        logfile.seek(0, os.SEEK_END)
        size = logfile.tell()
        logfile.seek(max(0, size - 4096))
        message = logfile.read().decode('utf-8', errors='replace')
    return status, message

def pkgid(pkg, installed_state=False):
    version = f"{pkg.get('version','0')}-{pkg.get('release','1')}"
    arch = pkg.get('arch', 'noarch')
    if arch == 'any':
        arch = 'noarch'
    return get_package_id(pkg['name'], version, arch, 'installed' if installed_state else pkg.get('repo', 'lpm'))


def names_from_ids(ids, available, inst, *, must_installed=False):
    names = []
    for value in ids:
        parts = split_package_id(value)
        if len(parts) != 4 or not VALID_NAME.fullmatch(parts[0]):
            raise ValueError('Malformed PackageKit ID')
        name, version, arch, origin = parts
        item = inst.get(name) if must_installed else available.get(name)
        if not item:
            raise ValueError(f'Package unavailable: {name}')
        if pkgid(item, must_installed) != value:
            raise ValueError(f'Stale or mismatched package ID: {name}')
        names.append(name)
    return list(dict.fromkeys(names))


class LPMBackend(PackageKitBaseBackend):
    def __init__(self, argv):
        super().__init__(argv)

    def _emit(self, item, is_installed):
        self.package(pkgid(item, is_installed), INFO_INSTALLED if is_installed else INFO_AVAILABLE,
                     safe(item.get('summary') or item['name']))

    def _packages(self, filters, predicate=lambda x: True):
        self.status(STATUS_QUERY)
        inst = installed()
        remote = available_packages()
        want_i = 'installed' in filters
        want_a = 'not-installed' in filters
        for name in sorted(set(remote) | set(inst)):
            is_installed = name in inst
            if want_i and not is_installed:
                continue
            if want_a and is_installed:
                continue
            item = dict((inst if is_installed else remote)[name])
            if is_installed and name in remote:
                item.update(summary=remote[name].get('summary',''), url=remote[name].get('url',''))
            if predicate(item):
                self._emit(item, is_installed)

    def get_packages(self, filters):
        self._packages(filters)

    def search_name(self, filters, terms):
        needles = [t.lower() for t in terms if t]
        self._packages(filters, lambda x: all(n in x['name'].lower() for n in needles))

    def search_details(self, filters, terms):
        needles = [t.lower() for t in terms if t]
        self._packages(filters, lambda x: all(n in (x['name']+' '+x.get('summary','')).lower() for n in needles))

    def resolve(self, filters, values):
        names = set(v.split(';')[0] for v in values)
        self._packages(filters, lambda x: x['name'] in names)

    def get_details(self, ids):
        self.status(STATUS_QUERY)
        inst = installed()
        remote = available_packages()
        for value in ids:
            parts = split_package_id(value)
            if len(parts) != 4:
                self.error(ERROR_PACKAGE_NOT_FOUND, 'Bad package ID', exit=False)
                continue
            name = parts[0]
            item = inst.get(name) if parts[3] == 'installed' else remote.get(name)
            if not item or pkgid(item, parts[3] == 'installed') != value:
                self.error(ERROR_PACKAGE_NOT_FOUND, 'Unknown or stale package', exit=False)
                continue
            meta = remote.get(name, {}) | item
            summary = safe(meta.get('summary', name))
            self.details(value, summary, safe(meta.get('license', 'unknown')),
                         GROUP_UNKNOWN, summary, safe(meta.get('url', '')), meta.get('size') or None)

    def get_updates(self, filters):
        self.status(STATUS_QUERY)
        inst = installed()
        remote = catalog()
        for name, current in sorted(inst.items()):
            candidate = remote.get(name)
            if candidate and version_key(candidate['version']) > version_key(current['version']):
                self.package(pkgid(candidate), INFO_NORMAL, safe(candidate.get('summary', name)))

    def _run_transaction(self, argv, *, interactive_build=False, timeout=3600):
        self.percentage(0)
        try:
            code, message = run_lpm(argv, input_newlines=interactive_build, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired) as err:
            self.error(ERROR_INTERNAL_ERROR, 'LPM operation failed: ' + safe(err))
            return False
        if code:
            self.error(ERROR_INTERNAL_ERROR,
                       f'LPM returned {code}: {safe(message[-1200:])}')
            return False
        self.percentage(100)
        return True

    def _transaction(self, subcommand, ids, *, require_installed=False):
        available = available_packages() if not require_installed else catalog()
        inst = installed()
        try:
            names = names_from_ids(ids, available, inst, must_installed=require_installed)
        except ValueError as err:
            self.error(ERROR_PACKAGE_NOT_FOUND, safe(err))
            return
        if not names:
            return
        self.status({'install': STATUS_INSTALL, 'removepkg': STATUS_REMOVE,
                     'upgrade': STATUS_UPDATE}[subcommand])
        if subcommand == 'install':
            binaries = [name for name in names if available[name].get('repo') != 'lpm-source']
            sources = [name for name in names if available[name].get('repo') == 'lpm-source']
            if binaries and not self._run_transaction(['/usr/bin/lpm', 'install', *binaries]):
                return
            for name in sources:
                # Re-resolve from the admin checkout at transaction time to
                # avoid passing arbitrary source paths from the PackageKit UI.
                item = source_catalog().get(name)
                if not item or item != available[name]:
                    self.error(ERROR_PACKAGE_NOT_FOUND, 'Source recipe changed during transaction')
                    return
                if not self._run_transaction(
                    ['/usr/bin/lpm', 'buildpkg', item['recipe'], '--install-default', 'y',
                     '--outdir', '/var/lib/lpm/pk-builds'],
                    interactive_build=True, timeout=14400):
                    return
        else:
            self._run_transaction(['/usr/bin/lpm', subcommand, *names])

    def install_packages(self, transaction_flags, ids):
        if not clean_transaction_flags(transaction_flags):
            self.error(ERROR_NOT_SUPPORTED, 'Unsupported transaction flags')
            return
        self._transaction('install', ids)

    def install_files(self, transaction_flags, files):
        """PackageKit InstallFiles -> LPM installpkg --verify for signed .zst."""
        if not clean_transaction_flags(transaction_flags):
            self.error(ERROR_NOT_SUPPORTED, 'Unsupported transaction flags')
            return
        checked = []
        for name in files:
            path = Path(name)
            if not path.is_absolute() or path.suffix != '.zst' or not path.is_file():
                self.error(ERROR_NOT_SUPPORTED, 'Only absolute local .zst packages supported')
                return
            if not Path(str(path) + '.sig').is_file():
                self.error(ERROR_NOT_SUPPORTED, 'Signed .zst package requires adjacent .sig file')
                return
            checked.append(str(path))
        if checked:
            self.status(STATUS_INSTALL)
            self._run_transaction(['/usr/bin/lpm', 'installpkg', '--verify', *checked])

    def remove_packages(self, transaction_flags, ids, allowdep, autoremove):
        if allowdep or autoremove or not clean_transaction_flags(transaction_flags):
            self.error(ERROR_NOT_SUPPORTED, 'Dependency auto-removal/simulation not implemented')
            return
        self._transaction('removepkg', ids, require_installed=True)

    def update_packages(self, transaction_flags, ids):
        if not clean_transaction_flags(transaction_flags):
            self.error(ERROR_NOT_SUPPORTED, 'Unsupported update transaction flags')
            return
        # Upgrades only work for binary packages in a registered LPM repository.
        self._transaction('upgrade', ids)

    def buildpkg(self, package_name):
        """LPM extension: source-build a trusted recipe and install result."""
        item = source_catalog().get(package_name)
        if item is None:
            self.error(ERROR_PACKAGE_NOT_FOUND, 'Recipe unavailable or untrusted')
            return
        self.status(STATUS_INSTALL)
        self._run_transaction(
            ['/usr/bin/lpm', 'buildpkg', item['recipe'], '--install-default', 'y',
             '--outdir', '/var/lib/lpm/pk-builds'],
            interactive_build=True, timeout=14400)

    def refresh_cache(self, force):
        # LPM publishes catalog through repos.json indexes, not PackageKit's cache.
        # Querying the catalog verifies index accessibility.
        self.status(STATUS_REFRESH_CACHE)
        catalog()
        source_catalog()
        self.percentage(100)


if __name__ == '__main__':
    # Source builds cannot be a standard PackageKit role. Offer an explicitly
    # privileged LPM extension for administrators, alongside PackageKit's
    # ordinary InstallPackages role for trusted source entries.
    if len(sys.argv) == 3 and sys.argv[1] == '--lpm-buildpkg':
        if os.geteuid() != 0:
            raise SystemExit('buildpkg extension requires root / explicit authorization')
        if not VALID_NAME.fullmatch(sys.argv[2]):
            raise SystemExit('Invalid package name')
        LPMBackend([]).buildpkg(sys.argv[2])
    else:
        LPMBackend(sys.argv[1:]).dispatcher(sys.argv[1:])
