from .adb import adb

_LOG_TAG_PROPERTY = 'log.tag.{tag}'

LOG_LEVELS = ('VERBOSE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'ASSERT')


def is_valid_log_level(level):
    return level.upper() in LOG_LEVELS


def set_loggable_level_for_tag(tag, level='VERBOSE'):
    """
    Set the minimum loggable level for a tag.

    :param tag: TAG name
    :param level: Log level.
    """
    level = level.upper()
    if not is_valid_log_level(level):
        raise ValueError("Unknown log level %s" % level)
    return adb.set_property(_LOG_TAG_PROPERTY.format(tag=tag), level)


def set_loggable_level_for_tags(tags, default_level='VERBOSE'):
    """
    Set the minimum log level for a set of tags.

    :param tags: A mapping of tags and their minimum loggable level.
    :param default_level: If `tags` is a list use this level as the default.
    """
    try:
        for tag, level in tags.iteritems():
            set_loggable_level_for_tag(tag, level)
    except AttributeError:
        for tag in tags:
            set_loggable_level_for_tag(tag, default_level)
