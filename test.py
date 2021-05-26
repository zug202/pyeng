
import syslog
import sys
#from cli import cli


# function sh_nfm_parser
####show hardware rate-limiter netflow
####Units for Config: kilo bits per second
####Allowed, Dropped & Total: aggregated bytes since last clear counters
####
####
####Module: 1
####  R-L Class             Config              Allowed              Dropped                Total
#### +----------------+----------+--------------------+--------------------+--------------------+
####  netflow               120000                    0                    0                    0
####
####
####Module: 2
####  R-L Class             Config              Allowed              Dropped                Total
#### +----------------+----------+--------------------+--------------------+--------------------+
####  netflow               120000                    0                    100                    0
####
####
####Module: 3
####  R-L Class             Config              Allowed              Dropped                Total
#### +----------------+----------+--------------------+--------------------+--------------------+
####  netflow               120000                    0                    0                    0
####
####Module: 4
####  R-L Class             Config              Allowed              Dropped                Total
#### +----------------+----------+--------------------+--------------------+--------------------+
####  netflow               120000                    0                    0                    0
####
####Module: 5
####
#### hw-rate limiter for netflow does not apply on the module
# function goes line by line and forms two list KEYS and VALUES
# line.split(': ')[1] for Module line --> module num
# values.append(drop_count[3]) for netflow line --> drop field in the list
# values.append('0') for hw-rate line --> set to 0, because nf is disabled
# function returns a dict {KEYS:VALUES}
# KEYS - module num; VALUES - drop count
#### {'1': '0', '2': '100', '3': '0', '4': '0', '5': '0'}

def sh_nfm_parser(output):
    keys = []
    values = []
    for line in output:
        line = line.strip()
        if line.startswith('Module:'):
            keys.append(line.split(': ')[1])
        elif line.startswith('netflow'):
            values.append(line.split()[3])
        elif line.startswith('hw-rate'):
            values.append('0')
    return dict(zip(keys, values))


# function syslog_required
# splits cli output into lines
# uses function sh_nfm_parser for parsing --> sh_nfm_parser(split_line)
# forms syslog state according to drops values
#### (syslog_state) = [False, True, False, False, False]
#### (syslog_needed) = True
# return common syslog state

def syslog_required(output):
    syslog_state = []
    drops_dict = sh_nfm_parser(output)
    is_dropped = False
    for value in drops_dict.values():
        is_dropped = is_dropped or (value != '0')
        print(is_dropped)
    return is_dropped


# function main
# execute cli command
# uses function syslog_required for printing syslogs accroding to syslog state (TRUE;FALSE)

def main():
    #output = cli('show hardware rate-limiter netflow')
    output = '''
    show hardware rate-limiter netflow

    Units for Config: kilo bits per second
    Allowed, Dropped & Total: aggregated bytes since last clear counters


    Module: 1
      R-L Class             Config              Allowed              Dropped                Total
     +----------------+----------+--------------------+--------------------+--------------------+
      netflow               120000                    0                    0                    0


    Module: 2
      R-L Class             Config              Allowed              Dropped                Total
     +----------------+----------+--------------------+--------------------+--------------------+
      netflow               120000                    0                    100                    0


    Module: 3
      R-L Class             Config              Allowed              Dropped                Total
     +----------------+----------+--------------------+--------------------+--------------------+
      netflow               120000                    0                    0                    0

    Module: 4
      R-L Class             Config              Allowed              Dropped                Total
     +----------------+----------+--------------------+--------------------+--------------------+
      netflow               120000                    0                    0                    0

    Module: 5

     hw-rate limiter for netflow does not apply on the module
    '''
    if syslog_required(output.splitlines()):
        syslog.syslog(1, 'Check finished. Warning! NF drops exist on the box.')
    else:
        syslog.syslog(1, 'Check finished. No NF drops.')


if __name__ == '__main__':
    try:
        main()
    except Exception: #as e:
        print('Please check input data')
        #syslog.syslog(1, '{0} {1} {2}'.format(e.__class__, e.__doc__, e.message))
