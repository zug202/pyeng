from task_17_3 import parse_sh_cdp_neighbors
import yaml
import glob

def generate_topology_from_cdp(list_of_files,save_to_filename = None):
    parsed_data = {}
    for filename in list_of_files:
        with open(filename) as f:
            parsed_data.update(parse_sh_cdp_neighbors(f.read()))
    if save_to_filename:
        with open(save_to_filename, 'w') as dest:
            yaml.dump(parsed_data, dest, default_flow_style=False)
    return parsed_data

if __name__ == "__main__":
    cdp_files = glob.glob("sh_cdp_n_*")
    print(generate_topology_from_cdp(cdp_files,'topology.yaml'))