from unittest import TestCase
# TODO: imports for tests go local or at top?
from src.xml_parse_to_csv import read_xml_to_tree
import xml.etree.ElementTree as ET

# class XmlTestCase(TestCase):
#     def setUp(self):
#         self.xml_tree


class TestImportXML(TestCase):
    def setUp(self):
        # read the xml from url to tree
        url = 'https://www.w3schools.com/xml/cd_catalog.xml'
        self.tree = read_xml_to_tree(url)

    def test_read_xml_to_tree(self):
        root = self.tree.getroot()

        # check that a tree is returned
        self.assertIsInstance(self.tree, ET.ElementTree)

        # check that the root is has tag catalog
        self.assertTrue(root.tag == 'CATALOG')

        # check that there are X children
        self.assertTrue(len(list(root)) == 26)

        # check that each of the children are parsing all of their children
        for child in root:
            self.assertTrue(len(list(child)) == 6)
