# from pySMART import Device, DeviceList
import subprocess


def get_mountpoints(dev_type='ATA device'):
    mp_strings = subprocess.run('smartctl.exe --scan', capture_output=True) \
        .stdout.decode('utf-8').split('\r\n')

    # print(dev_strings)

    mp_list = []
    for string in mp_strings:
        if string.endswith(dev_type):
            # print('!')
            mp_list.append(string.split(' ')[0])

    return mp_list


if __name__ == "__main__":
    print(get_mountpoints())
    print('###')
    # device = Device('/dev/sda')
    # print(device)
    # print(device.all_attributes())
