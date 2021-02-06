import yaml
from draw_network_graph import draw_topology


def transform_topology(topology_filename):
    final_topology = {}
    with open(topology_filename) as f:
        raw_topology = yaml.load(f, Loader=yaml.FullLoader)
    for l_device,peer in raw_topology.items():
        for l_port, remote in peer.items():
            for r_device, r_port in remote.items():
                new_value = (r_device,r_port)
                new_key = (l_device,l_port)
                if not final_topology.get(new_value) == new_key:
                    final_topology[new_key]=new_value
    return(final_topology)


if __name__ == "__main__":
    formatted_topology = transform_topology("topology.yaml")
    print(formatted_topology)
    draw_topology(formatted_topology)