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
    l2vni_vlan_site = []
    l2vni_mcast = {}
    for filename in site_outputs:
        with open(path + '/' + filename) as f:
            match_site = re.finditer(sh_nve_regex, f.read())
            if (match_site):
                for m in match_site:
                    l2vni_site.append((m.group('l2vni')))
                    l2vni_vlan_site.append((m.group('l2vni'), m.group('vlan')))
# creating a dict (vni:mcast) mapping for cfg generation:
                    l2vni_mcast.update({m.group('l2vni') : m.group('mcast')})
# creating a set for site vni:
    l2vni_site_set = set(l2vni_site)
    print(f"len(l2vni_site_set) = {len(l2vni_site_set)}")
# creating a set for list of tuples (vni:vlan) for site:
    l2vni_vlan_site_set = set(l2vni_vlan_site)
    print(f"len(l2vni_vlan_site_set) = {len(l2vni_vlan_site_set)}")

# creating a list of tuples (vni:vlan) for mpod:
    l2vni_mpod = []
    l2vni_vlan_mpod = []
    for filename in mpod_outputs:
        with open(path + '/' + filename) as f:
            match_mpod = re.finditer(sh_nve_regex, f.read())
            if (match_mpod):
                for m in match_mpod:
                    l2vni_mpod.append((m.group('l2vni')))
                    l2vni_vlan_mpod.append((m.group('l2vni'), m.group('vlan')))

# creating a set for mpod vni:
    l2vni_mpod_set = set(l2vni_mpod)
    print(f"len(l2vni_mpod_set) = {len(l2vni_mpod_set)}")
# creating a set for list of tuples (vni:vlan) for mpod:
    l2vni_vlan_mpod_set = set(l2vni_vlan_mpod)
    print(f"len(l2vni_vlan_mpod_set) = {len(l2vni_vlan_mpod_set)}")

# creating a list of tuples (vni:vlan) for mpod_bg:
    l2vni_mpod_bg = []
    l2vni_vlan_mpod_bg = []
    for filename in mpod_bg_outputs:
        with open(path + '/' + filename) as f:
            match_mpod_bg = re.finditer(sh_nve_regex, f.read())
            if (match_mpod_bg):
                for m in match_mpod_bg:
                    l2vni_mpod_bg.append((m.group('l2vni')))
                    l2vni_vlan_mpod_bg.append((m.group('l2vni'), m.group('vlan')))
# creating a set for mpod_bg vni:
    l2vni_mpod_bg_set = set(l2vni_mpod_bg)
    print(f"len(l2vni_mpod_bg_set) = {len(l2vni_mpod_bg_set)}")
    #print(f"l2vni_mpod_bg_set = {l2vni_mpod_bg_set}")
# creating a set for list of tuples (vni:vlan) for mpod_bg:
    l2vni_vlan_mpod_bg_set = set(l2vni_vlan_mpod_bg)
    print(f"len(l2vni_vlan_mpod_bg_set) = {len(l2vni_vlan_mpod_bg_set)}")
    #print(f"l2vni_mpod_bg_set = {l2vni_mpod_bg_set}")

# creating a vni_vlan_database:
    vni_vlan_database = {}
    vni_vlan_database.update(dict(l2vni_vlan_site_set))
    vni_vlan_database.update(dict(l2vni_vlan_mpod_set))
    vni_vlan_database.update(dict(l2vni_vlan_mpod_bg_set))
    #print(vni_vlan_database['2072916'])
    #print(vni_vlan_database['9013002'])

# finding set intersection between site and mpod:
    l2vni_site_mpod_list = l2vni_site_set.intersection(l2vni_mpod_set)
    print(f"len(l2vni_site_mpod) = {len(l2vni_site_mpod_list)}")
    l2vni_site_bg_list = l2vni_site_set.intersection(l2vni_mpod_bg_set)
    print(f"len(l2vni_site_bg) = {len(l2vni_site_bg_list)}")
    l2vni_mpod_list = l2vni_site_mpod_list.union(l2vni_site_bg_list)
    print(f"len(ag_vni_list) = {len(l2vni_mpod_list)}")

# finding vni list that should be created on bg:
    bg_vni_list = []
    for vni in l2vni_mpod_list:
        if vni not in l2vni_mpod_bg_set:
            bg_vni_list.append(vni)
    print(f"len(bg_vni_list) = {len(bg_vni_list)}")

# finding ag_vni_vlan set for config generation:
    ag_vni_vlan_list = {}
    for vni in l2vni_mpod_list:
        ag_vni_vlan_list.update({vni:vni_vlan_database[vni]})
    print(f"len(ag_vni_vlan_list) = {len(ag_vni_vlan_list)}")

    ag_vni_vlan_set = sorted(set(ag_vni_vlan_list.items()))

# finding bg_vni_vlan set for config generation:
    bg_vni_vlan_list = {}
    for vni in bg_vni_list:
        bg_vni_vlan_list.update({vni:vni_vlan_database[vni]})
    print(f"len(bg_vni_vlan_list) = {len(bg_vni_vlan_list)}")

    bg_vni_vlan_set = sorted(set(bg_vni_vlan_list.items()))


    return ag_vni_vlan_set, bg_vni_vlan_set, l2vni_mcast

