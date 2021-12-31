import os
from operator import itemgetter

from tabulate import tabulate
from xlsxwriter import Workbook

from mimir import Mimir
from credentials import credentials

import getpass

#DICT_OF_CLIENTS = {"VTB": 192322, "SBRF": 116846}

m = Mimir()
psswd = getpass.getpass(prompt='Input pass: ')
m.authenticate('atunin', psswd)

def func_dev_search(client_name):

    columns = ['ID', 'deviceSysname', 'deviceIp', 'productId', 'swType', 'swVersion', 'configTime', 'deviceId','serialNumber']
    while True:
        output_ok = []
        output_false = []
        dev_for_search = input(
            f"\nPress '1' to show device list or enter search value (hostname or suffix): ")
        try:
            if int(dev_for_search) == 1:
                for device in m.np.device_details.get(cpyKey=client_name):
                    if device.configTime:
                        output_ok.append(
                            [str(device.deviceSysname), str(device.deviceIp), str(device.productId), str(device.swType),
                             str(device.swVersion), str(device.configTime).replace("T", " "), str(device.deviceId)])
                    elif device.deviceIp or device.productId:
                        output_false.append(
                            [str(device.deviceSysname), str(device.deviceIp), str(device.productId), str(device.swType),
                             str(device.swVersion), str(device.configTime).replace("T", " "), str(device.deviceId)])
                for device in m.np.hardware.get(cpyKey=client_name):
                    if device.serialNumber:
                        output_ok.append(str(device.serialNumber))
                    else:
                        output_ok.append('N/A')
            else:
                raise ValueError
        except ValueError:
        	'''
            for device in m.np.device_details.get(cpyKey=client_name,
                                                  deviceSysname=f"%{dev_for_search.upper()}%"):
                if device.configTime:
                    output_ok.append(
                        [str(device.deviceSysname), str(device.deviceIp), str(device.productId), str(device.swType),
                         str(device.swVersion), str(device.configTime).replace("T", " "), str(device.deviceId)])
                elif device.deviceIp or device.productId:
                    output_false.append(
                        [str(device.deviceSysname), str(device.deviceIp), str(device.productId), str(device.swType),
                         str(device.swVersion), str(device.configTime).replace("T", " "), str(device.deviceId)])
            '''
            for device in m.np.hardware.get(cpyKey=client_name):
                if device.serialNumber:
                    output_ok.append(str(device.serialNumber))
                else:
                    output_ok.append('N/A')
        print(output_ok)

#        if len(output_false):
#            print("\nDevices without configuration from NP:\n",
#                  tabulate(sorted(output_false), headers=columns, showindex="always"))
#        print("\nFollowing configurations have been found:\n", tabulate(sorted(output_ok), headers=columns, showindex="always"))
#        commit = input("\nAre you agree to continue with the seleceted devices (yes/no)? [yes] ")
#        try:
#            if commit.startswith("yes") or not len(commit):
#                print("Selection confirmed.\n")
#                return output_ok
#            else:
#                continue
#        except ValueError:
#            continue

def main():
    while True:
        # Выбор компании
        #client_selection = func_client_id()
        client_selection = 116846

        # Выбор устройств компании
        devices_selection = func_dev_search(client_selection )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
      # do nothing here
        pass