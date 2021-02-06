config = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/09_functions/config_sw1.txt'

def get_int_vlan_map(config_filename):
    with open(config_filename) as file:
        access_dict = {}
        trunk_dict = {}
        for line in file:
            if line.startswith('interface Vlan'):
                pass
            elif line.startswith('interface'):
                intf = line.strip().replace('interface ','')
#                print(intf)
            elif line.startswith(' switchport access vlan'):
                access = int(line.strip().replace('switchport access vlan',''))
#                print(access)
                access_dict[intf] = access
            elif line.startswith(' switchport trunk allowed vlan'):
                trunk_str = line.strip().replace('switchport trunk allowed vlan ','').split(',')
                trunk = []
                for word in trunk_str:
                    trunk.append(int(word))
#                print(trunk)
                trunk_dict[intf] = trunk
        tuple_result = tuple([access_dict, trunk_dict])
        print(tuple_result)
        return tuple_result

get_int_vlan_map(config)

