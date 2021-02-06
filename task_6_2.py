a_check = False

while not a_check:
    a = input("vvedite ip: ")
    a_list = a.split('.')
    if len(a_list) != 4:
        print("neverno")
        continue

    try:
        a_list = [int(value) for value in a_list]
    except ValueError:
        print("neverno")
        continue
    octet_check = [0 <= value <= 255 for value in a_list]
    if False in octet_check:
        print("neverno")
        continue

    a_check = True
    if 1 <= int(a[0]) <= 223:
        print("unicast")
    elif 224 <= int(a[0]) <= 239:
        print("multicast")
    elif a.split('.') == ['255', '255', '255', '255']:
        print("multicast")
    elif a.split('.') == ['0', '0', '0', '0']:
        print("unassign")
    else:
        print("unused")