import xml.etree.ElementTree as ET
import argparse
import logging


def strip_xml_elements(tags: list, input_file: str, output_file: str) -> set:
    tree = ET.parse(input_file)
    root = tree.getroot()

    removed = set()
    for item in root.findall('*'):
        for element in item:
            tag = element.tag.split('}')[1]
            if tag not in tags:
                item.remove(element)
                removed.add(tag)

    tree.write(output_file)
    return removed


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove all fields not given as argument from xml data file.')
    parser.add_argument('xml_elements', metavar='S', nargs='+', type=str, help='eprints elements you want to keep')
    parser.add_argument('-f', dest='input_file', type=str, help='The XML file which should be cleaned.',
                        default='input-data.xml')
    parser.add_argument('-d', dest='output_file', type=str, help='The file the result should be stored in.',
                        default='output-data.xml')
    args = parser.parse_args()

    logger = logging.getLogger('xml-cleaner')
    logger.info('Keep the following XML-Elements: %s.', args.xml_elements)
    removed_tags = strip_xml_elements(args.xml_elements, args.input_file, args.output_file)
    logger.info('Removed the following elements: %s.', removed_tags)
    logger.info('Stored result in %s.', args.output_file)



