import re
import glob
import sys

def cfg_list(sh_nve_outputs, regex):
#creating a list of show_nve_vni files for room:
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
#nve1      [2010013]  [UnicastBGP]         Up    CP   L2 [13]            MS-IR
    sh_nve_regex = (".* +(?P<l2vni>\d+) +.* +(?P<mcast>((\d+\.\d+\.\d+\.\d+)|(UnicastBGP))) +.*Up +.*L2 +.*\[(?P<vlan>\d+)\]")
# creating a list of tuples (vni:vlan) for site:
    l2vni_site = []
    l2vni_mcast = {}
    for filename in site_outputs:
        with open(path + '/' + filename) as f:
            match_site = re.finditer(sh_nve_regex, f.read())
            if (match_site):
                for m in match_site:
                    l2vni_site.append((m.group('l2vni'), m.group('vlan')))
# creating a dict (vni:mcast) mapping for cfg generation:
                    l2vni_mcast.update({m.group('l2vni') : m.group('mcast')})
# creating a set for list of tuples (vni:vlan) for site:
    l2vni_site_set = set(l2vni_site)
    #print(f"len(l2vni_site_set) = {len(l2vni_site_set)}")
# creating a list of tuples (vni:vlan) for mpod:
    l2vni_mpod = []
    for filename in mpod_outputs:
        with open(path + '/' + filename) as f:
            match_mpod = re.finditer(sh_nve_regex, f.read())
            if (match_mpod):
                for m in match_mpod:
                    l2vni_mpod.append((m.group('l2vni'), m.group('vlan')))
# creating a list of tuples (vni:vlan) for mpod_bg:
    l2vni_mpod_bg = []
    for filename in mpod_bg_outputs:
        with open(path + '/' + filename) as f:
            match_mpod_bg = re.finditer(sh_nve_regex, f.read())
            if (match_mpod_bg):
                for m in match_mpod_bg:
                    l2vni_mpod_bg.append((m.group('l2vni'), m.group('vlan')))
# creating a set for list of tuples (vni:vlan) for mpod_bg:
    l2vni_mpod_bg_set = set(l2vni_mpod_bg)
# creating a set for list of tuples (vni:vlan) for mpod:
    l2vni_mpod_set = set(l2vni_mpod)
# finding set intersection between site and mpod:
    l2vni_site_mpod_list = l2vni_site_set.intersection(l2vni_mpod_set)
    #print(f"len(l2vni_site_mpod) = {len(l2vni_site_mpod_list)}")
    l2vni_site_bg_list = l2vni_site_set.intersection(l2vni_mpod_bg_set)
    #print(f"len(l2vni_site_bg) = {len(l2vni_site_bg_list)}")
    l2vni_mpod_list_unsorted = l2vni_site_mpod_list.union(l2vni_site_bg_list)
    l2vni_mpod_list = sorted(l2vni_mpod_list_unsorted)
    #print(f"len(ag_vni_list) = {len(l2vni_mpod_list)}")
#dict for mpod vni_vlan
    l2vni_mpod_list_dict = dict(l2vni_mpod_list)
    print(f"len(l2vni_mpod_list_dict) = {len(l2vni_mpod_list_dict)}")
    #print(f"l2vni_mpod_list_dict = {l2vni_mpod_list_dict}")
#dict for bg vni_vlan
    l2vni_mpod_bg_dict = dict(l2vni_mpod_bg_set)
    #print(f"len(l2vni_mpod_bg_dict) = {len(l2vni_mpod_bg_dict)}")
    #print(f"l2vni_mpod_bg_dict = {l2vni_mpod_bg_dict}")
#finding bg_vni_vlan_set
    bg_overlap_dict = {}
    for vni_mpod,vlan_mpod in l2vni_mpod_list_dict.items():
        for vni_bg,vlan_bg in l2vni_mpod_bg_dict.items():
            if vni_bg == vni_mpod:
                bg_overlap_dict.update({vni_bg:vlan_bg})
    bg_overlap_dict_set = set(bg_overlap_dict.items())
    l2vni_mpod_list_dict_set = set(l2vni_mpod_list_dict.items())
# finding set difference between intersection(site&mpod) and bg:
    bg_vni_list_diff = bg_overlap_dict_set.difference(l2vni_mpod_list_dict_set)
    #print(f"bg_vni_list_diff= {bg_vni_list_diff}")
    print(f"len_bg_vni_list_diff = {len(bg_vni_list_diff)}")
    bg_vni_list_diff_dict = dict(bg_vni_list_diff)
    #print(f"bg_vni_list_diff_dict= {bg_vni_list_diff_dict}")
    l2vni_mpod_list_dict_with_mapping = l2vni_mpod_list_dict.copy()
    l2vni_mpod_list_dict_with_mapping.update(bg_vni_list_diff_dict)
    #print(f"l2vni_mpod_list_dict_with_mapping = {l2vni_mpod_list_dict_with_mapping}")
    print(f"l2vni_mpod_list_dict_with_mapping = {len(l2vni_mpod_list_dict_with_mapping)}")
    ag_vni_list = set(l2vni_mpod_list_dict_with_mapping.items())
