import attr
import re
from .adb import adb


def _null_to_none(value):
    if value == 'null':
        return None
    return value


_DEFAULT_DEVICE_TMP_STORAGE = '/data/local/tmp'
_CURRENT_DIR = '.'


@attr.s
class PackageInstallInfo(object):
    _PACKAGE_LINE_INFO_RE = re.compile("package:(?P<file_path>.+)=(?P<package>[\w\.]+)\s+"
                                       "installer=(?P<installer>[\w\.]+)")
    name = attr.ib()
    file_path = attr.ib()
    installer = attr.ib()

    @classmethod
    def parse_from_line(cls, info_line):
        try:
            file_path, name, installer = PackageInstallInfo._PACKAGE_LINE_INFO_RE.findall(info_line)[0]
            _null_to_none(installer)
            return cls(name, file_path, installer)
        except IndexError:
            print info_line


@attr.s
class PermissionInfo(object):
    name = attr.ib()
    package = attr.ib()
    label = attr.ib()
    description = attr.ib()
    protection_level = attr.ib()

    @classmethod
    def parse_from_raw(cls, data):
        # The order of data is (permission, package, label, description, protectionLevel)
        permission, package, label, description, protection_level = (line.strip().split(":", 1)[1] for line in
                                                                     data.splitlines())
        label = _null_to_none(label)
        description = _null_to_none(description)
        return cls(permission, package, label, description, protection_level)


def list_packages(filter=None, only_disabled=False, only_enabled=False, only_system=False,
                  only_third_party=False, include_uninstalled=False):
    """
    Get device's packages

    :param filter: The package name must contain the filter text
    :param only_disabled: Return only disabled packages
    :param only_enabled: Return only enabled packages
    :param only_system: Return only system packages
    :param only_third_party: Return only third party packages
    :param include_uninstalled: Include uninstalled packages as well
    :return: A list of packages based on the given filter text and flags
    :rtype: list(PackageInstallInfo)
    """
    cmd = ['pm', 'list', 'packages', '-f', '-i']
    if only_disabled:
        cmd.append('-d')
    if only_enabled:
        cmd.append('-e')
    if only_system:
        cmd.append('-s')
    if only_third_party:
        cmd.append('-3')
    if filter:
        cmd.append(filter)

    raw_packages_info = adb.shell(' '.join(cmd))
    return [PackageInstallInfo.parse_from_line(info_line) for info_line in raw_packages_info.splitlines()]


def list_features():
    """
    Gets all features of the system.
    """
    return [line.split(':', 1)[1] for line in adb.shell('pm list features').splitlines()]


def list_permission_groups():
    """
    Gets all known permission groups.
    """
    return [line.split(':', 1)[1] for line in adb.shell('pm list permission-groups').strip().splitlines()]


def list_permissions(group=None):
    """
    Get all known permissions, optionally only those in ``group``

    :param group: Return only permissions within the group
    """
    cmd = "pm list permissions -f"
    permissions = []
    if group:
        cmd = "%s %s" % (cmd, group)
    raw_data = adb.shell(cmd)
    data_start = raw_data.find('+')
    if data_start < 0:
        return []
    data = raw_data[data_start + 1:]
    next_permission_start = data.find('+')
    while next_permission_start >= 0:
        permission_data = data[:next_permission_start]
        # print ','.join(permission_data.splitlines())
        permissions.append(PermissionInfo.parse_from_raw(permission_data))
        data = data[next_permission_start + 1:]
        next_permission_start = data.find('+')
    if data:
        permissions.append(PermissionInfo.parse_from_raw(data))
    return permissions


def disable_package(name, use_su=False):
    """
    Disable the given package or component.

    :param name: The package name or component (written as "package/class").
    :param use_su: Do it with SU.
    """
    adb.shell('pm disable %s' % name)


def enable_package(name, use_su=False):
    """
    Enable the given package or component.

    :param name: The package name or component (written as "package/class").
    :param use_su: Do it with SU.
    """
    adb.shell('pm enable %s' % name, use_su=use_su)


def clear_data(package):
    """
    Deletes all data associated with a package.

    :param package: The package's name
    :return: True if successful
    """
    return adb.shell('pm clear %s' % package).strip() == 'Success'


def pull_data(package, device_tmp_storage=_DEFAULT_DEVICE_TMP_STORAGE, output_path=_CURRENT_DIR):
    """
    Pull packages data dir.

    note: Uses su to access package's data dir.

    :param package: The package's name
    :param device_tmp_storage: Device storage to copy the data to
    :param output_path: Local path to copy data into.
    """
    tmp_storage_path = "%s/%s" % (device_tmp_storage, package)
    package_path = '/data/data/%s' % package
    adb.shell('rm -rf %s' % tmp_storage_path)
    adb.shell('cp -r %s %s' % (package_path, device_tmp_storage), use_su=True)
    adb.shell('chmod -R 0777 %s' % tmp_storage_path, use_su=True)
    adb.pull(tmp_storage_path, output_path)
    adb.shell('rm -rf %s' % tmp_storage_path)
