from lxml import html

def html2text(l):
    '''Convert HTML to unicode text in a list of nodes'''
    return [html.tostring(e, method = 'text', encoding = 'unicode') for e in l]

def trim_spaces(l):
    '''Trim white spaces in a list of text elements'''
    return [u' '.join(e.split()).encode('utf-8') for e in l]

def parse_course_header(node):
    e = node.xpath('./button/h3/span[@class="code"]/text()')
    code = trim_spaces(e)[0]
    l = code.split()
    if len(l) == 2:
        dept, num = l
    else:
        raise Exception('Expected department code and course number, got {}'.format(code))
    e = node.xpath('./button/h3/span[@class="title"]/text()')
    title = trim_spaces(e)[0]
    e = node.xpath('./button/h3/span[@class="hours"]/text()')
    hours = trim_spaces(e)[0]
    l = hours.split()
    if len(l) > 1 and l[-1][0:4] == 'Unit':
        units = ''.join(l[:-1])
    else:
        units = ''
    d = {'Department': dept, 'Number': num, 'Title': title, 'Units': units}
    return d

def parse_course_desc(node):
    e = node.xpath('.//p[@class="courseblockdesc"]/span/text()')
    e = trim_spaces(e)
    # first line should should start with 'Terms offered:'
    l = e[0].split(': ', 1)
    if l[0] == 'Terms offered':
        terms = l[1]
        desc = ' '.join(e[1:])
        d = {'Terms offered': terms, 'Description': desc}
    else:
        desc = ' '.join(e)
        d = {'Description': desc}
    return d

def parse_sections(node):
    # keys for parsing the catalog page
    keys = ['Also listed as', 'Credit Restrictions', 'Fall and/or spring',
        'Formerly known as', 'Grading', 'Grading/Final exam status', 'Online',
        'Prerequisites', 'Repeat rules', 'Subject/Course Level', 'Summer']
    e = node.xpath('.//div[@class="course-section"]/p')
    e = html2text(e)
    e = trim_spaces(e)
    d = {}
    for s in e:
        # skip lines not containing ': '
        if ':' not in s:
            continue
        # parse keys and values
        k, v = s.split(': ', 1)
        if k in keys:
            # remove incorrect <BR/> "tag"
            d[k] = v.replace('<BR/>', '')
    return d

def scrape_catalog(dept):
    # base URL for searching course catalog
    baseurl = 'http://guide.berkeley.edu/courses'
    url = '{}/{}/'.format(baseurl, dept.lower())
    tree = html.parse(url)
    courses = []
    course_nodes = tree.xpath('//div[@class="courseblock"]')
    for node in course_nodes:
        course = {}
        # parse header
        d = parse_course_header(node)
        course.update(d)
        # parse description
        d = parse_course_desc(node)
        course.update(d)
        # parse sections
        d = parse_sections(node)
        course.update(d)
        courses += [course]
    return courses

if __name__ == '__main__':
    from optparse import OptionParser
    from json import dump

    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-d', '--dept', dest = 'dept', default = 'MATH',
                      help = 'department abbreviation, default "MATH"')
    parser.add_option('-o', '--output', dest = 'outputfile', default = 'catalog.json',
                      help = 'name of output file in json format, default "catalog.json"')
    (options, args) = parser.parse_args()
    catalog = scrape_catalog(options.dept)
    print('{:d} courses scraped'.format(len(catalog)))
    # output file
    f = open(options.outputfile, 'wb')
    dump(catalog, f, sort_keys = True, indent = 2)
    f.close()
    print('see output in "{}"'.format(options.outputfile))
