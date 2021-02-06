from sys import argv
#file1 = argv[1]
#file1 = argv[2]
file1 = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/07_files/config_sw1.txt'
file2 = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/07_files/config_sw1_cleared.txt'
ignore = ["duplex", "alias", "Current configuration"]

with open(file1) as src, open (file2,'w') as dest:
    for line in src:
        #if not line.startswith('!'):
            for word in ignore:
                if word in line:
                    break
            else:
                dest.write(line)
