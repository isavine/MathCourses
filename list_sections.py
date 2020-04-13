'''List sections from the output of get_schedule.py'''
from __future__ import print_function
import sys
import json

sections = json.load(sys.stdin)
for s in sections:
    print(s['Course']['Department'], s['Course']['Number'], s['Section']['Type'], s['Section']['Number'], s['Section']['Class'])
print('{} section(s) found'.format(len(sections)), file = sys.stderr)
