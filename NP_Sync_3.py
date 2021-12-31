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


#def func_client_id():
#    """
#    Функция не принимает на вход параметры.
#    1. На основе словаря DICT_OF_CLIENTS функция запрашивает выбор клиента по индексу
#    Функция возвращает строку вида 'VTB'
#   	"""
#    while True:
#        print("Список клиентов:")
#        for client in DICT_OF_CLIENTS:
#            print(f"{list(DICT_OF_CLIENTS).index(client)} {client}")
#        input_client = input("Выберите клиента из предложенных вариантов: ")
#        try:
#            input_client = int(input_client)
#           if input_client in range(len(DICT_OF_CLIENTS)):
#               return list(DICT_OF_CLIENTS)[input_client]
#           else:
#               print("\nНеправильный ввод.\n")
#       except ValueError:
#           print("\nНеправильный ввод: нужно ввести число.\n")
#

def func_dev_search(client_name):
    """
    Функция принимает на вход строку вида 'VTB'
    1. На основе словаря DICT_OF_CLIENTS функция находит cpyKey, по которому, взаимодействуя с пользователем,
        определяет перечень устройств для поиска конфигурации.
    Функция возвращает список списков с перечнем устройств для дальнейшего поиска, вида
        [['pN77-1-otv1', '10.150.255.9', 'N77-C7710', 'NX-OS', '7.2(2)D1(2)', time, 6248965]]
    """
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
            for device in m.np.hardware.get(cpyKey=client_name):
                if device.serialNumber:
                    output_ok.append(str(device.serialNumber))
                else:
                    output_ok.append('N/A')
        print(output_ok)

        if len(output_false):
            print("\nDevices without configuration from NP:\n",
                  tabulate(sorted(output_false), headers=columns, showindex="always"))
        print("\nFollowing configurations have been found:\n", tabulate(sorted(output_ok), headers=columns, showindex="always"))
        commit = input("\nAre you agree to continue with the seleceted devices (yes/no)? [yes] ")
        try:
            if commit.startswith("yes") or not len(commit):
                print("Selection confirmed.\n")
                return output_ok
            else:
                continue
        except ValueError:
            continue


def func_search_in_runnconf(client_name, devices_selection):
    columns = ['ID', 'deviceSysname', 'deviceIp', 'productId', 'swType', 'swVersion', 'configTime', 'deviceId',
               'command', 'line']
    while True:
        command = input("Введите простую строку для поиска: ")
        if len(command) > 1:
            break
        else:
            print("Пустая строка не разрешена. Введите строку.")

    output = []
    print("Выполняется запрос с NP")
    for runn_conf in m.np.config.get(cpyKey=client_name, configType="STANDARD RUNNING"):
        runn_conf_str = runn_conf.rawData.split("\n")
        line_number = 1
        for line in runn_conf_str:
            if command in line:
                for device in devices_selection:
                    if str(runn_conf.deviceId) in str(device[6]):
                        output.append([str(device[0]), str(device[1]), str(device[2]), str(device[3]),
                                       str(device[4]), str(device[5]).replace("T", " "), str(device[6]), line,
                                       line_number])
            line_number += 1

    print("\n", tabulate(sorted(output, key=itemgetter(0, 8)), headers=columns, showindex="always"))
    print("\nПоиск завершен.\n")
    return output


def func_running_config(client_name, devices_selection):
    """
    Функция принимает на вход строку вида 'VTB' и список списков вида
        [['pN77-1-otv1', '10.150.255.9', 'N77-C7710', 'NX-OS', '7.2(2)D1(2)', 6248965]]

    1. Для полученного значения client_name и групп устройств devices_selection скачивает runn_conf в локальную папку

    Функция ничего не возвращает
    """
    # Создание директории
    if not os.path.exists(f"{client_name} running_config"):
        os.mkdir(f"{client_name} running_config")

    # Создание множества уникальных device_id
    set_of_dev = set()
    for device in devices_selection:
        device_id = device[6]
        set_of_dev.add(device_id)

    # Уведомление
    count_dev = int(len(devices_selection))
    if count_dev > 5:
        print(f"\nДанные сохраняются. Для {count_dev} устройств(а), "
              f"это займет не менее, {count_dev * 0.73} секунд(ы).")

    # Заполнение [hostname, dev_id]
    dict_of_dev = {}
    for dev_id in set_of_dev:
        for line in devices_selection:
            if line[6] == dev_id:
                dict_of_dev[line[0]] = dev_id

    # Сохранение
    for hostname, dev_id in dict_of_dev.items():
        for runn_conf in m.np.config.get(cpyKey=client_name, deviceId=dev_id,
                                         configType="STANDARD RUNNING"):
            path = os.path.join(f"{client_name} running_config", f"{hostname}.txt")
            with open(f"{path}", "w") as file:
                file.write(runn_conf.rawData)
    print(f"\nДанные сохранены в каталог './{client_name} running_config/'\n")


