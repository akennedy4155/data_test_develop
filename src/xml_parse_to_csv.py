import xml.etree.ElementTree as ET
import urllib2
from copy import deepcopy

from exceptions import AmbiguousElement, MissingElement, WrongElementType


def read_xml_to_tree(url):
    """
    Read XML from URL into ElementTree object
    :param url: XML file url
    :return: ElementTree of XML object
    """
    f_xml = urllib2.urlopen(url)
    return ET.parse(f_xml)


def find_all_rec(element, tag):
    """
    Recursively find all elements with tag within element
    :param element: Element to search
    :param tag: Tag to search for
    :return: List of all sub-elements that have the tag
    """
    # TODO: could make this a generator
    matches = []
    for child in list(element):
        if child.tag == tag:
            matches += [child]
        matches += find_all_rec(child, tag)
    return matches


# TODO: add functionality for other element types
def extract_basic(element, tag):
    """
    Extract a basic type (text field, leaf node) sub-element from parent with given tag

    :param element: Parent element to extract from
    :param tag: Tag of element to extract
    :return: Extracted element as a string
    """
    extract_elements = find_all_rec(element, tag)
    validate_extract_element(extract_elements)  # validate exists and non-duplicate

    # failure: element is not basic type
    return_element = extract_elements[0]
    if list(return_element):  # if element has children, then not basic type
        raise WrongElementType()

    # success!
    return return_element


def extract_list(element, list_tag, list_element_tag):
    """
    Extract a list type (internal node, all children basic type) sub-element from parent with given list_tag and
    elements having list_element_tag

    :param element: parent element
    :param list_tag:
    :param list_element_tag:
    :return: Extracted element as a list
    """
    extract_elements = find_all_rec(element, list_tag)
    validate_extract_element(extract_elements)  # validate exists and non-duplicate

    # failure: element is not list type
    possible_list = extract_elements[0]

    return_list = list(possible_list)
    for ele in return_list:  # validate that list element is basic type and ele tag matches
        if ele.tag != list_element_tag or list(ele):
            raise WrongElementType("Expected 'List'")

    # success!
    return return_list


def validate_extract_element(found_elements):
    """
    Validate conditions for extract element:
    Element must exist
    Element must not have duplicate tag as another element
    Helper method for extract_element_... methods
    :param found_elements: Preliminary element list found by extract_element_...
    :return: None
    """
    # failure: element with tag doesn't exist
    if not found_elements:
        raise MissingElement()

    # failure: multiple elements with same tag
    if len(found_elements) > 1:
        raise AmbiguousElement()


# TODO: make the assumption that one row element will not be inside another row element
# this means that in this problem, a Listing element will not be inside another Listing element
# This needs to be more robust... What happens if there are nested elements and we want to get information about both of
# them for a row?

# TODO: default behavior turns a list into a string with elements sep by commas.  Could add functionality to make this variable later.
def bulk_extract(tree, row_tag, elements_basic=[], elements_list=[]):
    """
    Creates a dictionary with keys that represent the parent element of a row and values that are the columns in that row
    Preparation for loading into a pandas DF
    Structure:
    {
        key (row_element): value (
            {
                key (sub-element tag): value (element text)
            }
        )
    }
    :param tree: xml tree to load all this information from
    :param row_tag: tag for the elements to extract from
    :param elements_basic: list of tags for the basic elements to extract
    :param elements_list: list of tags for the list elements to extract
    :return: Dict prepared for DF load
    """
    row_elements = find_all_rec(tree.getroot(), row_tag)
    df_dict = {}
    for element in row_elements:
        df_row_entry = {
            "basics": {},
            "lists": {}
        }
        for basic in elements_basic:
            df_row_entry["basics"][basic] = extract_basic(element, basic)
        for lists in elements_list:
            df_row_entry["lists"][lists["list_tag"]] = extract_list(element, lists["list_tag"], lists["list_element_tag"])
        df_dict[element] = df_row_entry
    return df_dict


# TODO: docstring
def stringify_bulk_extract(extract_row):
    a_copy = deepcopy(extract_row)

    # extract text from basic elements
    bel_dict = a_copy["basics"]
    for tag in bel_dict:
        bel_dict[tag] = bel_dict[tag].text

    # extract text from list elements and join with comma according to project requirements
    lel_dict = a_copy["lists"]
    for tag in lel_dict:
        for i in range(len(lel_dict[tag])):
            lel_dict[tag][i] = lel_dict[tag][i].text
        lel_dict[tag] = ", ".join(lel_dict[tag])

    # remove top level of nested dictionary and compress basics and lists
    # {'basics': {'TITLE': 'Greatest Hits'}, 'lists': {'ARTIST': 'TEST, TEST'}} ->
    # {'TITLE': 'Greatest Hits', 'ARTIST': 'TEST, TEST'}
    compressed = {}
    for el_dict in a_copy.values():
        for key in el_dict:
            compressed[key] = el_dict[key]

    return compressed
