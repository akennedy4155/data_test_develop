# Alex Kennedy 11-22-19
# Library Imports
from unittest import TestCase
from copy import deepcopy
import xml.etree.ElementTree as ET

# My Imports
from src.exceptions import MissingElement, AmbiguousElement, WrongElementType
import src.xml_parse_to_csv as xmltocsv

# Out of Scope TODOs
# TODO: add more layers of ancestry testing for extract_element
# TODO: expand bulk_extract asserts for further coverage
# TODO: flipped expected and actual for assertEquals


class TestXMLToCSV(TestCase):
    def setUp(self):
        # read the xml from url to tree
        url = 'https://www.w3schools.com/xml/cd_catalog.xml'
        self.tree = xmltocsv.read_xml_to_tree(url)

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

        # check that we parse nested elements
        for child in root:
            self.assertEqual(len(list(child)), 6)

    def test_find_all_rec(self):
        self.assertEqual(len(xmltocsv.find_all_rec(self.tree.getroot(), 'TITLE')), 26)
        self.assertEqual(len(xmltocsv.find_all_rec(self.tree_with_duplicate_tag.getroot(), "CD")), 7)

    def test_bulk_extract(self):
        test_tree = deepcopy(self.tree)
        root = test_tree.getroot()
        children = list(root)

        # add a list element to the first three to test that functionality
        for child_i in range(3):
            to_add = ET.Element('SUBARTIST')
            to_add.text = 'TEST'
            add_to = children[child_i].find('ARTIST')
            for _ in range(child_i):
                add_to.append(deepcopy(to_add))

        # truncate to 3 children
        for i in range(3, len(children)):
            root.remove(children[i])

        expected = [
            {
                "TITLE": "Empire Burlesque",
                "ARTIST": ""
            },
            {
                "TITLE": "Hide your heart",
                "ARTIST": "TEST"
            },
            {
                "TITLE": "Greatest Hits",
                "ARTIST": "TEST, TEST"
            }
        ]

        actual = xmltocsv.bulk_extract(
            root,
            "CD",
            elements_basic=["TITLE"],
            elements_list=[{"list_tag": "ARTIST", "list_element_tag": "SUBARTIST"}]
        ).values()
        actual = [xmltocsv.stringify_bulk_extract(row_dict) for row_dict in actual]

        # test that expected = actual but ignore order of the list
        expected = list(expected)  # make a mutable copy
        expected_equals_actual = True
        try:
            for elem in actual:
                expected.remove(elem)
        except ValueError:
            expected_equals_actual = False
        if expected:
            expected_equals_actual = False

        self.assertTrue(expected_equals_actual)

        # assert exception for arguments that aren't valid
        self.assertRaises(Exception, xmltocsv.bulk_extract, test_tree, "CD", basic=["TITLE"], list=["ARTIST"])


class TestExtractElement(TestCase):
    def setUp(self):
        # create CD catalog with 1 CD for easier testing
        url = 'https://www.w3schools.com/xml/cd_catalog.xml'
        self.tree = xmltocsv.read_xml_to_tree(url)
        root = self.tree.getroot()
        children = list(root)
        for i in range(1, len(children)):
            root.remove(children[i])

        # create a list element for testing
        to_add = ET.Element('SUBARTIST')
        to_add.text = 'TEST'
        add_to = xmltocsv.find_all_rec(root, 'ARTIST')[0]
        for i in range(3):
            add_to.append(deepcopy(to_add))

        # create the root element for testing functions
        self.test_root = xmltocsv.find_all_rec(self.tree.getroot(), 'CD')[0]

    def test_extract_element_success(self):
        parent_1LA = self.test_root

        # build first test for 2 level ancestry <Top><Mid><Bot>real</Bot></Mid><Bot>fake</Bot></Top>
        parent_2LA_a = ET.Element("Top")
        ET.SubElement(parent_2LA_a, "Mid")
        bot_real = ET.Element("Bot")
        bot_real.text = "real"
        parent_2LA_a.find("Mid").append(bot_real)
        bot_fake = ET.Element("Bot")
        bot_fake.text = "decoy"
        parent_2LA_a.append(bot_fake)

        # build second test for 2 level ancestry <Top><Mid><Bot>real</Bot></Mid><Mid2><Bot>fake</Bot></Mid2></Top>
        parent_2LA_b = ET.Element("Top")
        ET.SubElement(parent_2LA_b, "Mid")
        ET.SubElement(parent_2LA_b, "Mid2")
        bot_real = ET.Element("Bot")
        bot_real.text = "real"
        parent_2LA_b.find("Mid").append(bot_real)
        bot_fake = ET.Element("Bot")
        bot_fake.text = "decoy"
        parent_2LA_b.find("Mid2").append(bot_fake)

        # Basic
        # 1 level ancestry
        self.assertEqual(xmltocsv.extract_basic(parent_1LA, 'TITLE').text, 'Empire Burlesque')
        # 2 level ancestry
        self.assertEqual(xmltocsv.extract_basic(parent_2LA_a, 'Mid.Bot').text, 'real')
        self.assertEqual(xmltocsv.extract_basic(parent_2LA_b, 'Mid2.Bot').text, 'decoy')

        # List
        compare = ['TEST', 'TEST', 'TEST']
        self.assertEqual([ele.text for ele in xmltocsv.extract_list(parent_1LA, 'ARTIST', 'SUBARTIST')], compare)

    def test_extract_element_fail_not_exists(self):
        # Failure: Sub-element with tag does not exist within parent element
        parent = self.test_root

        # Basic
        self.assertEqual(xmltocsv.extract_basic(parent, 'NOT_THERE').text, "")

        # List
        self.assertEqual(xmltocsv.extract_list(parent, 'NOT_THERE', 'STILL_NOT_THERE').text, "")

    def test_extract_element_fail_duplicate_key(self):
        # Failure: Multiple sub-elements found with tag within parent element
        parent = self.test_root

        # Basic
        self.assertRaises(AmbiguousElement, xmltocsv.extract_basic, parent, 'SUBARTIST')

        # List
        self.assertRaises(AmbiguousElement, xmltocsv.extract_list, parent, 'SUBARTIST', 'SUBSUBARTIST')

    def test_extract_element_failure_wrong_type(self):
        parent = self.test_root

        # Basic
        self.assertRaises(WrongElementType, xmltocsv.extract_basic, parent, 'ARTIST')

        # List
        self.assertRaises(WrongElementType, xmltocsv.extract_list, self.tree.getroot(), 'CD', 'TRACK')

    def test_validate_extract_element(self):
        parent = self.test_root

        # Does not exist
        found_elements = xmltocsv.find_all_rec(parent, 'NOT_THERE')
        self.assertRaises(MissingElement, xmltocsv.validate_extract_element, found_elements)

        # Duplicate tag
        found_elements = xmltocsv.find_all_rec(parent, 'SUBARTIST')
        self.assertRaises(AmbiguousElement, xmltocsv.validate_extract_element, found_elements)
