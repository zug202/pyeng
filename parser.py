import os
import re

arg_expression = "\sip address"
arg_file = '/Users/atunin/Downloads/python/pyneg-tasks/exercises/15_module_re/config_r1.txt'

re_expression = re.compile ("^.*({0}).*$".format(arg_expression))

# config block is a sequence of lines where first line starts with anything but a whitespase character (see re_new_block)
# sunsequent lines start with a whitespase character
# config block may consists of a single line
# Exmaple:
##vlan 1
## name default_vlan

re_new_block = re.compile ("^\S.*$")

# 'is_match' is a flag of arg_expression being part of a line
is_match = False

temp_config_block = []
result_config_block = []
with open(arg_file) as file_obj:
    for line in file_obj:
        re_new_block_obj = re_new_block.match(line)
        re_expression_obj = re_expression.match(line)
        #print(re_new_block_obj)
        #print(re_expression_obj)
# if this is a new config block, then there might be a match in previous config block
# if there is a match, then previous config block stored in 'temp_config_block' should be
# copied to 'result_config_block' and 'is_match' flag is set to False

        if (re_new_block_obj):
            if (is_match):
                for each in temp_config_block:
                    result_config_block.append(each)
                is_match = False
# once evaluation of 'is_match' flash complete, temp_config_block can be zerotized
            temp_config_block = []

# every line is checked for a match. if yes, then 'is_match' flash is set to True

        if (re_expression_obj):
            is_match = True

# every line is copied in 'temp_config_block'
        temp_config_block.append(line)
        #print(temp_config_block)
# printing the result
for each in result_config_block:
# every line has \n in the end of it, so you do not what to print it
    print(each, end='')

