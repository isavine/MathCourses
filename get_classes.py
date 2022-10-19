from get_schedule import get_all_sections
from scrape_catalog import scrape_catalog

def aggregate(classes):
    '''Aggregate discussion sections with corresponding lectures'''
    # sort classes (a.k.a. sections) by sort key
    classes.sort(key = lambda c: c['Section']['Sort Key'])
    output = []
    index = -1
    for c in classes:
        if c['Section']['Primary']:
            index += 1
            output.append(c) # primary class
        elif c['Section']['Type'] == 'DIS' or c['Section']['Type'] == 'WBD':
            if not 'Discussions' in output[index]:
                output[index]['Discussions'] = [] # create list of discussions
            del c['Section']['Sort Key'] # discussion sort key is no longer needed
            output[index]['Discussions'].append(c['Section'])
    return output

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
    #print(len(classes))
    if classes and len(classes) > 0:
        classes = aggregate(classes)
        catalog = scrape_catalog(dept)
        classes = add_catalog_info(classes, catalog)
        return classes
    else:
        return []

if __name__ == '__main__':
    '''Get department class schedule for specified semester'''
    from optparse import OptionParser
    from json import dump
    usage = 'usage: %prog options'
    parser = OptionParser(usage)
    parser.add_option('-d', '--dept', dest = 'dept', default = 'MATH',
                      help = 'department abbreviation, default MATH')
    parser.add_option('-t', '--term', dest = 'term_id', default = '2232',
                      help = 'term id, e.g. 2232')
    parser.add_option('-p', '--number-of-pages', type = 'int', dest = 'number_of_pages', default = 10,
                      help = 'number of pages, e.g. 10 (drfault 10)')
    parser.add_option('-s', '--page-size', type = 'int', dest = 'page_size', default = 100,
                      help = 'page size, e.g. 100 (default maximum 100)')
    parser.add_option('-e', '--exclude', dest = 'exclude', default = 'IND,COL',
                      help = 'comma separated section types to be excluded from search results, default "IND,COL"')
    parser.add_option('-o', '--output', dest = 'outputfile', default = 'classes.json',
                      help = 'name of output file in json format, default "classes.json"')
    (options, args) = parser.parse_args()
    classes = get_classes(options.dept, options.term_id, options.number_of_pages, options.page_size, options.exclude)
    if classes and len(classes) > 0:
        print('{:d} aggregated class(es) processed'.format(len(classes)))
        with open(options.outputfile, 'w') as f:
            dump(classes, f, sort_keys = True, indent = 2)
        print('see output in "{}"'.format(options.outputfile))
    else:
        print('no classes found (no output)')
