import re
import glob

def room_12_list(sh_nve_outputs):
    room_12_outputs = []
    for output in sh_nve_outputs:
        if re.search('SKO-DATA-AC-012.*', output) != None:
            room_12_outputs.append(re.search('SKO-DATA-AC-012.*', output).group())
    return room_12_outputs

def room_11_list(sh_nve_outputs):
    room_11_outputs = []
    for output in sh_nve_outputs:
        if re.search('SKO-DATA-AC-011.*', output) != None:
            room_11_outputs.append(re.search('SKO-DATA-AC-011.*', output).group())
    return room_11_outputs

def room_md_list(sh_nve_outputs):
    room_md_outputs = []
    for output in sh_nve_outputs:
        if re.search('SKO-DATA-AC-MD.*', output) != None:
            room_md_outputs.append(re.search('SKO-DATA-AC-MD.*', output).group())
    return room_md_outputs

def room_bl_list(sh_nve_outputs):
    bl_outputs = []
    for output in sh_nve_outputs:
        if re.search('SKO-DATA-BL.*', output) != None:
            bl_outputs.append(re.search('SKO-DATA-BL.*', output).group())
    return bl_outputs

def parse_sh_nve(site_outputs,mpod_outputs):
    path = '/Users/atunin/Downloads/RawInventory_Export_2021-Feb-04_23-53-59/CLI/show_nve_vni'
    sh_nve_regex = (".* +(?P<l2vni>\d+) +.*\d+\.\d+\.\d+\.\d+ +.*Up +.*L2")

    l2vni_site = []
    for filename in site_outputs:
        with open(path + '/' + filename) as f:
            match_site = re.finditer(sh_nve_regex, f.read())
            for m in match_site:
                l2vni_site.append(m.group('l2vni'))
    l2vni_site_set = set(l2vni_site)

    l2vni_mpod = []
    for filename in mpod_outputs:
        with open(path + '/' + filename) as f:
            match_mpod = re.finditer(sh_nve_regex, f.read())
            for m in match_mpod:
                l2vni_mpod.append(m.group('l2vni'))
    l2vni_mpod_set = set(l2vni_mpod)

    result = l2vni_site_set.intersection(l2vni_mpod_set)

    return result




if __name__ == "__main__":

    sh_nve_outputs = glob.glob('/Users/atunin/Downloads/RawInventory_Export_2021-Feb-04_23-53-59/CLI/show_nve_vni/*.txt')
    site = room_12_list(sh_nve_outputs)
    mpod = room_11_list(sh_nve_outputs)+room_md_list(sh_nve_outputs)+room_bl_list(sh_nve_outputs)
    print(parse_sh_nve(site,mpod))