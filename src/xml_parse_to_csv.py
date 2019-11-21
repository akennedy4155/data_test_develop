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
    # Base Case: no children, leaf element
    if not list(element):
        return [element] if element.tag == tag else []

    # Recursive Step: internet element / root element
    matches = element.findall(tag)
    for child in list(element):
        matches += find_all_rec(child, tag)
    return matches


# TODO: document exceptions for extract element
# TODO: add more element types that we can extract besides basic and list
def extract_element_basic(element, tag):
    """
    Extract a basic type (text field, leaf node) sub-element from parent with given tag

    :param element: Parent element to extract from
    :param tag: Tag of element to extract
    :return: Extracted element as a string
    """
    pass


def extract_element_list(element, list_tag, list_element_tag):
    """
    Extract a list type (internal node, all children leaf nodes) sub-element from parent with given list_tag and
    elements having list_element_tag

    :param element: parent element
    :param list_tag:
    :param list_element_tag:
    :return: Extracted element as a list
    """
    pass
