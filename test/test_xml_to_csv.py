from unittest import TestCase
from copy import deepcopy
import xml.etree.ElementTree as ET

# TODO: refactor all of these imports
from src import read_xml_to_tree, find_all_rec, extract_element_basic, extract_element_list


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


class TestExtractElement(TestCase):
    # Sauce: https://stackoverflow.com/questions/8672754/how-to-show-the-error-messages-caught-by-assertraises-in-unittest-in-python2-7
    def assertRaisesWithMessage(self, msg, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.assertFail()
        except Exception as inst:
            self.assertEqual(inst.message, msg)

    # TODO: Tear Down
    def setUp(self):
        # create CD catalog with 1 CD for easier testing
        url = 'https://www.w3schools.com/xml/cd_catalog.xml'
        self.tree = read_xml_to_tree(url)
        root = self.tree.getroot()
        children = list(root)
        for i in range(1, len(children)):
            root.remove(children[i])

        # create a list element for testing
        to_add = ET.Element('SUBARTIST')
        to_add.text = 'TEST'
        add_to = find_all_rec(root, 'ARTIST')[0]
        for i in range(3):
            add_to.append(deepcopy(to_add))

        print(ET.tostring(root))

    def test_extract_element_success(self):
        parent = find_all_rec(self.tree.getroot(), 'CD')[0]

        # Basic
        self.assertEqual(extract_element_basic(parent, 'TITLE'), 'Empire Burlesque')

        # List
        compare = ['TEST', 'TEST', 'TEST']
        self.assertEqual(extract_element_list(parent, 'ARTIST', 'SUBARTIST'))

    def test_extract_element_fail_not_exists(self):
        # Tests failure case of both extract element methods
        # Failure: Sub-element with tag does not exist within parent element
        parent = find_all_rec(self.tree.getroot(), 'CD')[0]

        # Basic
        self.assertRaisesWithMessage('Element does not exist.', extract_element_basic, parent, 'NOT_THERE')

        # List
        self.assertRaisesWithMessage('Element does not exist.', extract_element_list, parent, 'NOT_THERE')

    def test_extract_element_fail_duplicate_key(self):
        # Tests failure case of both extract element methods
        # Failure: Multiple sub-elements found with tag within parent element
        parent = find_all_rec(self.tree.getroot(), 'CD')[0]

        # Basic
        self.assertRaisesWithMessage('Duplicate extraction tag.', extract_element_basic, parent, 'SUBARTIST')

        # List
        self.assertRaisesWithMessage('Duplicate extraction tag.', extract_element_list, parent, 'SUBARTIST')

    def test_extract_element_basic_failure_not_basic(self):
        # Failure: sub-element is not type basic (text field, leaf node)
        parent = find_all_rec(self.tree.getroot(), 'CD')[0]
        self.assertRaisesWithMessage('Duplicate extraction tag.', extract_element_basic, parent, 'ARTIST')

    def test_extract_element_failure_not_list(self):
        # Failure: sub-element is not type list ()
        parent = find_all_rec(self.tree.getroot(), 'CD')[0]
        self.assertRaisesWithMessage('Duplicate extraction tag.', extract_element_list, parent, 'TITLE')
