import re
import glob

sh_nve_output = '/Users/atunin/Downloads/RawInventory_Export_2021-Feb-04_23-53-59/CLI/show_nve_vni/SKO-DATA-AC-011-E18-01-INT-show_nve_vni.txt'
sh_nve_outputs = glob.glob('/Users/atunin/Downloads/RawInventory_Export_2021-Feb-04_23-53-59/CLI/show_nve_vni/*.txt')

room_12_outputs = []
for output in sh_nve_outputs:
    if re.search('SKO-DATA-AC-012.*', output) != None:
       room_12_outputs.append(re.search('SKO-DATA-AC-012.*', output).group())


sh_nve_regex = (".* +(?P<l2vni>\d+) +.* +(?P<mcast>\d+\.\d+\.\d+\.\d+) +.*Up +.*L2 +.*\[(?P<vlan>\d+)\]")
with open(sh_nve_output) as f:
    match = re.finditer(sh_nve_regex, f.read())

l2vni_room_12 = []
l2vni_mcast = {}
for m in match:
    l2vni_room_12.append((m.group('l2vni'), m.group('vlan')))
    l2vni_mcast.update({m.group('l2vni') : m.group('mcast')})
print(l2vni_mcast)
l2vni_room_12_set = set(l2vni_room_12)
print(l2vni_room_12_set)