trunk_mode_template = [
    "switchport mode trunk", "switchport trunk native vlan 999",
    "switchport trunk allowed vlan"
]

trunk_config = {
    "FastEthernet0/1": [10, 20, 30],
    "FastEthernet0/2": [11, 30],
    "FastEthernet0/4": [17]
}

def generate_trunk_config(intf_vlan_mapping, trunk_template):
    config = []
    for intf, vlan in intf_vlan_mapping.items():
        config.append('interface ' + intf)
        for command in trunk_template:
            if command.endswith('allowed vlan'):
                config.append(command + " " + (str(vlan).strip('[]').replace(" ","")))
            else:
                config.append(command)
    print(config)
    return config

generate_trunk_config(trunk_config,trunk_mode_template)