def func_show_command(client_name, devices_selection):
    """
    Функция принимает на вход строку вида 'VTB' и список списков вида
        [['pN77-1-otv1', '10.150.255.9', 'N77-C7710', 'NX-OS', '7.2(2)D1(2)', 6248965]]

    1. Функция проверяет список доступных команд show с коллектора
    2. Функция запрашивает перечень команд для сбора данных у пользователя
    3. Перебирая списки с индексом [-1] (deviceId) в цикле, выводим запрошенные команды.

    Функция ничего не возвращает
    """

    columns = ['№', 'show command']

    print("\nСписок доступных команд (выбирается для первого устройства в списке):\n")

    # Подготовка списка доступных команд. Выбирается для первого устройства в списке
    list_show_commands = []
    for cli_avail in m.np.cli_available.get(cpyKey=client_name, deviceId=devices_selection[0][6]):
        list_show_commands.append(cli_avail.commandName)

    # Подготовка словаря для индексации каждой команды
    dict_show_commands_sorted_with_index = {}
    for ind, value in enumerate(sorted(list_show_commands)):
        dict_show_commands_sorted_with_index[ind] = value

    # Работа со словарем dict_show_commands_sorted_with_index. Вывод для пользователя
    # Выбор из словаря dict_show_commands_sorted_with_index более узкого dict_selected_show_commands
    # На выходе получаем dict_selected_show_commands
    while True:
        print(tabulate([[k, v] for k, v in dict_show_commands_sorted_with_index.items()], headers=columns))
        show_range = input(f"\nВведите id интересующей show команды для группы устройств (пример: 1,2,6-9): ")
        try:
            list_of_index = []
            for index in show_range.split(","):
                if index.isdigit():
                    list_of_index.append(int(index))
                else:
                    data = index.split("-")
                    data_range = list(range(int(data[0]), int(data[1]) + 1))
                    for _ in data_range:
                        list_of_index.append(_)
            dict_selected_show_commands = {}
            for show_comm in sorted(list_of_index):
                dict_selected_show_commands[show_comm] = dict_show_commands_sorted_with_index[show_comm]
            print("\nВыбраны show команды:\n")
            print(tabulate([[k, v] for k, v in dict_selected_show_commands.items()], headers=columns))
            commit = input("\nВыполнить сохранение для выбранных show команд (yes/no)? [yes] ")
            try:
                if commit.startswith("yes") or not len(commit):
                    break
                else:
                    continue
            except:
                continue
        except:
            print("Введите корректное значение")

    # Создание директории
    for command in dict_selected_show_commands.values():
        if not os.path.exists(f"{client_name} {command.replace(':', ' ')}"):
            os.mkdir(f"{client_name} {command.replace(':', ' ')}")

    # Уведомление
    count_dev = int(len(devices_selection)) * int(len(dict_selected_show_commands))
    if count_dev > 5:
        print(f"\nДанные сохраняются. Загрузка {count_dev} файлов "
              f"займет не менее {count_dev * 3} секунд(ы).\nДля массовой загрузки используйте NP.")

    # Парсинг и сохранение
    for device in devices_selection:
        hostname = device[0]
        device_id = device[-1]
        for command in dict_selected_show_commands.values():
            for show_data in m.np.cli.get(cpyKey=client_name, deviceId=device_id, command=command):
                path = os.path.join(f"{client_name} {command.replace(':', ' ')}", f"{hostname}.txt")
                with open(f"{path}", "w") as file:
                    file.write(show_data.rawData)
    print(f"\nДанные сохранены в каталог './{client_name} show <command>/'\n")


def func_dev_search_save(client_selection, devices_selection):
    if len(devices_selection[0]) <= 8:
        columns = ['ID', 'deviceSysname', 'deviceIp', 'productId', 'swType', 'swVersion', 'configTime', 'deviceId']
    else:
        columns = ['ID', 'deviceSysname', 'deviceIp', 'productId', 'swType', 'swVersion', 'configTime', 'deviceId',
                   'line', 'line_num']
    try:
        wb = Workbook('list_of_devices.xlsx')
        ws = wb.add_worksheet(client_selection)
        ws.set_column(0, len(columns), 20)
        bold = wb.add_format({'bold': True})
        first_row = 0
        for header in columns:
            col = columns.index(header)  # we are keeping order.
            ws.write(first_row, col, header, bold)  # we have written first row which is the header of worksheet also.
        row = 1
        for line in devices_selection:
            for column, value in enumerate(line):
                ws.write(row, column + 1, value)
            ws.write(row, 0, row - 1)
            row = row + 1  # enter the next row
        wb.close()
    except:
        print("\nОшибка сохранения.\nЗакройте файл list_of_devices.csv")


def main():
    while True:
        # Выбор компании
        #client_selection = func_client_id()
        client_selection = 116846

        # Выбор устройств компании
        devices_selection = func_dev_search(client_selection )

        while True:
            # Запрос на сохранение конфигурации
            print(f"Введите 1, для поиска в конфигурации для выбранных устройств\n"
                  f"Введите 2, для сохранения running config выбранных устройств в локальный каталог\n"
                  f"Введите 3, для выбора списка show команд перед их сохранением\n"
                  f"Введите 4, для экспорта выбранной группы устройств в xls\n"
                  f"Введите 5, для возврата в начало\n")
            while True:
                type_of_action = input(f"Выбор дальнейшего действия для {client_selection}: ")
                try:
                    if int(type_of_action) in range(1, 6):
                        break
                    else:
                        print("Введите корректное значение\n")
                except ValueError:
                    print("Введите корректное значение\n")
            if int(type_of_action) == 1:
                devices_selection = func_search_in_runnconf(client_selection, devices_selection)
            elif int(type_of_action) == 2:
                func_running_config(client_selection, devices_selection)
            elif int(type_of_action) == 3:
                func_show_command(client_selection, devices_selection)
            elif int(type_of_action) == 4:
                func_dev_search_save(client_selection, devices_selection)
            elif int(type_of_action) == 5:
                break
        print(f"\n{'#' * 25}\nРабота функции завершена.\n{'#' * 25}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
      # do nothing here
        pass