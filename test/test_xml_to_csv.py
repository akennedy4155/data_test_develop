from unittest import TestCase
from copy import deepcopy
import xml.etree.ElementTree as ET

from src.xml_parse_to_csv import read_xml_to_tree, find_all_rec


class TestImportXML(TestCase):
    def setUp(self):
        # read the xml from url to tree
        url = 'https://www.w3schools.com/xml/cd_catalog.xml'
        self.tree = read_xml_to_tree(url)

    def test_read_xml_to_tree(self):
        root = self.tree.getroot()

        # basic xml tree structure inserts
        self.assertIsInstance(self.tree, ET.ElementTree)
        self.assertEqual(root.tag, 'CATALOG')
        self.assertEqual(len(list(root)), 26)

        # check that each of the children are parsing all of their children
        for child in root:
            self.assertEqual(len(list(child)), 6)

    def test_find_all_rec(self):
        # create an instance of the tree with duplicate tags in tree for testing find all rec method
        tree_with_duplicate_tag = deepcopy(self.tree)
        root = tree_with_duplicate_tag.getroot()

        # delete all children except the first one
        children = list(root)
        for i in range(1, len(children)):
            root.remove(children[i])

        # add a copy of the only child of tree to each grandchild
        add_to = list(root)[0]
        to_add = deepcopy(add_to)
        for child in add_to:
            child.append(to_add)

        self.assertEqual(len(find_all_rec(root, "CD")), 7)
