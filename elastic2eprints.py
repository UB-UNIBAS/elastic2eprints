from lxml import etree
import logging


class UnknownElementError(Exception):
    pass


def transform(output_base_path, base_file_name, data, chunk_size=1000):
    """Transforms a json data record to a eprints XML data record.

    :param output_base_path:    Directory where the data should be stored.
    :param base_file_name:      Base file name. Append a number if there are more than chunk_size records.
    :param data:                The data as list of json dictionaries.
    :param chunk_size:          The number of records per output file.
    """
    # splits data into chunks of 1000 items
    split_data = [data[x:x+chunk_size] for x in range(0, len(data), chunk_size)]

    # used to make sure file names are unique
    repeat = 1
    for data_chunk in split_data:
        root = etree.Element('eprints')
        for record in data_chunk:
            eprint = etree.SubElement(root, 'eprint', xmlns='http://eprints.org/ep2/data/2.0')
            for key in record:
                # e.g. mcssid
                if isinstance(record[key], list):
                    list_element = etree.SubElement(eprint, key)
                    for item in record[key]:
                        item_element = etree.SubElement(list_element, 'item')
                        if list_element.tag == 'documents':
                            item_element.tag = 'document'
                        # e.g. divisions_names
                        if isinstance(item, str):
                            item_element.text = item
                        # e.g. mcssid
                        elif isinstance(item, int):
                            item_element.text = str(item)
                        # e.g. contributors, id_number, documents
                        elif isinstance(item, dict):
                            for key in item:
                                # e.g. no fields, added for completeness.
                                if isinstance(item[key], int) or isinstance(item[key], float):
                                    etree.SubElement(item_element, key).text = str(item[key])
                                # e.g. contributors.id, id_number.type
                                elif isinstance(item[key], str):
                                    etree.SubElement(item_element, key).text = item[key]
                                # e.g. empty fields.
                                elif isinstance(item[key], type(None)):
                                    pass
                                    # etree.SubElement(item_element, key).text = 'None'
                                # e.g. contributors.name
                                elif isinstance(item[key], dict) and key == 'name':
                                    name = etree.SubElement(item_element, 'name')
                                    for name_key in item[key]:
                                        # e.g. empty field (honorific, lineage)
                                        if isinstance(item[key][name_key], type(None)):
                                            pass
                                        # e.g. contributors.name.given
                                        else:
                                            etree.SubElement(name, name_key).text = str(item[key][name_key])
                                # e.g. documents.files
                                elif isinstance(item[key], list):
                                    files_element = etree.SubElement(item_element, key)
                                    if key == 'files':
                                        sub_element_name = 'file'
                                    # e.g. if the list in dict is not a file. currently not present in edoc.
                                    else:
                                        sub_element_name = 'item'
                                    # e.g. documents.files.filesize
                                    for file in item[key]:
                                        file_element = etree.SubElement(files_element, sub_element_name)
                                        for file_element_key in file:
                                            etree.SubElement(file_element, file_element_key).text = str(file[file_element_key])
                                else:
                                    raise UnknownElementError('Found an element which could not be transformed: ' + key)

                        # e.g. divisions_ids, .. (no eprints standard field at the moment)
                        elif isinstance(item, list):
                            for element in item:
                                if isinstance(element, str):
                                    item_element.text = element
                                elif isinstance(element, list):
                                    item_element.text = str(element[0])
                                    for sub_elements in element[1:]:
                                        etree.SubElement(list_element, 'item').text = str(sub_elements)
                                else:
                                    raise UnknownElementError('Found an element which could not be transformed: ' + key)
                        else:
                            raise UnknownElementError('Found an element which could not be transformed: ' + key)
                # e.g. eprint_status
                else:
                    temp = etree.SubElement(eprint, key)
                    temp.text = str(record[key])

        result = etree.tostring(root, encoding='utf-8', xml_declaration=True, pretty_print=True)
        with open(output_base_path + base_file_name + str(repeat) + '.xml', 'w', encoding='utf-8') as file:
            file.write(result.decode('utf-8'))
        repeat += 1
        logging.info('Transformed and stored %s records in %s.', len(data_chunk), output_base_path + base_file_name + str(repeat) + '.xml')

    logging.info('Finished transformation.')


if __name__ == '__main__':
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    transform('/home/swissbib/Dokumente/open_access/elastic_to_eprints/', 'edoc-vmware-data-')
