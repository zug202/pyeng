
def parse_cdp_neighbors(command_output):
    device_name = command_output.replace('\n','').split(">")[0]
    neighbors = command_output.split('Port ID')[1].split('\n')
    output_dict = {}
    while '' in neighbors:
        neighbors.remove('')
    for line in neighbors:
        local_intf = [line.split()[1],line.split()[2]]
        remote_intf = [line.split()[-2],line.split()[-1]]
        remote_name = line.split()[0]
        output_dict.update({(device_name,''.join(local_intf)):(remote_name,''.join(remote_intf))})
    #print(output_dict)
    return(output_dict)

if __name__ == "__main__":
    with open('/Users/atunin/Downloads/python/pyneg-tasks/exercises/11_modules/sh_cdp_n_sw1.txt') as f:
        print(parse_cdp_neighbors(f.read()))
