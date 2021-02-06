access_mode_template = [
    "switchport mode access", "switchport access vlan",
    "switchport nonegotiate", "spanning-tree portfast",
    "spanning-tree bpduguard enable"
]

port_security_template = [
    "switchport port-security maximum 2",
    "switchport port-security violation restrict",
    "switchport port-security"
]
access_config = {
    "FastEthernet0/12": 10,
    "FastEthernet0/14": 11,
    "FastEthernet0/16": 17
}

def generate_access_config(intf_vlan_mapping, access_template, psecurity='None'):
    config = []
    for intf, vlan in intf_vlan_mapping.items():
        config.append('interface ' + intf)
        for command in access_template:
            if command.endswith('access vlan'):
                config.append(command + " " + str(vlan))
            else:
                config.append(command)
        if not 'None' in psecurity:
            for command in psecurity:
                config.append(command)
    print(config)
    return config

generate_access_config(access_config,access_mode_template,port_security_template)