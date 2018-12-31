"""Miscellaneous taxonomy functions."""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import xml.sax

import constants


#
# Note: All miscellaneous taxonomy files are covered except for solar-ref-roles which has only one
# entry # (which happens to have the value "standard").  This file will not be covered 
# programmatically in the initial release of pyoblib.
#


class _TaxonomyNumericHandler(xml.sax.ContentHandler):
    """Loads Taxonomy Numeric Types from the numeric us xsd file."""

    def __init__(self):
        """Numeric handler constructor."""
        self._numeric_types = []

    def startElement(self, name, attrs):
        if name == "complexType":
            for item in attrs.items():
                if item[0] == "name":
                    self._numeric_types.append(item[1])

    def numeric_types(self):
        return self._numeric_types


class _TaxonomyRefPartsHandler(xml.sax.ContentHandler):
    """Loads Taxonomy Ref Parts from the numeric us xsd file."""

    def __init__(self):
        """Ref parts constructor."""
        self._ref_parts = []

    def startElement(self, name, attrs):
        if name == "xs:element":
            for item in attrs.items():
                if item[0] == "name":
                    self._ref_parts.append(item[1])

    def ref_parts(self):
        return self._ref_parts


class _TaxonomyGenericRolesHandler(xml.sax.ContentHandler):
    """Loads Taxonomy Generic Roles from the generic roles xsd file."""

    def __init__(self):
        """Generic role handler constructor."""
        self._generic_roles = []
        self._process = False

    def startElement(self, name, attrs):
        if name == "link:definition":
            self._process = True

    def endElement(self, name):
        if name == "link:definition":
            self._process = False

    def characters(self, content):
        if self._process:
            self._generic_roles.append(content)

    def roles(self):
        return self._generic_roles


class TaxonomyNumericTypes(object):
    """
    Represents Miscellaneous Taxonomy Objects.

    Represents objects that are not covered in the
    other classes.  Generally speaking these are rarely used.
    """

    def __init__(self):
        """Misc object constructor."""
        self._numeric_types = self._load_numeric_types()

    def _load_numeric_types_file(self, pathname):
        tax = _TaxonomyNumericHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(tax)
        parser.parse(open(pathname))
        return tax.numeric_types()

    def _load_numeric_types(self):
        pathname = os.path.join(constants.SOLAR_TAXONOMY_DIR, "core")
        for filename in os.listdir(pathname):
            if 'numeric' in filename:
                numeric_types = self._load_numeric_types_file(os.path.join(
                    pathname, filename))
        return numeric_types

    def numeric_types(self):
        """
        A list of numeric types.
        """

        return self._numeric_types

    def validate_numeric_type(self, numeric_type):
        """
        Check if a numeric type is valid.
        """

        if numeric_type in self._numeric_types:
            return True
        else:
            return False


class TaxonomyGenericRoles(object):
    """
    Represents Generic Roles portion of the taxonomy.  Generally speaking this is rarely used.
    """

    def __init__(self):
        self._generic_roles = self._load_generic_roles()

    def _load_generic_roles_file(self, pathname):
        tax = _TaxonomyGenericRolesHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(tax)
        parser.parse(open(pathname))
        return tax.roles()

    def _load_generic_roles(self):
        pathname = os.path.join(constants.SOLAR_TAXONOMY_DIR, "core")
        for filename in os.listdir(pathname):
            if 'gen-roles' in filename:
                generic_roles = self._load_generic_roles_file(os.path.join(
                    pathname, filename))
        return generic_roles

    def generic_roles(self):
        """A list of generic roles."""
        return self._generic_roles

    def validate_generic_role(self, generic_role):
        """Check if a generic role is valid."""
        if generic_role in self._generic_roles:
            return True
        else:
            return False


class TaxonomyRefParts(object):
    """
    Represents the Referential Parts portion of the Taxonomy.  Generally speaking this is rarely used.
    """

    def __init__(self):
        self._ref_parts = self._load_ref_parts()

    def _load_ref_parts_file(self, pathname):
        tax = _TaxonomyRefPartsHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(tax)
        parser.parse(open(pathname))
        return tax.ref_parts()

    def _load_ref_parts(self):
        pathname = os.path.join(constants.SOLAR_TAXONOMY_DIR, "core")
        for filename in os.listdir(pathname):
            if 'ref-parts' in filename:
                ref_parts = self._load_ref_parts_file(os.path.join(pathname,
                                                                   filename))
        return ref_parts

    def ref_parts(self):
        """A list of ref parts."""
        return self._ref_parts

    def validate_ref_part(self, ref_part):
        """Check if a ref part is valid."""
        if ref_part in self._ref_parts:
            return True
        else:
            return False

class _TaxonomyDocstringHandler(xml.sax.ContentHandler):
    """Loads Taxonomy Docstrings from Labels file"""

    def __init__(self):
        """Ref parts constructor."""
        self._docstrings = {}
        self._awaiting_text_for_concept = None

    def startElement(self, name, attrs):
        # Technically we should be using the labelArc element to connect a label
        # element to a loc element and the loc element refers to a concept by its anchor
        # within the main xsd, but that's really complicated and in practice the
        # xlink:label atrr in the <label> element seems to always be "label_" plus the
        # name of the concept.
        concept = None
        role = None
        if name == "label":
            for item in attrs.items():
                # Do we care about the difference between xlink:role="http:.../documentation"
                # and xlink:role="http:.../label" ??
                if item[0] == "xlink:label":
                    concept = item[1].replace("label_solar_", "solar:")
                if item[0] == "xlink:role":
                    role = item[1]
        if concept is not None and role == "http://www.xbrl.org/2003/role/documentation":
            self._awaiting_text_for_concept = concept

    def characters(self, chars):
        if self._awaiting_text_for_concept is not None:
            self._docstrings[ self._awaiting_text_for_concept ] = chars

    def endElement(self, name):
        self._awaiting_text_for_concept = None

    def docstrings(self):
        return self._docstrings


class TaxonomyDocstrings(object):
    """
    Loads the documentation strings for each concept from solar_2018-03-31_r01_lab.xml
    """
    def __init__(self):
        self._docstrings = self._load_docstrings()

    def _load_docstrings(self):
        label_file = "solar_2018-03-31_r01_lab.xml"
        filename = os.path.join(constants.SOLAR_TAXONOMY_DIR, "core", label_file)

        tax = _TaxonomyDocstringHandler()
        parser = xml.sax.make_parser()
        parser.setContentHandler(tax)
        parser.parse(open(filename))
        return tax.docstrings()

    def docstrings(self):
        return self._docstrings
