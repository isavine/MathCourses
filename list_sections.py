'''List sections from the output of get_schedule.py'''
from __future__ import print_function
import sys
import json
import re

sections = json.load(sys.stdin)
sections.sort(key = lambda s: s['Section']['Sort Key'])
primary_num = 0
for s in sections:
    course_num = s['Course']['Number']
    r = r'(^\D?)(\d+)(\D*)$'
    m = re.match(r, course_num)
    m1 = m.group(1)
    m2 = m.group(2)
    m3 = m.group(3)
    just_num = (m1 + m2 + m3).ljust(6, ' ')
    if s['Section']['Primary']:
        primary = 'primary'
        primary_num += 1
    else:
        primary = ''
    print(s['Course']['Department'], just_num, s['Section']['Type'], s['Section']['Number'], s['Section']['Class'], primary)
print('{} section(s) found'.format(len(sections)), file = sys.stderr)
print('{} primary section(s) found'.format(primary_num), file = sys.stderr)
