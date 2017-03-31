import subprocess
import os
import sys
__version__ = "1.0"

TYPE = {
    0:  'bios',
    1:  'system',
    2:  'base board',
    3:  'chassis',
    4:  'processor',
    7:  'cache',
    8:  'port connector',
    9:  'system slot',
    10: 'on board device',
    11: 'OEM strings',
    #13: 'bios language',
    15: 'system event log',
    16: 'physical memory array',
    17: 'memory device',
    19: 'memory array mapped address',
    24: 'hardware security',
    25: 'system power controls',
    27: 'cooling device',
    32: 'system boot',
    41: 'onboard device',
    }


def parse_dmi(content):
    """
    Parse the whole dmidecode output.
    Returns a list of tuples of (type int, value dict).
    """
    info = []
    lines = iter(content.strip().splitlines())
    while True:
        try:
            line = lines.next()
        except StopIteration:
            break

        if line.startswith('Handle 0x'):
            typ = int(line.split(',', 2)[1].strip()[len('DMI type'):])
            if typ in TYPE:
                info.append((TYPE[typ], _parse_handle_section(lines)))
    return info


def _parse_handle_section(lines):
    """
    Parse a section of dmidecode output

    * 1st line contains address, type and size
    * 2nd line is title
    * line started with one tab is one option and its value
    * line started with two tabs is a member of list
    """
    data = {
        '_title': lines.next().rstrip(),
        }

    for line in lines:
        line = line.rstrip()
        if line.startswith('\t\t'):
            data[k].append(line.lstrip())
        elif line.startswith('\t'):
            k, v = [i.strip() for i in line.lstrip().split(':', 1)]
            if v:
                data[k] = v
            else:
                data[k] = []
        else:
            break

    return data


def profile():
    if os.isatty(sys.stdin.fileno()):
        content = _get_output()
    else:
        content = sys.stdin.read()

    info = parse_dmi(content)
    _show(info)


def _get_output():
    output = subprocess.check_output(
        'PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin '
        'sudo dmidecode', shell=True)
    # print output
    return output


def _show(info):
    def _get(i):
        return [v for j, v in info if j == i]

    system = _get('system')[0]
    print ' ========== Hardware Information ==================== \n'
    print ' Manufacturer: %s \n Product Name: %s \n SN: %s \n UUID: %s' % (
        system['Manufacturer'],
        system['Product Name'],
        system['Serial Number'],
        system['UUID'],
        )
    print ' =================================================== \n'
    for cpu in _get('processor'):
        # print ' CPU: %s %s %s (Core: %s, Thead: %s)' % (
        #     cpu['Manufacturer'],
        #     cpu['Family'],
        #     cpu['Max Speed'],
        #     cpu['Core Count'],
        #     cpu['Thread Count'],
        #     )
        print ' CPU: ' \
              ' \n + %s (Core: %s, Thead: %s)' % (
            cpu['Version'],
            cpu['Core Count'],
            cpu['Thread Count'],
        )
    for cache in _get('cache'):
        print ' + %s: Installed Size: %s, Maximum Size: %s' % (
            cache['Socket Designation'],
            cache['Installed Size'],
            cache['Maximum Size'],
        )

    print ' =================================================== \n'
    cnt, total, unit = 0, 0, None
    for mem in _get('memory device'):
        if mem['Size'] == 'No Module Installed':
            continue
        i, unit = mem['Size'].split()
        cnt += 1
        total += int(i)
    print ' RAM: ' \
          '\n + %d memory stick(s), ' \
          '\n + %d %s in total' % (
        cnt,
        total,
        unit,
        )
    for physical_memory in _get('physical memory array'):
        print ' + Maximum Supported Memory: %s \n' % (
            physical_memory['Maximum Capacity'],
            )
    print ' =================================================== \n'

    for bios in _get('bios'):
        print ' BIOS: ' \
              '\n + Version: %s, ' \
              '\n + BIOS Version String: %s, ' \
              '\n + Release Date: %s ' % (
            bios['BIOS Revision'],
            bios['Version'],
            bios['Release Date'],
        )

    print ' =================================================== \n'

    for baseboard in _get('base board'):
        print ' Motherboard: ' \
              '\n + Product Name: %s, ' \
              '\n + Version: %s, ' \
              '\n + Serial Number: %s ' % (
            baseboard['Product Name'],
            baseboard['Version'],
            baseboard['Serial Number'],
              )

    print ' =================================================== \n'
    print ' Disk:'
    result_disk = subprocess.Popen("sudo lshw -class disk | grep -iE 'description|product|vendor|serial|size'",
                               stdout=subprocess.PIPE, shell=True).communicate()[0]
    print result_disk

    print ' =================================================== \n'
    print ' Network:'
    result_network = subprocess.Popen("sudo lshw -class network | grep -iE 'description|product|vendor|serial|size'",
                               stdout=subprocess.PIPE, shell=True).communicate()[0]
    print result_network

if __name__ == '__main__':
    profile()
