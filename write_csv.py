from get_classes import get_classes

def output_section_row(section):
    output = {}
    output['Section'] = '%s %s' % (section['Number'], section['Type'])
    output['Days/Times'] = section['Days/Times']
    output['Location']  = section['Location']
    # separate intructors with ', ' instead of '\n'
    output['Instructor'] = ', '.join(section['Instructor'].split('\n'))
    #print output['Instructor']
    output['Class'] = section['Class']
    return output

def format_sections(sections):
    if len(sections) == 0:
        return str('')
    keys  = ['Section', 'Days/Times', 'Location', 'Instructor','Class']
    width = ['15%',     '25%',        '25%',      '25%',       '10%'  ]
    html = '<table class="course-data">'
    # header row
    html += '<tr>'
    for w, k in zip(width, keys):
        html += '<th style="width: %s;">%s</th>' % (w, k)
    html += '</tr>'
    # data rows
    for section in sections:
        output = output_section_row(section)
        html += '<tr>'
        for k in keys:
            if output[k]:
                html += '<td>%s</td>' % output[k]
            else:
                html += '<td>&nbsp;</td>'
        html += '</tr>'
    html += '</table>'
    #print html
    return html

def format_schedule(c):
    html = format_sections([c['Section']])
    # Add section course units and section status information
    html += '<table class="course-data" style="width= 50%">'
    # header row
    html += '<tr>'
    html += '<th style="width:20%;">Units</th>'
    html += '<th style="width:80%;">Enrollment Status</th>'
    html += '</tr>'
    # data row
    html += '<tr>'
    html += '<td>%s</td>' % c['Course']['Units']
    html += '<td>%s</td>' % c['Section']['Status']
    html += '</tr>'
    html += '</table>'
    # escape dollar sign to avoid collision with MathJax
    return html.replace('$', '\$')

def format_notes(course):
    html = ''
    keys = ['Prerequisites', 'Description', 'Office', 'Office Hours', 'Required Text',
            'Recommended Reading', 'Grading', 'Homework', 'Course Webpage']
    for k in keys:
        if k in course and course[k]:
            html += '<p class="course-data"><strong>%s:</strong>&nbsp;%s</p>' % (k, course[k])
        else:
            html += '<p class="course-data"><strong>%s:</strong>&nbsp;</p>' % k
    # escape dollar sign to avoid collision with MathJax
    return html.replace('$', '\$')

def output_class(c):
    o = {}
    o['Course Number'] = c['Course']['Number']
    o['Section'] = '%s %s' % (c['Section']['Number'], c['Section']['Type'])
    o['Sort Key'] = c['Section']['Sort Key']
    o['Course Title'] = c['Course']['Title']
    o['Days/Time'] = c['Section']['Days/Times']
    o['Location']  = c['Section']['Location']
    o['Instructor'] = c['Section']['Instructor']
    o['Course Control Number'] = c['Section']['Class']
    o['Schedule Info'] = format_schedule(c)
    if 'Discussions' in c:
        o['Sections'] = format_sections(c['Discussions'])
    else:
        o['Sections'] = ''
    o['Notes'] = format_notes(c['Course'])
    return o

if __name__ == '__main__':
    from optparse import OptionParser
    from csv import writer
    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-d', '--dept', dest = 'dept', default = 'MATH',
                      help = 'department abbreviation, default MATH')
    parser.add_option('-t', '--term', dest = 'term_id', default = '2198',
                      help = 'term id, e.g. 2198')
    parser.add_option('-p', '--number-of-pages', type = 'int', dest = 'number_of_pages', default = 5,
                      help = 'number of pages, e.g. 1')
    parser.add_option('-s', '--page-size', type = 'int', dest = 'page_size', default = 100,
                      help = 'page number, e.g. 100 (maximum 400)')
    parser.add_option('-e', '--exclude', dest = 'exclude', default = 'IND,COL',
                      help = 'comma separated section types to be excluded from search results, default "IND,COL"')
    parser.add_option('-o', '--output', dest = 'outputfile', default = 'classes.csv',
                      help = 'name of output file in csv format, default "classes.csv"')
    (options, args) = parser.parse_args()
    classes = get_classes(options.dept, options.term_id, options.number_of_pages, options.page_size, options.exclude)
    # output keys
    keys = ['Course Number', 'Section', 'Sort Key', 'Course Title', 'Days/Time', 'Location',
            'Instructor', 'Course Control Number', 'Schedule Info', 'Sections', 'Notes']
    with open(options.outputfile, 'w') as f:
        w = writer(f)
        w.writerow(keys)
        for c in classes:
            o = output_class(c)
            r = []
            for k in keys:
                r += [o[k]]
            #print r
            w.writerow(r)
