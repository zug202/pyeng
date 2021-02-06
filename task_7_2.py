from sys import argv
#file = argv[1]
file = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/07_files/config_sw1.txt'
with open(file) as src:
    for line in src:
        if not line.startswith('!'):
            print(line.rstrip())
