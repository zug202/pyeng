import re
file = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/15_module_re/config_r1.txt'
def get_ints_without_description(filename):
    with open(filename) as f:
        match = re.finditer(r'!\ninterface (?P<intf>\S+)\n(?P<descr> description \S+)?',f.read())

        result = [m.group('intf') for m in match if m.lastgroup == 'intf']
        print(result)
        return result
    #return intf_with_desc


if __name__ == "__main__":
    get_ints_without_description(file)
    #interface \S+\n|no ip address|ip unnumbered \S+\n|ip address \d+.\d+.\d+.\d+ +\d+.\d+.\d+.\d+