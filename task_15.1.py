
file = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/15_module_re/config_r1.txt'

import re

def get_ip_from_cfg(filename):
    regex = (r'ip address (\S+) (\S+)')
    with open(filename) as f:
        result = [match.groups() for match in re.finditer(regex, f.read())]

    #print(result)
    return result

if __name__ == "__main__":
    print(get_ip_from_cfg(file))