import xml.etree.ElementTree as ET
import urllib2


def read_xml_to_tree(url):
    """
    Read XML from URL into ElementTree object
    :param url: XML file url
    :return: ElementTree of XML object
    """
    f_xml = urllib2.urlopen(url)
    return ET.parse(f_xml)


def find_all_rec(element, tag):
    # TODO: could make this into a generator?
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


# TODO: document exceptions for extract element
# TODO: add more element types that we can extract besides basic and list
# TODO: custom exceptions for the failure cases
# TODO: better error messages for the failure cases
def extract_element_basic(element, tag):
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
        raise Exception('Element not basic type.')

    # success!
    return return_element


def extract_element_list(element, list_tag, list_element_tag):
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
    if not list(possible_list):  # validate that the possible list element is not basic
        raise Exception('Element not list type.')

    return_list = list(possible_list)
    for ele in return_list:  # validate that list element is basic type and ele tag matches
        if ele.tag != list_element_tag or list(ele):
            raise Exception('Element not list type.')

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
        raise Exception('Element does not exist.')

    # failure: multiple elements with same tag
    if len(found_elements) > 1:
        raise Exception('Duplicate extraction tag.')
