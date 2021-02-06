import re
file = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/15_module_re/sh_ip_int_br.txt'
def parse_sh_ip_int_br(filename):
    with open(filename) as f:
        result = re.finditer(r'(\S+) +'
                        r'(\S+) +'
                        r'\S+ +'
                        r'\S+ +'
                        r'(up|down|administratively down) +'
                        r'(up|down)',f.read())
    groups = []
    for match in result:
        groups.append(match.groups())

    print(groups)
    return groups

if __name__ == "__main__":
    parse_sh_ip_int_br(file)