ospf = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/07_files/ospf.txt'
route_template = '''
Prefix          {}
AD/Metric       {}
Next-Hop        {}
Last-Update     {}
Interface       {}
'''
#print (route_template.format('1.1.1.1', '110', '2.2.2.2', '1D', 'fa0/1'))
with open(ospf) as src:
    for line in src:
        line_list=line.split()
        #print(line_list)
        print(route_template.format(line_list[1], line_list[2].strip('[]'), line_list[4].strip(','), line_list[5].strip(','), line_list[6]))
