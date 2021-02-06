file = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/07_files/CAM_table.txt'
f = open(file)
list = f.readlines()
dict_vlan = {}
dict_new = {}
for word in list[6:]:
    vlan, mac, dyn, intf = word.split()
    dict_vlan[int(vlan)] = mac, intf
#print(dict_vlan)
for key in sorted(dict_vlan.keys()):
    dict_new[key] = dict_vlan[key]
    print("{:4}".format(key) +' %s   %s' % dict_vlan[key])