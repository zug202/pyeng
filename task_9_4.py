config = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/09_functions/config_sw1.txt'
ignore = ["duplex", "alias", "Current configuration"]

def ignore_command(command,ignore):
    for word in ignore:
        if word in command:
            pass
    return any (word in command for word in ignore)

def convert_config_to_dict(config_filename):
    with open(config_filename) as file:
        level1 = ''
        level2 = ''
        config_dict = {}
        for line in file:
            if line.startswith('!'):
                pass
            elif line[0].isalpha():
                if ignore_command(line, ignore):
                    pass
                else:
                    level1 = line.strip()
                    config_dict[level1] = []
                    #print(level1)
            elif line.startswith(' ') and line[1].isalpha():
                if ignore_command(line, ignore):
                    pass
                else:
                    config_dict[level1].append(line.strip())
                    #print(level2)
        print(config_dict)
        return config_dict

convert_config_to_dict(config)

