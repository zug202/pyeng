import re
import csv
import glob
file = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/17_serialization/sh_cdp_n_sw1.txt'

def parse_sh_cdp_neighbors(sh_cdp_output):
    result = {}
    regex = (
        '(?P<nbr>\S+)\s+(?P<lintf>\S+\s\d.\d).*\s(?P<rintf>\S+\s\d.\d)'
        #r"(?P<nbr>\w+)  +(?P<lintf>\S+ \S+)"
        #r"  +\d+  +[\w ]+  +\S+ +(?P<rintf>\S+ \S+)"
    )
    hostname = re.search(r"(\S+)[>#]", sh_cdp_output).group(1)
    result[hostname] = {}
    match = re.finditer(regex,sh_cdp_output)
    for m in match:
        result[hostname][m.group('lintf')] = {m.group('nbr'):m.group('rintf')}
        #result[hostname][m.group('lintf')] = m.group('nbr','rintf')
    return result


if __name__ == "__main__":
    with open(file) as f:
        print(parse_sh_cdp_neighbors(f.read()))