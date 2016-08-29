import tempfile

import attr
import lxml.etree as etree
from collections import OrderedDict
from .adb import adb

_types_parsers = {
    'int': int,
    'long': long,
    'boolean': lambda val: val.lower() == 'true',
    'string': unicode,
    'float': float,
}

_types_names = {
    int: 'int',
    long: 'long',
    bool: 'boolean',
    str: 'string',
    unicode: 'string',
    float: 'float'
}


@attr.s
class PrefValue(object):
    value = attr.ib()
    type = attr.ib()


def _get_pref_element_value(element):
    value_type_name = element.tag
    try:
        raw_value = element.attrib['value']
    except KeyError:
        raw_value = element.text or ''
    value_parser = _types_parsers[value_type_name]
    return PrefValue(value_parser(raw_value), value_type_name)


def _get_pref_element_name(element):
    return element.attrib['name']


def _to_pref_element(name, value, forced_type=None):
    value_type = forced_type or value.type
    value = value.value
    if value_type == 'string':
        element = etree.Element(value_type, name=name)
        element.text = value
        return element
    else:
        return etree.Element(value_type, name=name, value=str(value).lower())


class SharedPref(object):
    """
    A collection of shared preferences
    """

    def __init__(self):
        self._prefs = OrderedDict()

    @classmethod
    def from_xml(cls, xml_data):
        mapping = cls()
        root = etree.fromstring(xml_data)
        for pref_element in root.iterchildren():
            name = _get_pref_element_name(pref_element)
            value = _get_pref_element_value(pref_element)
            mapping[name] = value
        return mapping

    @classmethod
    def from_file(cls, fileobj):
        if isinstance(fileobj, basestring):
            with open(fileobj) as f:
                return cls.from_xml(f.read())
        else:
            return cls.from_xml(fileobj.read())

    @classmethod
    def from_device(cls, package, pref_name):
        pref_device_path = build_shared_pref_path(package, pref_name)
        data = adb.shell("cat %s" % pref_device_path, use_su=True)
        return cls.from_xml(data)

    def to_xml(self):
        root = etree.Element('map')
        for name, value in self._prefs.iteritems():
            root.append(_to_pref_element(name, value))
        return etree.tostring(root, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def to_file(self, fileobj):
        xml = self.to_xml()
        if isinstance(fileobj, basestring):
            with open(fileobj, 'wb') as f:
                f.write(xml)
        else:
            fileobj.write(xml)
            fileobj.flush()

    def to_device(self, package, pref_name):
        with tempfile.NamedTemporaryFile() as tmp_shared_file:
            self.to_file(tmp_shared_file)
            pref_device_path = build_shared_pref_path(package, pref_name)
            local_path = tmp_shared_file.name
            remote_tmp_path = "/data/local/tmp/%s" % os.path.basename(local_path)
            adb.push(local_path, remote_tmp_path)
            adb.shell('mv %s %s' % (remote_tmp_path, pref_device_path), use_su=True)

            # We need to fix any permissions mix up
            adb.shell('chmod 0777 %s' % pref_device_path, use_su=True)

    def __setitem__(self, key, value):
        if key in self._prefs:
            self._prefs[key].value = value
        else:
            if not isinstance(value, PrefValue):
                pref_type = _types_names[type(value)]
                value = PrefValue(value, pref_type)
            self._prefs[key] = value

    def __getitem__(self, item):
        return self._prefs[item].value

    def __repr__(self):
        return repr(self._prefs)

    def __str__(self):
        return self.to_xml()

    def update(self, updates):
        for k, v in updates.iteritems():
            self[k] = v


def build_shared_pref_path(package, pref_name):
    """
    Build the full path for the shared pref

    :param package: The package name the shred pref belongs to.
    :param pref_name: The shared preference name (xml extension can be ommited)
    """
    if pref_name.endswith('.xml'):
        pref_name = pref_name.rsplit('.')[0]
    return "/data/data/{package}/shared_prefs/{pref_name}.xml".format(package=package, pref_name=pref_name)
