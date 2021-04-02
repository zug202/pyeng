import re
import glob
import sys

def cfg_list(sh_nve_outputs, regex):
#creating a list of show_nve_vni files for room
    room_outputs = []
    for output in sh_nve_outputs:
        if re.search(regex, output) is not None:
            room_outputs.append(re.search(regex, output).group())
    return room_outputs

def parse_sh_nve(site_outputs, mpod_outputs, mpod_bg_outputs, path):
# regex that cover L2vni with mcast, Up state
#Interface VNI      Multicast-group   State Mode Type [BD/VRF]      Flags
#--------- -------- ----------------- ----- ---- ------------------ -----
#nve1      [2010012]  [225.1.0.1]         Up    CP   L2 [12]            MS-IR

    sh_nve_regex = (".* +(?P<l2vni>\d+) +.* +(?P<mcast>\d+\.\d+\.\d+\.\d+) +.*Up +.*L2 +.*\[(?P<vlan>\d+)\]")
# creating a list of tuples (vni:vlan) for site
    l2vni_site = []
    l2vni_mcast = {}
    for filename in site_outputs:
        with open(path + '/' + filename) as f:
            match_site = re.finditer(sh_nve_regex, f.read())
            if (match_site):
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
            if (match_mpod):
                for m in match_mpod:
                    l2vni_mpod.append((m.group('l2vni'), m.group('vlan')))

# creating a list of tuples (vni:vlan) for mpod_bg
    l2vni_mpod_bg = []
    for filename in mpod_bg_outputs:
        with open(path + '/' + filename) as f:
            match_mpod_bg = re.finditer(sh_nve_regex, f.read())
            if (match_mpod_bg):
                for m in match_mpod_bg:
                    l2vni_mpod_bg.append((m.group('l2vni'), m.group('vlan')))
# creating a set for list of tuples (vni:vlan) for mpod_bg
    l2vni_mpod_bg_set = set(l2vni_mpod_bg)
# creating a set for list of tuples (vni:vlan) for mpod
    l2vni_mpod_set = set(l2vni_mpod)
# finding set intersection between site and mpod
    l2vni_site_mpod_list = l2vni_site_set.intersection(l2vni_mpod_set)
    l2vni_site_bg_list = l2vni_site_set.intersection(l2vni_mpod_bg_set)
    l2vni_mpod_list_unsorted = l2vni_site_mpod_list.union(l2vni_site_bg_list)
    l2vni_mpod_list = sorted(l2vni_mpod_list_unsorted)
# finding set difference between intersection(site&mpod) and bg
    bg_vni_list_unsorted = l2vni_mpod_bg_set.difference(l2vni_mpod_list_unsorted)
# finding overlapping vni between site&mpod and bg
    bg_vni_overlap_list = []
    site_vni_overlap_list = []
    for site_vni_vlan in l2vni_mpod_list:
        for bg_vni_vlan in bg_vni_list_unsorted:
            if site_vni_vlan[0] in bg_vni_vlan[0]:
                site_vni_overlap_list.append((site_vni_vlan[0], site_vni_vlan[1]))
                bg_vni_overlap_list.append((bg_vni_vlan[0], bg_vni_vlan[1]))
    print('bg overlapping:\n')
    print(sorted(bg_vni_overlap_list))
    print('\n')
    print('site overlapping:\n')
    print(sorted(site_vni_overlap_list))
    print('\n')

    bg_set_vni = []
    for vni_vlan in bg_vni_overlap_list:
        bg_set_vni.append(vni_vlan[0])

    ag_set_vni = []
    for vni_vlan in l2vni_mpod_list:
        ag_set_vni.append(vni_vlan[0])

    bg_vni_list = []
    for vni in ag_set_vni:
        if vni not in bg_set_vni:
            for vni_vlan in l2vni_mpod_list:
                if vni_vlan[0] == vni:
                    bg_vni_list.append(vni_vlan)

# writing config to file for BG
    with open(path + '/pre_bg_l2_vni.txt', 'w') as bg_l2_vni:
        for vni_vlan in bg_vni_list:
            template_bg = (
                f"vlan {vni_vlan[1]}\n"
                f" vn-segment {vni_vlan[0]}\n"
                "\n"
                "evpn\n"
                f" vni {vni_vlan[0]} l2\n"
                "  rd auto\n"
                f"  route-target import 64998:{vni_vlan[0]}\n"
                f"  route-target export 64998:{vni_vlan[0]}\n"
                "\n"
                "interface nve1\n"
                f" member vni {vni_vlan[0]}\n"
                "  multisite ingress-replication\n"
                f"  mcast-group {l2vni_mcast[vni_vlan[0]]}\n"
                "\n"
            )
            bg_l2_vni.write(template_bg)

# writing config to file for AG (pre-works)
    with open(path + '/pre_ag_l2_vni.txt', 'w') as ag_l2_vni:
        for vni_vlan in l2vni_mpod_list:
            template_ag_l2vni = (
                f"vlan {vni_vlan[1]}\n"
                f" vn-segment {vni_vlan[0]}\n"
                "\n"
                "evpn\n"
                f" vni {vni_vlan[0]} l2\n"
                "  rd auto\n"
                f"  route-target import 64998:{vni_vlan[0]}\n"
                f"  route-target export 64998:{vni_vlan[0]}\n"
                "\n"
            )
            ag_l2_vni.write(template_ag_l2vni)

# writing config to file for AG nve without MS-IR (main-works)
    with open(path + '/mw1-bgw_l2_vni_without_MS-IR.txt', 'w') as ag_l2_vni_nve:
        for vni_vlan in l2vni_mpod_list:
            template_ag_nve = (
                "interface nve1\n"
                f" member vni {vni_vlan[0]}\n"
                f"  mcast-group {l2vni_mcast[vni_vlan[0]]}\n"
                "\n"
            )
            ag_l2_vni_nve.write(template_ag_nve)

# writing config to file for AG adding MS-IR (main-works)
    with open(path + '/mw1-bgw_l2_vni_with_MS-IR.txt', 'w') as ag_l2_vni_ms_ir:
        for vni_vlan in l2vni_mpod_list:
            template_ag_ms_ir = (
                "interface nve1\n"
                f" member vni {vni_vlan[0]}\n"
                "  multisite ingress-replication\n"
                "\n"
            )
            ag_l2_vni_ms_ir.write(template_ag_ms_ir)

# writing vni:vlan to file
    with open(path + '/stretched_vni_list.txt', 'w') as vni_list:
        for vni_vlan in l2vni_mpod_list:
            vni_list.write('{},{}\n'.format(vni_vlan[0], vni_vlan[1]))

    with open(path + '/bg_vni_list.txt', 'w') as vni_list:
        for vni_vlan in bg_vni_list:
            vni_list.write('{},{}\n'.format(vni_vlan[0], vni_vlan[1]))

    return l2vni_mpod_list, bg_vni_list

def main():
    path = sys.argv[1]
    sh_nve_outputs = glob.glob(path + '/*.txt')
    site = cfg_list(sh_nve_outputs, 'SKO-DATA-AC-012.*')
    room_11 = cfg_list(sh_nve_outputs, 'SKO-DATA-AC-011.*')
    room_md = cfg_list(sh_nve_outputs, 'SKO-DATA-AC-MD.*')
    mpod_bl = cfg_list(sh_nve_outputs, 'SKO-DATA-BL.*')
    mpod_bg = cfg_list(sh_nve_outputs, 'SKO-DATA-BG-[MD1|MD2].*INT.*')
    mpod = room_11+room_md+mpod_bl
    parse_sh_nve(site, mpod, mpod_bg, path)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print('Please check input data')
