import pipes
import re
import json

# keys for parsing the catalog page
keys = ['Also listed as', 'Credit Restrictions', 'Fall and/or spring', 'Formerly known as', 'Grading', 'Grading/Final exam status', 'Online', 'Prerequisites', 'Repeat rules', 'Subject/Course Level', 'Summer', 'Terms offered']

def read_pipe(baseurl, dept):
    cmd = 'w3m -dump -no-cookie -cols 500'
    # add department code
    url = '%s/%s/' % (baseurl, dept.lower())
    pipecmd = '%s "%s"' % (cmd, url)
    kind = '.-'
    t = pipes.Template()
    t.prepend(pipecmd, kind)
    f = t.open('-', 'r')
    dept = dept.upper()
    fields = []
    # flag for matching course description
    t = 0
    for l in f:
        l = l.strip()
        #print l
        # matching course title
        m = re.match(r'^%s .* Units?$' % dept, l)
        if m:
            fields += [('Course', m.group())]
        # matching course fields
        for k in keys:
            m = re.match(r'^(%s): (.*)$' % k, l)
            if m:
                if m.group(2):
                    fields += [m.group(1,2)]
                else:
                    fields += [(m.group(1), '')]
                if k == 'Terms offered':
                    t = 1
                    d = []
        # matching course description (zero or more non-empty lines after the field 'Terms offered')
        if t == 1:
            t = 2
            # go to next line
            continue
        elif t == 2 and len(l) > 0:
        # Original code will produce a description ending with 'Read More [+]'
            if not l.endswith('[+]'):
                d += [l]
        #####################################################################
        elif t == 2 and len(l) == 0:
            t = 0
            fields += [('Description', ' '.join(d))]
    f.close()
    return fields

def split_course_info(course_field_value):
    s = course_field_value.split()
    d = {'Dept Code': s[0], 'Number': s[1]}
    if s[-3] == '-':
        d['Title'] = ' '.join(s[2:-4])
        d['Units'] = ''.join(s[-4:-1])
    else:
        d['Title'] = ' '.join(s[2:-2])
        d['Units'] = s[-2]
    return d

def get_catalog(baseurl, dept):
    courses = []
    course = {}
    fields = read_pipe(baseurl, dept)
    for k, v in fields:
        if k == 'Course' and course:
            courses += [course]
            course = {}
        course[k] = v
    if course:
        courses += [course]
    #print len(courses)
    for c in courses:
        c['Course'] = split_course_info(c['Course'])
    comment = str(len(courses)) + ' courses matched'
    return {'Comment': comment, 'Courses': courses}

if __name__ == '__main__':
    from optparse import OptionParser

    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-d', '--dept', dest='dept', default='MATH',
                      help='department abbreviation, e.g. MATH')
    parser.add_option('-f', '--file', dest='file', default='catalog.json',
                      help='name of output file (in json format)')
    (options, args) = parser.parse_args()
    # base URL for searching course catalog
    baseurl = 'http://guide.berkeley.edu/courses'
    dept = options.dept
    # output file
    f = open(options.file, 'wb')

    catalog = get_catalog(baseurl, dept)
    json.dump(catalog, f, sort_keys=True, indent=4)
    f.close()
