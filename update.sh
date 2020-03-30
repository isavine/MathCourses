#!/bin/sh 
cd `dirname $0`
[ -r venv/bin/activate ] && . venv/bin/activate
d=`date '+%d'`
python get_schedule.py -t 2202 -o spring-sections-$d.json
python write_csv.py -t 2202 -o spring-classes-$d.csv
python get_schedule.py -t 2205 -o summer-sections-$d.json
python write_csv.py -t 2205 -o summer-classes-$d.csv
python get_schedule.py -t 2208 -o fall-sections-$d.json
python write_csv.py -t 2208 -o fall-classes-$d.csv
find . -name \*-[0-3][0-9].\* -mtime +3 | xargs -r rm
