# Alex Kennedy 11-22-19
# Library Imports
import xml.etree.ElementTree as ET
import urllib2
from copy import deepcopy

# My Imports
from exceptions import AmbiguousElement, MissingElement, WrongElementType

# Out of Scope TODOs
# TODO: assumes that the client is connected to the internet. could add some functionality to check this
# TODO: change find_all_rec to generator func
# TODO: add variable behavior for default MissingElement() error handling, default blank string return
# TODO: default behavior turns a list into a string with elements sep by commas, create variable functionality?
# TODO: add functionality for other element types besides 'Basic' and 'List'


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
    matches = []
    for child in list(element):
        if child.tag == tag:
            matches += [child]
        matches += find_all_rec(child, tag)
    return matches


def extract_basic(element, tag):
    """
    Extract and validate a basic type (text field, leaf node) sub-element from parent with given tag

    :param element: Parent element to extract from
    :param tag: Tag of element to extract
    :return: Extracted element as a string
    """
    # parse and traverse ancestry
    ancestry = tag.split('.')
    current = element
    for sub_tag in ancestry:
        extract_elements = find_all_rec(current, sub_tag)
        # validate exists and non-duplicate for ancestor
        try:
            validate_extract_element(extract_elements)  # validate exists and non-duplicate
        except MissingElement:  # default missing element behavior return blank element
            blank = ET.Element("Blank")
            blank.text = ""
            return blank
        current = extract_elements[0]

    # failure: element is not basic type
    return_element = current
    if list(return_element):  # if element has children, then not basic type
        raise WrongElementType("Expected 'basic'.")

    # success!
    return return_element


def extract_list(element, list_tag, list_element_tag):
    """
    Extract and validate a list type (internal node, all children basic type) sub-element from
    parent with given list_tag and elements having list_element_tag

    :param element: parent element
    :param list_tag:
    :param list_element_tag:
    :return: Extracted element as a list
    """
    # parse and traverse ancestry
    ancestry = list_tag.split('.')
    current = element
    for sub_tag in ancestry:
        extract_elements = find_all_rec(current, sub_tag)
        try:
            validate_extract_element(extract_elements)  # validate exists and non-duplicate
        except MissingElement:  # default missing element behavior return blank element
            blank = ET.Element("Blank")
            blank.text = ""
            return blank
        current = extract_elements[0]

    # failure: element is not list type
    possible_list = current
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

    :param found_elements: Preliminary element list found by extract_...
    :return: None
    """
    # failure: element with tag doesn't exist
    if not found_elements:
        raise MissingElement()

    # failure: multiple elements with same tag
    if len(found_elements) > 1:
        raise AmbiguousElement("{}".format(found_elements[0].tag))


def bulk_extract(root, row_tag, elements_basic=[], elements_list=[]):
    """
    Creates a dictionary (structure below) of a bulk extract from an XML tree, preparation for pd.DataFrame

    Structure:
    {
        key (row_element): value (
            {
                "basics": {
                    basic_tag: basic_element,
                    ...
                },
                "lists": {
                    list_tag: [
                        list_sub_element,
                        ...
                    ],
                    ...
                }
            }
        )
    }

    :param root: root of tree
    :param row_tag: tag for the parent elements to extract from
    :param elements_basic: basic element to extract tags
    :param elements_list: list element to extract tags
    :return: Dict prepared for DF load (structure above)
    """
    # get all row elements to parse
    row_elements = find_all_rec(root, row_tag)

    # construct the dictionary with basic and list elements
    df_dict = {}
    for element in row_elements:
        df_row_entry = {
            "basics": {},
            "lists": {}
        }
        for basic in elements_basic:
            df_row_entry["basics"][basic] = extract_basic(element, basic)
        for lists in elements_list:
            df_row_entry["lists"][lists["list_tag"]] = extract_list(
                element, lists["list_tag"], lists["list_element_tag"]
            )
        df_dict[element] = df_row_entry

    return df_dict


def stringify_bulk_extract(extract_row):
    """
    Stringify a build extract row:
    Remove parent element,
    compress basics and lists dicts,
    extract text from each <ELement>,
    make list into ',' joined string

    Example:
    Input
    {<Element 'CD' at 0x3482400>: {'basics': {'TITLE': <Element 'TITLE' at 0x3482518>},
                               'lists': {'ARTIST': []}},
     <Element 'CD' at 0x34824a8>: {'basics': {'TITLE': <Element 'TITLE' at 0x3482828>},
                                   'lists': {'ARTIST': [<Element 'SUBARTIST' at 0x34e0438>]}},
     <Element 'CD' at 0x34827b8>: {'basics': {'TITLE': <Element 'TITLE' at 0x3482b38>},
                                   'lists': {'ARTIST': [<Element 'SUBARTIST' at 0x34e0470>,
                                                        <Element 'SUBARTIST' at 0x34e04a8>]}}}

    Output
    [{'ARTIST': '', 'TITLE': 'Empire Burlesque'},
     {'ARTIST': 'TEST', 'TITLE': 'Hide your heart'},
     {'ARTIST': 'TEST, TEST', 'TITLE': 'Greatest Hits'}]

    :param extract_row: row dict to extract from
    :return: List of CSV rows
    """
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
