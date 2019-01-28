import requests
import pprint
import json
import re
import datetime

pp = pprint.PrettyPrinter(indent = 2)

def get_sections(term_id, section_id):
    '''Get section from class API by section ID'''
    base_url = 'https://apis.berkeley.edu/sis/v1/classes/sections'
    url = '{}/{}?term-id={}&include-secondary=true'.format(base_url, section_id, term_id)
    pp.pprint(url)
    # API ID and Key
    with open('config/api_keys.json', 'r') as f:
        api_keys = json.load(f)
    app_id = api_keys['class_app_id']
    app_key = api_keys['class_app_key']
    headers = {'Accept': 'application/json', 'app_id': app_id, 'app_key': app_key}
    pp.pprint(headers)

    api_response = requests.get(url, headers = headers)
    #pp.pprint(api_response.json())
    if api_response.json()['apiResponse']['httpStatus']['code'] != '200':
        return
    section = api_response.json()['apiResponse']['response']['classSections']
    return section


if __name__ == '__main__':
    '''Get class section by id in json format'''
    from optparse import OptionParser

    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-t', '--term', dest = 'term_id', default = '2188',
                      help = 'term ID, e.g. 2188')
    parser.add_option('-s', '--section-id', dest = 'section_id', default = None,
                      help = 'class section ID')
    parser.add_option('-o', '--output', dest = 'output', default = 'section.json',
                      help = 'name of output file (in json format)')
    (options, args) = parser.parse_args()
    # get arguments
    term_id = options.term_id
    section_id = options.section_id
    output = options.output
    # get matching sections
    sections = get_sections(term_id, section_id)
    if sections:
        print 'section {} found (see output in {})'.format(section_id, output)
        with open(output, 'w') as f:
            json.dump(sections, f, sort_keys = True, indent = 2)
    else:
        print 'section {} not found (no output)'.format(section_id)
