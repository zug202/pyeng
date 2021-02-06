vlan_usr = int(input('vvedite vlan: '))
file = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/07_files/CAM_table.txt'
f = open(file)
list = f.readlines()
dict_vlan = {}
for word in list[6:]:
    vlan, mac, dyn, intf = word.split()
    dict_vlan[int(vlan)] = mac, intf
print("{:4}".format(vlan_usr) +' %s   %s' % dict_vlan[vlan_usr])
