#!/bin/sh 
cd `dirname $0`
[ -r venv/bin/activate ] && . venv/bin/activate
d=`date '+%d'`
python get_classes.py -t 2252 -o spring-classes-$d.json
python write_csv.py -t 2252 -o spring-classes-$d.csv
python get_classes.py -t 2255 -o summer-classes-$d.json
python write_csv.py -t 2255 -o summer-classes-$d.csv
python get_classes.py -t 2258 -o fall-classes-$d.json
python write_csv.py -t 2258 -o fall-classes-$d.csv
find . -maxdepth 1 -name \*-[0-3][0-9].\* -mtime +30 | xargs -r rm
