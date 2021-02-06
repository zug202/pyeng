import re
import glob
import sys


def room_12_list(sh_nve_outputs):
#creating a list of show_nve_vni files for room 12
    room_12_outputs = []
    for output in sh_nve_outputs:
        if re.search('SKO-DATA-AC-012.*', output) != None:
            room_12_outputs.append(re.search('SKO-DATA-AC-012.*', output).group())
    return room_12_outputs

def room_11_list(sh_nve_outputs):
# creating a list of show_nve_vni files for room 11
    room_11_outputs = []
    for output in sh_nve_outputs:
        if re.search('SKO-DATA-AC-011.*', output) != None:
            room_11_outputs.append(re.search('SKO-DATA-AC-011.*', output).group())
    return room_11_outputs

def room_md_list(sh_nve_outputs):
# creating a list of show_nve_vni files for room md
    room_md_outputs = []
    for output in sh_nve_outputs:
        if re.search('SKO-DATA-AC-MD.*', output) != None:
            room_md_outputs.append(re.search('SKO-DATA-AC-MD.*', output).group())
    return room_md_outputs

def room_bl_list(sh_nve_outputs):
# creating a list of show_nve_vni files for mpod bl
    bl_outputs = []
    for output in sh_nve_outputs:
        if re.search('SKO-DATA-BL.*', output) != None:
            bl_outputs.append(re.search('SKO-DATA-BL.*INT-show.*', output).group())
    return bl_outputs

def parse_sh_nve(site_outputs,mpod_outputs,path):
# regex that cover L2vni with mcast, Up state
    sh_nve_regex = (".* +(?P<l2vni>\d+) +.*\d+\.\d+\.\d+\.\d+ +.*Up +.*L2 +.*\[(?P<vlan>\d+)\]")
# creating a list of tuples (vni:vlan) for site
    l2vni_site = []
    for filename in site_outputs:
        with open(path + '/' + filename) as f:
            match_site = re.finditer(sh_nve_regex, f.read())
            for m in match_site:
                l2vni_site.append((m.group('l2vni'), m.group('vlan')))
# creating a set for list of tuples (vni:vlan) for site
    l2vni_site_set = set(l2vni_site)
# creating a list of tuples (vni:vlan) for mpod
    l2vni_mpod = []
    for filename in mpod_outputs:
        with open(path + '/' + filename) as f:
            match_mpod = re.finditer(sh_nve_regex, f.read())
            for m in match_mpod:
                l2vni_mpod.append((m.group('l2vni'), m.group('vlan')))
# creating a set for list of tuples (vni:vlan) for mpod
    l2vni_mpod_set = set(l2vni_mpod)
# finding set intersection between site and mpod
    result = l2vni_site_set.intersection(l2vni_mpod_set)
# cfg template
    template = (
    "vlan {}\n"
    " vn-segment {}\n"
    )
# writing config to file
    with open(path + '/bgw_l2_vni.txt', 'w') as bgw_l2_vni:
        for tuple in result:
            bgw_l2_vni.write(template.format(tuple[1],tuple[0]))

# writing vni:vlan to file
    with open(path + '/vni_list.txt', 'w') as vni_list:
        for vni_vlan in result:
            print(vni_vlan)
            vni_list.write('{},{}\n'.format(vni_vlan[0],vni_vlan[1]))

    return result

def main():
    path = sys.argv[1]
    sh_nve_outputs = glob.glob(path + '/*.txt')
    site = room_12_list(sh_nve_outputs)
    mpod = room_11_list(sh_nve_outputs)+room_md_list(sh_nve_outputs)+room_bl_list(sh_nve_outputs)
    parse_sh_nve(site,mpod,path)



if __name__ == "__main__":

    try:
        main()
    except Exception:
        print('Please check input data')
