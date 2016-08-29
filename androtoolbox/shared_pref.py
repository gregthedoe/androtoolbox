from collections import OrderedDict

import lxml.etree as etree

_types_parsers = {
    'int': int,
    'long': long,
    'boolean': lambda val: val.lower() == 'true',
    'string': unicode
}

_types_names = {
    int: 'int',
    long: 'long',
    bool: 'boolean',
    str: 'string',
    unicode: 'string'
}


def _get_pref_element_value(element):
    value_type = element.tag
    try:
        raw_value = element.attrib['value']
    except KeyError:
        raw_value = element.text or ''
    value_parser = _types_parsers[value_type]
    return value_parser(raw_value)


def _get_pref_element_name(element):
    return element.attrib['name']


def _to_pref_element(name, value, forced_type=None):
    value_type = forced_type or _types_names[type(value)]
    if value_type == 'string':
        element = etree.Element(value_type, name=name)
        element.text = value
        return element
    else:
        return etree.Element(value_type, name=name, value=str(value).lower())


class SharedPref(OrderedDict):
    """
    A collection of shared preferences
    """

    def __init__(self, mapping=None):
        super(SharedPref, self).__init__(mapping or {})

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

    def to_xml(self):
        root = etree.Element('map')
        for name, value in self.iteritems():
            root.append(_to_pref_element(name, value))
        return etree.tostring(root, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def to_file(self, fileobj):
        if isinstance(fileobj, basestring):
            with open(fileobj, 'wb') as f:
                f.write(self.to_xml())
        else:
            fileobj.write(self.to_xml())


def build_shared_pref_path(package, pref_name):
    """
    Build the full path for the shared pref

    :param package: The package name the shred pref belongs to.
    :param pref_name: The shared preference name (xml extension can be ommited)
    """
    if pref_name.endswith('.xml'):
        pref_name = pref_name.rsplit('.')[0]
    return "/data/data/{package}/shared_prefs/{pref_name}.xml".format(package=package, pref_name=pref_name)