def generate_config(ag_vni_list, bg_vni_list, l2vni_mcast, path):
# common cfg templates
    template_interface_nve_1 = ("interface nve1\n")
    template_evpn =("evpn\n")

# writing config to file for BG
    with open(path + '/pre_bg_l2_vni.ios', 'w') as bg_l2_vni:
        for vni_vlan in bg_vni_list:
            template_bg_vni_vlan = (
                f"vlan {vni_vlan[1]}\n"
                f" vn-segment {vni_vlan[0]}\n"
                "\n"
            )
            bg_l2_vni.write(template_bg_vni_vlan)
        bg_l2_vni.write(template_evpn)
        for vni_vlan in bg_vni_list:
            template_bg_vni_evpn = (
                f" vni {vni_vlan[0]} l2\n"
                "  rd auto\n"
                f"  route-target import 65554:{vni_vlan[0]}\n"
                f"  route-target export 65554:{vni_vlan[0]}\n"
                "\n"
            )
            bg_l2_vni.write(template_bg_vni_evpn)
        bg_l2_vni.write(template_interface_nve_1)
        for vni_vlan in bg_vni_list:
            template_bg_ingress = (
                f" member vni {vni_vlan[0]}\n"
                "  multisite ingress-replication\n"
                "  ingress-replication protocol bgp\n"
            )
            template_bg_mcast = (
                f" member vni {vni_vlan[0]}\n"
                "  multisite ingress-replication\n"
                f"  mcast-group {l2vni_mcast[vni_vlan[0]]}\n"
            )
            if l2vni_mcast[vni_vlan[0]] == 'UnicastBGP':
                bg_l2_vni.write(template_bg_ingress)
            else:
                bg_l2_vni.write(template_bg_mcast)
# writing config to file for AG (pre-works)
    with open(path + '/pre_ag_l2_vni.ios', 'w') as ag_l2_vni:
        for vni_vlan in ag_vni_list:
            template_ag_vni_vlan = (
                f"vlan {vni_vlan[1]}\n"
                f" vn-segment {vni_vlan[0]}\n"
                "\n"
            )
            ag_l2_vni.write(template_ag_vni_vlan)
        ag_l2_vni.write(template_evpn)
        for vni_vlan in ag_vni_list:
            template_ag_vni_evpn = (
                f" vni {vni_vlan[0]} l2\n"
                "  rd auto\n"
                f"  route-target import 65554:{vni_vlan[0]}\n"
                f"  route-target export 65554:{vni_vlan[0]}\n"
                "\n"
            )
            ag_l2_vni.write(template_ag_vni_evpn)

# writing config to file for AG nve without MS-IR (main-works)
    with open(path + '/mw1-bgw_l2_vni_without_MS-IR.ios', 'w') as ag_l2_vni_nve:
        ag_l2_vni_nve.write(template_interface_nve_1)
        for vni_vlan in ag_vni_list:
            template_ag_nve_mcast = (
                f" member vni {vni_vlan[0]}\n"
                f"  mcast-group {l2vni_mcast[vni_vlan[0]]}\n"
            )
            template_ag_nve_ingress = (
                f" member vni {vni_vlan[0]}\n"
                "  ingress-replication protocol bgp\n"
            )
            if l2vni_mcast[vni_vlan[0]] == 'UnicastBGP':
                ag_l2_vni_nve.write(template_ag_nve_ingress)
            else:
                ag_l2_vni_nve.write(template_ag_nve_mcast)
# writing config to file for AG adding MS-IR (main-works)
    with open(path + '/mw1-bgw_l2_vni_with_MS-IR.ios', 'w') as ag_l2_vni_ms_ir:
        ag_l2_vni_ms_ir.write(template_interface_nve_1)
        for vni_vlan in ag_vni_list:
            template_ag_ms_ir = (
                f" member vni {vni_vlan[0]}\n"
                "  multisite ingress-replication\n"
            )
            ag_l2_vni_ms_ir.write(template_ag_ms_ir)
# writing vni:vlan to file
    with open(path + '/ag_vni_list.ios', 'w') as vni_list:
        for vni_vlan in ag_vni_list:
            vni_list.write('{},{}\n'.format(vni_vlan[0], vni_vlan[1]))
    with open(path + '/bg_vni_list.ios', 'w') as vni_list:
        for vni_vlan in bg_vni_list:
            vni_list.write('{},{}\n'.format(vni_vlan[0], vni_vlan[1]))


def main():
    path = sys.argv[1]
    sh_nve_outputs = glob.glob(path + '/*.txt')
    site = cfg_list(sh_nve_outputs, 'SKO-DATA-AC-014.*')
    mpod_bl = cfg_list(sh_nve_outputs, 'SKO-DATA-BL.*')
    mpod_bg = cfg_list(sh_nve_outputs, 'SKO-DATA-BG-[MD1|MD2].*EXT.*')
    room_md = cfg_list(sh_nve_outputs, 'SKO-DATA-AC-MD.*')
    mpod = room_md + mpod_bl
    ag_vni_vlan_set, bg_vni_vlan_set, l2vni_mcast = parse_sh_nve(site, mpod, mpod_bg, path)
    generate_config(ag_vni_vlan_set, bg_vni_vlan_set, l2vni_mcast, path)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        print('Please check input data')