# finding set difference between ag_vni_list and bg_vni_list:
    bg_vni_list = ag_vni_list.difference(bg_overlap_dict_set)
    #print(f"bg_overlap_dict = {bg_overlap_dict}")
    print(f"len_bg_overlap_dict = {len(bg_overlap_dict)}")
    #print(f"bg_vni_list= {bg_vni_list}")
    print(f"bg_vni_list = {len(bg_vni_list)}")

    return ag_vni_list, bg_vni_list, l2vni_mcast, bg_vni_list_diff

def generate_config(ag_vni_list, bg_vni_list, l2vni_mcast, bg_vni_list_diff, path):
# writing config to file for BG
    with open(path + '/pre_bg_l2_vni.ios', 'w') as bg_l2_vni:
        for vni_vlan in bg_vni_list:
            template_bg_ingress = (
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
                "  ingress-replication protocol bgp\n"
                "\n"
            )
            template_bg_mcast = (
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
            if l2vni_mcast[vni_vlan[0]] == 'UnicastBGP':
                bg_l2_vni.write(template_bg_ingress)
            else:
                bg_l2_vni.write(template_bg_mcast)
# writing config to file for AG (pre-works)
    with open(path + '/pre_ag_l2_vni.ios', 'w') as ag_l2_vni:
        for vni_vlan in ag_vni_list:
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
    with open(path + '/mw1-bgw_l2_vni_without_MS-IR.ios', 'w') as ag_l2_vni_nve:
        for vni_vlan in ag_vni_list:
            template_ag_nve_mcast = (
                "interface nve1\n"
                f" member vni {vni_vlan[0]}\n"
                f"  mcast-group {l2vni_mcast[vni_vlan[0]]}\n"
                "\n"
            )
            template_ag_nve_ingress = (
                "interface nve1\n"
                f" member vni {vni_vlan[0]}\n"
                "  ingress-replication protocol bgp\n"
                "\n"
            )
            if l2vni_mcast[vni_vlan[0]] == 'UnicastBGP':
                ag_l2_vni_nve.write(template_ag_nve_ingress)
            else:
                ag_l2_vni_nve.write(template_ag_nve_mcast)
# writing config to file for AG adding MS-IR (main-works)
    with open(path + '/mw1-bgw_l2_vni_with_MS-IR.ios', 'w') as ag_l2_vni_ms_ir:
        for vni_vlan in ag_vni_list:
            template_ag_ms_ir = (
                "interface nve1\n"
                f" member vni {vni_vlan[0]}\n"
                "  multisite ingress-replication\n"
                "\n"
            )
            ag_l2_vni_ms_ir.write(template_ag_ms_ir)
# writing vni:vlan to file
    template_write_to_file = (
        f"overlapping vni:\n {sorted(bg_vni_list_diff)}\n"
    )
    with open(path + '/ag_vni_list.ios', 'w') as vni_list:
        vni_list.write(template_write_to_file)
        for vni_vlan in ag_vni_list:
            vni_list.write('{},{}\n'.format(vni_vlan[0], vni_vlan[1]))
    with open(path + '/bg_vni_list.ios', 'w') as vni_list:
        vni_list.write(template_write_to_file)
        for vni_vlan in bg_vni_list:
            vni_list.write('{},{}\n'.format(vni_vlan[0], vni_vlan[1]))


def main():
    path = sys.argv[1]
    sh_nve_outputs = glob.glob(path + '/*.log')
    site = cfg_list(sh_nve_outputs, 'SKO-DATA-AC-011.*')
    room_md = cfg_list(sh_nve_outputs, 'SKO-DATA-AC-MD.*')
    mpod_bl = cfg_list(sh_nve_outputs, 'SKO-DATA-BL.*')
    mpod_bg = cfg_list(sh_nve_outputs, 'SKO-DATA-BG-[MD1|MD2].*INT.*')
    mpod = room_md+mpod_bl
    ag_vni_vlan_list, bg_vni_vlan_list, l2vni_mcast_map, bg_vni_vlan_list_diff = parse_sh_nve(site, mpod, mpod_bg, path)
    generate_config(ag_vni_vlan_list, bg_vni_vlan_list, l2vni_mcast_map, bg_vni_vlan_list_diff, path)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print('Please check input data')