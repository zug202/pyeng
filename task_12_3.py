import subprocess
import ipaddress
from tabulate import tabulate

def check_if_ip_is_ip(ip_address):
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False

def convert_ranges_to_ip_list(ip_list):
    range_list = []
    for ip_address in ip_list:
        if check_if_ip_is_ip(ip_address) is True:
            range_list.append(ip_address)
        else:
            start_ip = ipaddress.ip_address(ip_address.split('-')[0])
            if len(ip_address.split('-')[1]) < 4:
                end_ip = start_ip + (int(ip_address.split('-')[1]) - int(ip_address.split('-')[0].split('.')[3])) + 1
            elif check_if_ip_is_ip(ip_address.split('-')[1]) is True:
                end_ip = ipaddress.ip_address(ip_address.split('-')[1]) + 1
            #print(start_ip)
            #print(end_ip)
            for ip_int in range(int(start_ip), int(end_ip)):
                range_list.append(str(ipaddress.ip_address(ip_int)))
    return range_list

def ping_ip_address(ip_list):
    alive_list = []
    unreach_list = []
    for ip_address in ip_list:
        reply = subprocess.run(['ping', '-c', '3', '-n', ip_address])
        if reply.returncode == 0:
            alive_list.append(ip_address)
        else:
            unreach_list.append(ip_address)

    result = tuple([alive_list]+[unreach_list])
#    print(result)
    return result

def print_ip_table(ip_list):
    alive_list = ip_list[0]
    unreach_list = ip_list[1]
    for i, a in enumerate(alive_list):
        if i == len(unreach_list):
            rows = zip(alive_list, unreach_list)
            summary = list(rows)
        elif i > len(unreach_list):
            unreach_list.append("")
            rows = zip(alive_list, unreach_list)
            summary = list(rows)
        else:
            alive_list.append("")
            rows = zip(alive_list, unreach_list)
            summary = list(rows)

    print(tabulate(summary, headers=['reach', 'unreach']))

if __name__ == "__main__":
    ip = ['1.1.1.1','2.2.2.2-5','8.8.8.8-10','192.168.0.1-192.168.0.10']
    print_ip_table(ping_ip_address(convert_ranges_to_ip_list(ip)))