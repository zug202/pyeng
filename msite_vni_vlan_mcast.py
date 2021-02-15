import re
import glob
import sys

def cfg_list(sh_nve_outputs,regex):
#creating a list of show_nve_vni files for room
    room_outputs = []
    for output in sh_nve_outputs:
        if re.search(regex,output) != None:
            room_outputs.append(re.search(regex,output).group())
    return room_outputs

def parse_sh_nve(site_outputs,mpod_outputs,path):
# regex that cover L2vni with mcast, Up state
    sh_nve_regex = (".* +(?P<l2vni>\d+) +.* +(?P<mcast>\d+\.\d+\.\d+\.\d+) +.*Up +.*L2 +.*\[(?P<vlan>\d+)\]")
# creating a list of tuples (vni:vlan) for site
    l2vni_site = []
    l2vni_mcast = {}
    for filename in site_outputs:
        with open(path + '/' + filename) as f:
            match_site = re.finditer(sh_nve_regex, f.read())
            for m in match_site:
                l2vni_site.append((m.group('l2vni'), m.group('vlan')))
# creating a dict (vni:mcast) mapping for cfg generation
                l2vni_mcast.update({m.group('l2vni') : m.group('mcast')})
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
    result_unsorted = l2vni_site_set.intersection(l2vni_mpod_set)
    result = sorted(result_unsorted)
# cfg template
    template = (
    "vlan {}\n"
    " vn-segment {}\n"
    "\n"
    "interface nve1\n"
    " member vni {}\n"
    "  multisite ingress-replication\n"
    "  mcast-group {}\n"
    "\n"
    )
# writing config to file
    with open(path + '/bgw_l2_vni.txt', 'w') as bgw_l2_vni:
        for tuple in result:
            bgw_l2_vni.write(template.format(tuple[1],tuple[0],tuple[0],l2vni_mcast[tuple[0]]))

# writing vni:vlan to file
    with open(path + '/vni_list.txt', 'w') as vni_list:
        for vni_vlan in result:
            print(vni_vlan)
            vni_list.write('{},{}\n'.format(vni_vlan[0],vni_vlan[1]))

    return result

def main():
    path = sys.argv[1]
    sh_nve_outputs = glob.glob(path + '/*.txt')
    site = cfg_list(sh_nve_outputs,'SKO-DATA-AC-012.*')
    room_11 = cfg_list(sh_nve_outputs,'SKO-DATA-AC-011.*')
    room_md = cfg_list(sh_nve_outputs,'SKO-DATA-AC-MD.*')
    mpod_bl = cfg_list(sh_nve_outputs,'SKO-DATA-BL.*')
    mpod = room_11+room_md+mpod_bl
    parse_sh_nve(site,mpod,path)



if __name__ == "__main__":

    try:
        main()
    except Exception:
        print('Please check input data')
