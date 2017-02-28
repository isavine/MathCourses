import requests
import json

def get_class(dept, app_id, app_key):
    #params = {'app_id': app_id,'app_key': app_key}
    #json_response = response.json()
    url = 'https://apis.berkeley.edu/sis/v1/classes/sections?term-id=2172&print-in-schedule=true&section-number=001&subject-area-code='+dept
    #print-in-schedule=true : To exclude cancelled classes. 
    #section-number=001 : To get only unique cs-course-id. Assuming each offered course has Section 1 (uncancelled). 
    #This would probably cause a bug if Section 1 is cancelled.
    headers = {'Accept': 'application/json', 'app_id': app_id, 'app_key': app_key}

    r = requests.get(url, headers=headers)
    #print r.json()
    s = r.json()['apiResponse']['response']
    #print len(s['classSections'])
    #print s['classes'][0]['number']
    return s['classSections']
    
def get_sections(courseid, app_id, app_key):
    url = 'https://apis.berkeley.edu/sis/v1/classes/sections?term-id=2172&print-in-schedule=true&cs-course-id='+courseid
    headers = {'Accept': 'application/json', 'app_id': app_id, 'app_key': app_key}

    r = requests.get(url, headers=headers)
    #print r.json()
    s = r.json()['apiResponse']['response']
    return s['classSections']

if __name__ == '__main__':
    from optparse import OptionParser

    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-d', '--dept', dest='dept', default='MATH',
                      help='department abbreviation, e.g. MATH')
    parser.add_option('-f', '--file', dest='file', default='class.json',
                      help='name of output file (in json format)')
    (options, args) = parser.parse_args()
    # API ID and Key
    class_app_id = 'app_id'
    class_app_key = 'app_key'
    # base URL for searching course catalog
    #baseurl = 'https://apis.berkeley.edu/sis/v1/classes?term-id=2172&subject-area-code=MATH'
    dept = options.dept
    # output file
    f = open(options.file, 'wb')

    c = get_class(dept, class_app_id, class_app_key)
    json.dump(c, f, sort_keys=True, indent=4)
    f.close()
    
    f = open('sections.json', 'wb')

    u = get_sections('114496', class_app_id, class_app_key) #1A
    #u = get_sections('114564', class_app_id, class_app_key) #198BC No assignedInstructors
    json.dump(u, f, sort_keys=True, indent=4)
    f.close()