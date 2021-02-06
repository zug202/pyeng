import re
file = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/15_module_re/sh_cdp_n_sw1.txt'

def generate_description_from_cdp1(filename):
    descr = {}
    with open(filename) as f:
        result = re.finditer(r'(?P<nbr>\S+) +(?P<lintf>\S+\s\d.\d) +\d+ +\S\s\S\s\S +\d+ + (?P<rintf>\S+\s\d.\d)',f.read())

        for match in result:
            descr[match.group('lintf')] = 'description Connected to '+ match.group('nbr') + ' port ' + match.group('rintf')
        print(descr)
        return descr

def generate_description_from_cdp2(sh_cdp_filename):
    regex = re.compile(
        r"(?P<r_dev>\w+)  +(?P<l_intf>\S+ \S+)"
        r"  +\d+  +[\w ]+  +\S+ +(?P<r_intf>\S+ \S+)"
    )
    description = "description Connected to {} port {}"
    intf_desc_map = {}
    with open(sh_cdp_filename) as f:
        for match in regex.finditer(f.read()):
            r_dev, l_intf, r_intf = match.group("r_dev", "l_intf", "r_intf")
            intf_desc_map[l_intf] = description.format(r_dev, r_intf)
    print(intf_desc_map)
    return intf_desc_map

if __name__ == "__main__":
    generate_description_from_cdp1(file)
    generate_description_from_cdp2(file)