import requests
import pprint
import json
import re
import datetime

pp = pprint.PrettyPrinter(indent = 2)

def trim_spaces(l):
        '''Trim white spaces in a list of text elements'''
        return [u' '.join(e.split()).encode('utf-8') for e in l]
 
def get_sections(dept, term_id, page_number, page_size, exclude):
    '''Get classes/sections from class API (one page at a time)'''
    base_url = 'https://apis.berkeley.edu/sis/v1/classes/sections'
    url = '{}?term-id={}&subject-area-code={}&print-in-schedule=true&page-number={}&page-size={}'.format(base_url, term_id, dept, page_number, page_size)
    #pp.pprint(url)
    # API ID and Key
    with open('config/api_keys.json', 'r') as f:
        api_keys = json.load(f)
        app_id = api_keys['class_app_id']
        app_key = api_keys['class_app_key']
    headers = {'Accept': 'application/json', 'app_id': app_id, 'app_key': app_key}
    #pp.pprint(headers)
    response = requests.get(url, headers = headers)
    #pp.pprint(response.json())
    if response.status_code != requests.codes.ok:
        return []
    sections = response.json()['apiResponse']['response']['classSections']
    return sections

def get_all_sections(dept, term_id, number_of_pages, page_size, exclude):
    '''Get all sections in output format compatible with Math website'''
    sections = []
    for i in range(number_of_pages):
        page_number = i + 1
        sections = sections + get_sections(dept, term_id, page_number, page_size, exclude)
    exclude_list = exclude.split(',')
    classes = []
    course_headers = ('Department', 'Number', 'Title')
    section_headers = ('Class', 'Number', 'Type', 'Days/Times', 'Location', 'Instructor', 'Status', 'Sort Key')
    for s in sections:
        course_info = dict(zip(course_headers, get_course_info(s)))
        section_info = dict(zip(section_headers, get_section_info(s)))
        if section_info['Type'] in exclude_list:
            # drop sections from exclude list
            continue
        #print s['class']['course']['displayName'], s['component']['code'], s['number'], s['id']
        #print course_info['Department'], course_info['Number'], section_info['Type'], section_info['Number'], section_info['Class']
        classes += [{'Course': course_info, 'Section': section_info}]
    return classes

def get_course_info(section):
    '''Get course information from raw section format'''
    dept = section['class']['course']['subjectArea']['code']
    course_num = section['class']['course']['catalogNumber']['formatted']
    course_title = section['class']['course']['title']
    return (dept, course_num, course_title)

def get_section_info(section):
    '''Get section infomation from raw section format'''
    class_num = section['id']
    section_num = section['number']
    section_type = section['component']['code']
    days = ''
    if 'meetings' in section.keys() and \
       'meetsDays' in section['meetings'][0].keys():
            days = section['meetings'][0]['meetsDays']
    times = ''
    if 'meetings' in section.keys() and \
       'startTime' in section['meetings'][0].keys() and \
       'endTime' in section['meetings'][0].keys():
            # convert 24 hour to 12 hour time
            t = datetime.datetime.strptime(section['meetings'][0]['startTime'], '%H:%M:%S')
            start_time = t.strftime('%I:%M%p')
            t = datetime.datetime.strptime(section['meetings'][0]['endTime'], '%H:%M:%S')
            end_time = t.strftime('%I:%M%p')
            times = '%5s - %5s' % (start_time, end_time)
    days_times = ('%s %s' % (days, times)).strip()
    #if days_times:
        #print days_times
    location = ''
    if 'meetings' in section.keys() and \
       'location' in section['meetings'][0].keys() and \
       'description' in section['meetings'][0]['location'].keys():
            location = section['meetings'][0]['location']['description']
            #print location
    instructor = ''
    if 'meetings' in section.keys() and \
       'assignedInstructors' in section['meetings'][0].keys():
            names = []
            for e in section['meetings'][0]['assignedInstructors']:
                if e['printInScheduleOfClasses'] and \
                   'instructor' in e.keys() and \
                   'names' in e['instructor'].keys() and \
                   'formattedName' in e['instructor']['names'][0].keys():
                        name = e['instructor']['names'][0]['formattedName']
                        #print name
                        names += [name]
            instructor = '\n'.join(trim_spaces(names))
    status = section['enrollmentStatus']['status']['description']
    course_num = section['class']['course']['catalogNumber']['formatted']
    sort_key = get_sortkey(course_num, section_num, section_type)
    return (class_num, section_num, section_type, days_times, location, instructor, status, sort_key)

def get_sortkey(course_num, section_num, section_type):
    '''Produce sort key from course number, section number, and section type'''
    r = r'(^\D?)(\d+)(\D*)$'
    i = 0
    m = re.match(r, course_num)
    m1 = m.group(1).rjust(1, ' ')
    m2 = m.group(2).rjust(3, '0')
    m3 = m.group(3).ljust(2, ' ')
    n = section_num
    if section_type == 'DIS' or section_type == 'WBD':
        n = n.rjust(5, '0')
    else:
        n = n.ljust(5, '0')
    return m2 + m3 + m1 + n


if __name__ == '__main__':
    '''Get department class schedule for specified term'''
    from optparse import OptionParser

    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-d', '--dept', dest = 'dept', default = 'MATH',
                      help = 'department abbreviation, e.g. MATH')
    parser.add_option('-t', '--term', dest = 'term_id', default = '2188',
                      help = 'term id, e.g. 2188')
    parser.add_option('-p', '--number-of-pages', type = 'int', dest = 'number_of_pages', default = 2,
                      help = 'number of pages, e.g. 1')
    parser.add_option('-s', '--page-size', type = 'int', dest = 'page_size', default = 400,
                      help = 'page number, e.g. 100 (maximum 400)')
    parser.add_option('-e', '--exclude', dest = 'exclude', default = 'IND,COL',
                      help = 'comma separated section types to be excluded from search results, default "IND,COL"')
    parser.add_option('-o', '--output', dest = 'output', default = 'sections.json',
                      help = 'name of output file (in json format)')
    (options, args) = parser.parse_args()
    # get arguments
    dept = options.dept
    term_id = options.term_id
    number_of_pages = options.number_of_pages
    page_size = options.page_size
    exclude = options.exclude
    output = options.output
    # get matching sections
    sections = get_all_sections(dept, term_id, number_of_pages, page_size, exclude)
    if sections and len(sections) > 0:
        print '{} class(es) found (see output in {})'.format(len(sections), output)
        with open(output, 'w') as f:
            json.dump(sections, f, sort_keys = True, indent = 2)
    else:
        print 'no classes found (no output)'
