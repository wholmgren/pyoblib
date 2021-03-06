# Copyright 2018 SunSpec Alliance

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Taxonomy units."""

import xml.sax

import constants
import taxonomy
import util
import os
import sys


class _TaxonomyUnitsHandler(xml.sax.ContentHandler):
    """Loads Taxonomy Units from the units type registry file."""

    def __init__(self):
        self._units = {}

    def startElement(self, name, attrs):
        if name == "unit":
            for item in attrs.items():
                if item[0] == "id":
                    self._curr = taxonomy.Unit()
                    self._curr.id = item[1]
        elif name == "xs:enumeration":
            for item in attrs.items():
                if item[0] == "value":
                    self._curr.append(item[1])

    def characters(self, content):
        self._content = content

    def endElement(self, name):
        if name == "unitId":
            self._curr.unit_id = self._content
            self._units[self._content] = self._curr
        elif name == "unitName":
            self._curr.unit_name = self._content
        elif name == "nsUnit":
            self._curr.ns_unit = self._content
        elif name == "itemType":
            self._curr.item_type = self._content
        elif name == "itemTypeDate":
            self._curr.item_type_date = util.convert_taxonomy_xsd_date(self._content)
        elif name == "symbol":
            self._curr.symbol = self._content
        elif name == "definition":
            self._curr.definition = self._content
        elif name == "baseStandard":
            self._curr.base_standard = taxonomy.BaseStandard(self._content)
        elif name == "status":
            self._curr.status = taxonomy.UnitStatus(self._content)
        elif name == "versionDate":
            self._curr.version_date = util.convert_taxonomy_xsd_date(self._content)

    def units(self):
        return self._units


class TaxonomyUnits(object):
    """
    Represents Taxonomy Units.

    Represents Taxonomy Units and allows lookup of enumerated values for
    each Taxonomy Unit.
    """

    def __init__(self):
        """Constructor."""
        self._units = self._load_units()

    def _load_units_file(self, fn):
        taxonomy = _TaxonomyUnitsHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(taxonomy)
        if sys.version_info[0] < 3:
            # python 2.x
            with open(fn, 'r') as infile:
                parser.parse(infile)
        else:
            with open(fn, 'r', encoding='utf8') as infile:
                parser.parse(infile)
        return taxonomy.units()

    def _load_units(self):
        pathname = os.path.join(constants.SOLAR_TAXONOMY_DIR, "external")
        filename = "utr.xml"
        units = self._load_units_file(os.path.join(pathname, filename))
        return units

    def get_all_units(self):
        """
        Used to lookup the entire list of units.

        Returns:
             A dict of units with unit_id as primary key.
        """
        return self._units

    def _by_id(self):
        """Return a dict of the form {id: unit_id}"""
        return {self._units[k].id: k for k in self._units.keys()}

    def _by_unit_name(self):
        """Return a dict of the form {unit_name: unit_id}"""
        return {self._units[k].unit_name: k for k in self._units.keys()}

    def is_unit(self, unit_str, attr=None):
        """
        Return True if unit_str is the unit_id, unit_name or id of a unit in
        the taxonomy, False otherwise.

        The search for the unit can be restricted by specifying attr as one
        of 'unit_id', 'unit_name', or 'id'.

        Args:
            unit_str: str
                can be unit_id, unit_name or id
            attr: str, default None
                checks only specified attribute, can be 'unit_id', 'unit_name',
                or 'id'

        Returns:
            boolean

        Raises:
            ValueError if attr is not valid attribute
        """
        if not attr:
            # check for any attribute
            return (unit_str in self._units.keys() or \
                    unit_str in self._by_id().keys() or \
                    unit_str in self._by_unit_name().keys())
        elif attr not in {'unit_id', 'unit_name', 'id'}:
            raise ValueError('{} is not a valid unit attribute, must be one of'
                             '"unit_id", "unit_name" or "id"'
                             .format(attr))
        else:
            if attr=='unit_id':
                return unit_str in self._units.keys()
            elif attr=='unit_name':
                return unit_str in self._by_unit_name().keys()
            elif attr=='id':
                return unit_str in self._by_id().keys()

    def get_unit(self, unit_str, attr=None):
        """
        Returns the unit with unit_id, unit_name or id is given by unit_str.

        The search for the unit can be restricted by specifying attr as one
        of 'unit_id', 'unit_name', or 'id'.

        Args:
            unit_str: str
                can be unit_id, unit_name or id
            attr: str, default None
                checks only specified attribute, can be 'unit_id', 'unit_name',
                or 'id'

        Returns:
            unit: dict

        Raises:
            ValueError if unit_str is not a value for a unit in the taxonomy
        """
        found = False
        if not attr:
            # search by unit_id, unit_name or id
            if self.is_unit(unit_str, attr):
                # find unit_id
                try:
                    unit = self._units[unit_str]
                    found = True
                except:
                    if unit_str in self._by_id():
                        unit_id = self._by_id()[unit_str]
                        unit = self._units[unit_id]
                        found = True
                    elif unit_str in self._by_unit_name():
                        unit_id = self._by_unit_name()[unit_str]
                        unit = self._units[unit_id]
                        found = True
            if not found:
                raise ValueError("{} is not a valid unit_id, unit_name or id"
                                .format(unit_str))
                return None
            else:
                return unit

        elif attr not in {'unit_id', 'unit_name', 'id'}:
            raise ValueError('{} is not a recognized unit attribute'
                             .format(attr))
        else:
            # valid attr, search for unit_str in attr's values
            if attr=='unit_id':
                if unit_str in self._units.keys():
                    unit = self._units[unit_str]
                    found = True
            elif attr=='unit_name':
                if unit_str in self._by_unit_name():
                    unit_id = self._by_unit_name()[unit_str]
                    unit = self._units[unit_id]
                    found = True
            elif attr=='id':
                if unit_str in self._by_id():
                    unit_id = self._by_id()[unit_str]
                    unit = self._units[unit_id]
                    found = True
            if not found:
                raise ValueError("{} is not a valid value for {}"
                                .format(unit_str, attr))
                return None
            else:
                return unit
