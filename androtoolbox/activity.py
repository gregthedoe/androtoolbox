import attr
from .adb import adb

_extra_types_to_flags = {
    str: '--es',
    unicode: '--es',
    bool: '--ez',
    int: '--ei',
    long: '--el',
    float: '--ef',
}


@attr.s
class Intent(object):
    action = attr.ib(default=None)
    data_uri = attr.ib(default=None)
    mime_type = attr.ib(default=None)
    category = attr.ib(default=None)
    component = attr.ib(default=None)
    extras = attr.ib(default=dict)
    flags = attr.ib(default=None)
    grant_read_uri_permission = attr.ib(default=False)
    grant_write_uri_permission = attr.ib(default=False)
    debug_log_resolution = attr.ib(default=False)
    exclude_stopped_packages = attr.ib(default=False)
    include_stopped_packages = attr.ib(default=False)

    # activity_brought_to_front = attr.ib(default=False)
    # activity_clear_top = attr.ib(default=False)
    # activity_clear_when_task_reset = attr.ib(default=False)
    # activity_exclude_from_recents = attr.ib(default=False)
    # activity_launched_from_history = attr.ib(default=False)
    # activity_multiple_task = attr.ib(default=False)
    # activity_no_animation = attr.ib(default=False)
    # activity_no_history = attr.ib(default=False)
    # activity_no_user_action = attr.ib(default=False)
    # activity_previous_is_top = attr.ib(default=False)
    # activity_reorder_to_front = attr.ib(default=False)
    # activity_reset_task_if_needed = attr.ib(default=False)
    # activity_single_top = attr.ib(default=False)
    # activity_clear_task = attr.ib(default=False)
    # activity_task_on_home = attr.ib(default=False)
    # receiver_registered_only = attr.ib(default=False)
    # receiver_replace_pending = attr.ib(default=False)

    def to_cmdline(self):
        cmd = []
        if self.action:
            cmd.extend(['-a', self.action])
        if self.data_uri:
            cmd.extend(['-d', self.data_uri])
        if self.mime_type:
            cmd.extend(['-d', self.mime_type])
        if self.category:
            cmd.extend(['-c', self.category])
        if self.component:
            cmd.extend(['-n', self.component])
        cmd.extend(self._extras_to_cmdline())
        if self.grant_read_uri_permission:
            cmd.append('--grant-read-uri-permission')
        if self.grant_write_uri_permission:
            cmd.append('--grant-write-uri-permission')
        if self.debug_log_resolution:
            cmd.append('--debug-log-resolution')
        if self.exclude_stopped_packages:
            cmd.append('--exclude-stopped-packages')
        if self.include_stopped_packages:
            cmd.append('--include-stopped-packages')
        return cmd

    def _extras_to_cmdline(self):
        cmd = []
        for k, v in self.extras:
            cmd.extend(self._extra_to_cmdline(k, v))
        return cmd

    def _extra_to_cmdline(self, key, value):
        # null extra
        if not value:
            return ['--esn', key]
        value_type = type(value)
        return [_extra_types_to_flags[value_type], str(value)]


def start_activity(intent, enable_debugging=False, wait_for_launch=False, repeat=0,
                   force_stop=False, user_id=None, use_su=False):
    cmd = ['am', 'start']
    if enable_debugging:
        cmd.append('-D')
    if wait_for_launch:
        cmd.append('-W')
    if repeat:
        cmd.extend(['-R', str(repeat)])
    if force_stop:
        cmd.append('-S')
    if user_id is not None:
        cmd.extend(['--user', str(user_id)])

    cmd.extend(intent.to_cmdline())
    return adb.shell(' '.join(cmd), use_su=use_su)


def start_service(intent, user_id=None, use_su=False):
    cmd = ['am', 'startservice']
    if user_id is not None:
        cmd.extend(['--user', str(user_id)])
    cmd.extend(intent.to_cmdline())

    return adb.shell(' '.join(cmd), use_su=use_su)


def force_stop(package, use_su=False):
    return adb.shell('am force-stop %s' % package, use_su=use_su)


def kill_package(package, user_id=None, use_su=False):
    cmd = ['am', 'kill']
    if user_id is not None:
        cmd.extend(['--user', str(user_id)])
    cmd.append(package)
    return adb.shell(' '.join(cmd), use_su=use_su)


def kill_all_background(use_su=False):
    return adb.shell('am kill-all', use_su=use_su)


def send_broadcast(intent, user_id=None, use_su=False):
    cmd = ['am', 'broadcast']
    if user_id is not None:
        cmd.extend(['--user', str(user_id)])
    cmd.extend(intent.to_cmdline())
    return adb.shell(' '.join(cmd), use_su=use_su)