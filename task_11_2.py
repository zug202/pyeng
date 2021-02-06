import task_11_1 as cdp_p
from draw_network_graph import draw_topology

def create_network_map(filenames):
    output_dict = {}
    seen = set()
    to_remove = []
    for cfg in filenames:
        with open(cfg) as f:
            output_dict.update(cdp_p.parse_cdp_neighbors(f.read()))
    for key, val in output_dict.items():
        entry = tuple(sorted(key + val))
        #print(entry)
        if entry in seen:
            to_remove.append(key)
        else:
            seen.add(entry)
    #print(to_remove)
    for key in to_remove:
        del output_dict[key]

    #print(output_dict)
    return output_dict
if __name__ == "__main__":
    infiles = [
        '/Users/atunin/Downloads/python/pyneg-tasks/exercises/11_modules/sh_cdp_n_sw1.txt',
        "/Users/atunin/Downloads/python/pyneg-tasks/exercises/11_modules/sh_cdp_n_r1.txt",
        "/Users/atunin/Downloads/python/pyneg-tasks/exercises/11_modules/sh_cdp_n_r2.txt",
        "/Users/atunin/Downloads/python/pyneg-tasks/exercises/11_modules/sh_cdp_n_r3.txt",
    ]

    topology = create_network_map(infiles)

    #print(len(topology))
    draw_topology(topology)