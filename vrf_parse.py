import re
import glob
import sys

def parse_sh_vrf(outputs, path):
    sh_vrf_regex = ("VRF-Name:\s(?P<vrf_name>\S+), VRF-ID: (?P<vrf_id>\d+)[\S\s]*?(?P<table_id>\w+), AF: IPv4, Fwd-ID: 0x(?P<fwd_id>\w+)")
    vrf_dict = {}
    for filename in outputs:
        hostname = filename.replace(path,'').strip('-nxos_vrf_det.txt')
        vrf_dict[hostname] = {}
        with open(filename) as f:
            match_vrf = re.finditer(sh_vrf_regex, f.read())
            for m in match_vrf:
                vrf_dict[hostname].update({m.group('vrf_name'): {m.group('vrf_id'):[m.group('table_id'), m.group('fwd_id')]}})

    #print(f"vrf_dict = {vrf_dict}")
    return vrf_dict

def compare(dict):
    device_list = []
    for hostname, vrf_data in dict.items():
        for vrf_name, id_data in vrf_data.items():
           #print(vrf_data[vrf_name])
           for vrf_id, table_fwd_id_list in id_data.items():
               if int(vrf_id) is not int(table_fwd_id_list[0],16):
                   device_list.append(hostname)
               elif int(vrf_id) is not int(table_fwd_id_list[1],16):
                   device_list.append(hostname)
    #print(set(device_list))
    return set(device_list)

def generate_file(device_list, path):
    with open(path + '/invalid_vrf_id.txt', 'w') as file:
        for each in device_list:
            template = (f"{each}\n")
            file.write(template)

def main():
    path = sys.argv[1]
    sh_vrf_outputs = glob.glob(path + '*.*')
    vrf_dict = parse_sh_vrf(sh_vrf_outputs, path)
    generate_file(compare(vrf_dict),path)

if __name__ == "__main__":
    #try:
        main()
    #except Exception:
    #    print('Please check input data')
