file = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/15_module_re/config_r1.txt'

import re

def get_ip_from_cfg(filename):
    with open(filename) as f:
        match = re.finditer(r"interface (?P<intf>\S+)\n"
                            r"( .*\n)*"
                            r" ip address (?P<ip>\S+) (?P<mask>\S+)",f.read())

    result = {m.group('intf') : m.group('ip','mask') for m in match}
    return result

if __name__ == "__main__":
    print(get_ip_from_cfg(file))