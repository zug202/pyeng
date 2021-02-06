import re
file = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/15_module_re/cisco_nat_config.txt'
def convert_ios_nat_to_asa(ios,asa):
    template = (
    "object network LOCAL_{host}\n"
    " host {host}\n"
    " nat (inside,outside) static interface service {service} {lport} {gport}\n"
    )

    with open(ios) as f, open(asa, 'w') as asa_nat:
        result = re.finditer(r'ip nat inside source static +'
                            r'(?P<service>\w+) +'
                            r'(?P<host>\d+.\d+.\d+.\d+) +'
                            r'(?P<lport>\d+) +'
                            r'\S+ +\S+ +'
                            r'(?P<gport>\d+)',f.read())
        for match in result:
            #print(template.format(**match.groupdict()))
            asa_nat.write(template.format(**match.groupdict()))

if __name__ == "__main__":
    convert_ios_nat_to_asa(file,'asa_config.txt')