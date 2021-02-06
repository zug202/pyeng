import subprocess
alive_list = []
unreach_list = []


def ping_ip_addresses(ip_list):
    for ip_address in ip_list:
        reply = subprocess.run(['ping', '-c', '3', '-n', ip_address])
        if reply.returncode == 0:
            alive_list.append(ip_address)
        else:
            unreach_list.append(ip_address)

    result = tuple([alive_list]+[unreach_list])
    print(result)
    return result

if __name__ == "__main__":
    ip = ['1.1.1.1','2.2.2.2','8.8.8.8','192.168.0.1']
    ping_ip_addresses(ip)
