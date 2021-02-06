file = 'Rpython/pyneg-tasks/exercises/07_files/CAM_table.txt'
f = open(file)
list = f.readlines()
for word in list[6:]:
    vlan, mac, dyn, intf = word.split()
    print("{:4}   {}  {}".format(vlan, mac, intf))
