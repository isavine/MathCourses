from get_schedule import get_all_sections
from scrape_catalog import scrape_catalog

def aggregate(classes):
    '''Aggregate discussion sections with corresponding lectures'''
    # create a dictionary out of class sections by sort key
    keys = [c['Section']['Sort Key'] for c in classes]
    dc = dict(zip(keys, classes))
    for k in sorted(keys):
        c = dc[k]
        if c['Section']['Type'] != 'DIS' and c['Section']['Type'] != 'WBD':
           dc[k] = c
        else:
           pk = k[:-2].ljust(11,'0')
           if pk in dc:
              if not 'Discussions' in dc[pk]:
                  dc[pk]['Discussions'] = []
              # the duscussion sort key is no longer needed
              del c['Section']['Sort Key']
              dc[pk]['Discussions'] += [c['Section']]
              del dc[k]
    classes = [dc[k] for k in sorted(dc.keys())]
    return classes

def add_catalog_info(classes, catalog):
    '''Add description and other info from course catalog'''
    add_keys = ['Description', 'Prerequisites', 'Grading', 'Units']
    # create a dictionary out of catalog courses by course number
    keys = [c['Number'] for c in catalog]
    cat_info = dict(zip(keys, catalog))
    for c in classes:
        # lookup key for catalog courses
        cat_key = c['Course']['Number']
        # loop through additional keys
        for add_key in add_keys:
            if cat_key in cat_info and add_key in cat_info[cat_key]:
                # course listed in catalog and contains additional key
                c['Course'][add_key] = cat_info[cat_key][add_key]
            else:
                c['Course'][add_key] = ''
        # done with adding catalog info
    return classes

def get_classes(dept, term_id, number_of_pages, page_size, exclude):
    '''Get class schedule in the format compatible with Math website'''
    classes = get_all_sections(dept, term_id, number_of_pages, page_size, exclude)
    if classes and len(classes) > 0:
        classes = aggregate(classes)
        catalog = scrape_catalog(dept)
        classes = add_catalog_info(classes, catalog)
        return classes
    else:
        return

if __name__ == '__main__':
    '''Get department class schedule for specified semester'''
    from optparse import OptionParser
    from json import dump
    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-d', '--dept', dest = 'dept', default = 'MATH',
                      help = 'department abbreviation, default MATH')
    parser.add_option('-t', '--term', dest = 'term_id', default = '2198',
                      help = 'term id, e.g. 2198')
    parser.add_option('-p', '--number-of-pages', dest = 'number_of_pages', default = 2,
                      help = 'number of pages, e.g. 1')
    parser.add_option('-s', '--page-size', dest = 'page_size', default = 400,
                      help = 'page number, e.g. 100 (maximum 400)')
    parser.add_option('-e', '--exclude', dest = 'exclude', default = 'IND,COL',
                      help = 'comma separated section types to be excluded from search results, default "IND,COL"')
    parser.add_option('-o', '--output', dest = 'outputfile', default = 'classes.json',
                      help = 'name of output file in json format, default "classes.json"')
    (options, args) = parser.parse_args()
    classes = get_classes(options.dept, options.term_id, options.number_of_pages, options.page_size, options.exclude)
    if classes and len(classes) > 0:
        print '%d aggregated class(es) processed' % len(classes)
        with open(options.outputfile, 'w') as f:
            dump(classes, f, sort_keys = True, indent = 2)
        print 'see output in "%s"' % options.outputfile
    else:
        print 'no classes found (no output)'
