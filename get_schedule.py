#import urllib
#import pipes
import re
import json
import get_class
from datetime import datetime

# keys for parsing the schedule page
keys = ['Course', 'Course Title', 'Location', 'Instructor', 'Course Control Number',
        'Units/Credit', 'Final Exam Group', 'Session Dates', 'Restrictions', 'Summer Fees',
        'Note', r'Enrollment on \d\d/\d\d/\d\d']
#keys = ['Course', 'Course Title', 'Location', 'Instructor', 'Course Control Number',
#        'Session Dates']
        
def get_all_courses(classes, app_id, app_key):
    courses = get_courses(classes, app_id, app_key)            
    for c in courses:
        c = add_sort_key(c)
        #print c['Course']
    comment = str(len(courses)) + ' courses matched the schedule for Spring 2017'
    return {'Comment': comment, 'Courses': courses}

#def course_info(nCourse, block_num, split_courses, data): #

def add_sort_key(course):
    r = r'(^\D?)(\d+)(\D*)$'
    i = 0
    n = course['Course']['Number']
    m = re.match(r, n)
    m1 = m.group(1).rjust(1, ' ')
    m2 = m.group(2).rjust(3, '0')
    m3 = m.group(3).ljust(2, ' ')
    s = course['Course']['Section']
    if course['Course']['Type'] == 'P':
        if not '-' in s:
            s = s.ljust(5, '0')
        else:
            s = s.ljust(5, ' ')
    if course['Course']['Type'] == 'S':
        s = s.rjust(5, '0')
    course['Course']['Sort Key'] = m2 + m3 + m1 + s
    return course

def get_courses(classes, app_id, app_key):
    courses = []
    #k = 0
    #keep track of the block of data we are working with starting from 0
    #data[0] - block of 3; data[1] - block of 4
    for x in classes:
        sections = get_class.get_sections(x['class']['course']['identifiers'][0]['id'], app_id, app_key) 
        #I have to call classes/sections for each course because for some reason I couldn't query all classes and sections from /sections at once.
        for y in sections:
            course = {}
        
            d = {}
            #(d['Number'], d['Section'], d['Kind']) = (split_courses[3*nCourse+1],data[0][3*(nCourse+nSec)+1],data[0][3*(nCourse+nSec)+2])
            d['Number'] = y['class']['course']['catalogNumber']['formatted']
            d['Section'] = y['class']['number']
            d['Kind'] = y['component']['code']
            #d['Type'] = x.['instructionMode']['code']   --- instructionMode can only be found for main classes not for discussion sections
            #Assuming 'DIS' is of type 'S'; else 'P'
            if d['Kind'] == 'DIS':
                d['Type'] = 'S'
            else:
                d['Type'] = 'P'
            #d['Department'] = x.['subjectArea']['description'] <-- return 'Mathematics'
            d['Department'] = 'MATHEMATICS'
        
            course['Course'] = d
            #skipping 'IND' courses
            if course['Course']['Kind'] == 'IND' or course['Course']['Kind'] == 'COL': #'SEM' shouldn't be omitted.
                #k += 1
                continue
            course['Course Title'] = y['class']['course']['title']
            if 'meetings' in y:
                #course['Days/Time'] = y['meetings'][0]['meetsDays'] + ' ' + y['meetings'][0]['startTime'] + ' - ' + y['meetings'][0]['endTime']
                #Time in 24:00:00
                start = datetime.strptime(y['meetings'][0]['startTime'], '%H:%M:%S')
                end = datetime.strptime(y['meetings'][0]['endTime'], '%H:%M:%S')
                course['Days/Time'] = y['meetings'][0]['meetsDays'] + ' ' + start.strftime("%I:%M%p") + ' - ' + end.strftime("%I:%M%p")
                course['Location'] = y['meetings'][0]['location']['description']
                if 'assignedInstructors' in y['meetings'][0]:
                    if 'names' in y['meetings'][0]['assignedInstructors'][0]['instructor']:
                        course['Instructor'] = y['meetings'][0]['assignedInstructors'][0]['instructor']['names'][0]['givenName'] + ' ' + y['meetings'][0]['assignedInstructors'][0]['instructor']['names'][0]['familyName']
                    else:
                        course['Instructor'] = ''
                else:
                    course['Instructor'] = ''
            else:
                course['Days/Time'] = 'TBA'
                course['Location'] = 'TBA'
                course['Instructor'] = ''
            course['Course Control Number'] = y['id'] #aka class section id
            course['Units/Credit'] = y['class']['allowedUnits']['forAcademicProgress'] #option minimum/maximum/forAcademicProgress/forFinancialAid
            course['Final Exam Group'] = "" #probably not available via api. See http://registrar.berkeley.edu/sis-SC-message
            #Final Exam Info is supposed to be in classes/sections  ['exam'] but it's currently not available?
            #course['Session Dates'] = ""
            course['Restrictions'] = ""
            #course['Summer Fees'] = ""
            course['Note'] = ""
            course['Enrollment'] = y['enrollmentStatus']['status']['description'] 
            #enrollmentStatus: enrolledCount, waitlistedCount, minEnroll, maxEnroll, maxWaitlist
            courses = courses + [course]
            #k += 1
    return courses
    
if __name__ == '__main__':
    from optparse import OptionParser

    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-d', '--dept', dest='dept', default='MATH',
                      help='department abbreviation, e.g. MATH')
    parser.add_option('-t', '--term', dest='term', default='FL',
                      help='term/semester code (FL or SP or SU)')
    parser.add_option('-f', '--file', dest='file', default='schedule.json',
                      help='name of output file (in json format)')
    #parser.add_option('-s', '--searchresults', dest='searchresults',
    #                  help='name of search results file (in html format)')
    (options, args) = parser.parse_args()
    # API ID and Key
    class_app_id = 'app_id'
    class_app_key = 'app_key'
    #baseurl = 'https://apis.berkeley.edu/sis/v1/classes?term-id=2172&subject-area-code='
    dept = options.dept
    
    import get_class
    classes = get_class.get_class(dept, class_app_id, class_app_key)
    #print classes[0]
    #result = get_courses(classes)
    
    # Output file: searchresults.html -> searchresults.json
    #f = open(options.searchresults.split('.')[0]+'.json', 'wb')
    f = open(options.file, 'wb')
    schedule = get_all_courses(classes, class_app_id, class_app_key)
    json.dump(schedule, f, sort_keys=True, indent=4)
    f.close()