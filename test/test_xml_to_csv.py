from unittest import TestCase
from copy import deepcopy
import xml.etree.ElementTree as ET

from src import read_xml_to_tree, find_all_rec, extract_element_basic


class TestXMLToCSV(TestCase):
    # TODO: TearDown
    def setUp(self):
        # read the xml from url to tree
        url = 'https://www.w3schools.com/xml/cd_catalog.xml'
        self.tree = read_xml_to_tree(url)
        print(ET.tostring(self.tree.getroot()))

        # create an instance of the tree with duplicate tags in tree for testing find all rec method
        self.tree_with_duplicate_tag = deepcopy(self.tree)
        root = self.tree_with_duplicate_tag.getroot()

        # delete all children except the first one
        children = list(root)
        for i in range(1, len(children)):
            root.remove(children[i])

        # add a copy of the only child of tree to each grandchild
        add_to = list(root)[0]
        to_add = deepcopy(add_to)
        for child in add_to:
            child.append(to_add)

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
        self.assertEqual(len(find_all_rec(self.tree_with_duplicate_tag.getroot(), "CD")), 7)

    def test_extract_element_basic_success(self):
        # Success: Basic element (text field, leaf node)

        # create CD catalog with 1 CD for easier testing
        ee_tree = deepcopy(self.tree)
        root = ee_tree.getroot()
        children = list(root)
        for i in range(1, len(children)):
            root.remove(children[i])

        root_tag, extract_tag = 'CD', 'Title'
        elements = find_all_rec(root, root_tag)[0]  # use the first CD in the list for testing
        self.assertEqual(extract_element_basic(elements, extract_tag), "Empire Burlesque")


class TestExtractElement(TestCase):
    # TODO: Tear Down
    def setUp(self):
        pass

    def test_extract_element_success(self):
        # Tests success case of both extract element methods
        self.fail()

    def test_extract_element_fail_not_exists(self):
        # Tests failure case of both extract element methods
        # Failure: Sub-element with tag does not exist within parent element
        self.fail()

    def test_extract_element_fail_duplicate_key(self):
        # Tests failure case of both extract element methods
        # Failure: Multiple sub-elements found with tag within parent element
        self.fail()

    def test_extract_element_basic_failure_not_basic(self):
        # Failure: sub-element is not type basic (text field, leaf node)
        self.fail()

    def test_extract_element_failure_not_list(self):
        # Failure: sub-element is not type list ()
        self.fail()
