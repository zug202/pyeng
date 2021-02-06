file = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/15_module_re/config_r2.txt'

import re

def get_ip_from_cfg(filename):
    result = {}
    with open(filename) as f:
        match = re.finditer("interface (\S+)\n"
                            "( .*\n)*"
                            " ip address \S+ \S+\n"
                            "( ip address \S+ \S+ secondary\n)*",f.read())
        for m in match:
            print(m.group())
            result[m.group(1)] = re.findall('ip address (\S+) (\S+)', m.group())
    return result

if __name__ == "__main__":
    print(get_ip_from_cfg(file))
