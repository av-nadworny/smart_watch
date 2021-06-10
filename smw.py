import os
import json
import subprocess
from pySMART import Device
from datetime import datetime


SNAPSHOT_FILENAME = "snapshot.json"
CONFIG_FILENAME = "config.json"
DEFAULT_CONFIG = {
    'filters': {
        'dev_filter': {'*'},
        'attr_filter': {'*'}
    }
}
DEBUG = True


def print_debug(message):
    if DEBUG:
        print(f'\tdebug: {message}')


def load_json(filename):
    if os.path.exists(filename) and os.path.isfile(filename):
        with open(filename, "r") as f:
            return json.loads(f.read())
    else:
        return None


def save_json(snapshot, filename):
    with open(filename, "w") as f:
        f.write(json.dumps(snapshot))


def parse_attr_string(attr):
    result = {}
    result['id'] = attr[:3].strip()
    result['name'] = attr[4:27].strip()
    result['raw'] = attr[69:].strip()
    return result


def get_device_smart(device):
    smart = {}
    for attr in device.attributes:
        # if attr is not empty...
        if attr:
            # get values from string
            parsed_attr = parse_attr_string(str(attr))
            attr_id = parsed_attr['id']
            attr_name = parsed_attr['name']
            attr_raw = parsed_attr['raw']
            smart[attr_id] = {'name': attr_name, 'raw': attr_raw}
    return smart


def make_snapshot():
    # get storage devices' mountpoints from smartctl output
    # (pySMART DeviceList is empty)
    mp_strings = subprocess.run('smartctl.exe --scan', capture_output=True) \
        .stdout.decode('utf-8').split('\r\n')
    # get ATA devices only
    mp_list = []
    for string in mp_strings:
        if string.endswith('ATA device'):
            mp_list.append(string.split(' ')[0])
    dev_list = []
    for mountpoint in mp_list:
        dev_list.append(Device(mountpoint))

    # get SMART for each device
    smarts = {}
    for device in dev_list:
        device_name = f'{device.model} :: {device.serial}'
        device_smart = get_device_smart(device)
        smarts[device_name] = device_smart

    # assembly and return the new snapshot
    snapshot = {}
    snapshot['timestamp'] = str(datetime.utcnow())
    snapshot['devices'] = smarts

    return snapshot


def compare_smart(last_smart, new_smart):
    diff = {}
    for attr in last_smart.keys():
        last = last_smart[attr]
        new = new_smart[attr]
        if last['raw'] != new['raw']:
            diff[attr] = {
                'name': last['name'],
                'last': last['raw'],
                'new': new['raw']
            }
    return diff


def compare_snapshots(last_snapshot, new_snapshot):
    diff = {}
    # get filters
    # dev_filter = filters['dev_filter']
    # attr_filter = filters['attr_filter']
    last_devices_set = set(last_snapshot['devices'].keys())
    new_devices_set = set(new_snapshot['devices'].keys())
    # compare devices sets
    if last_devices_set != new_devices_set:
        diff['devices'] = {}
        # devices now offline (they are not in new snapshot, but in the last)
        offline_devices = last_devices_set - new_devices_set
        diff['devices']['offline'] = list(offline_devices)
        # new devices (they are not in old snapshot, but now they are)
        new_devices = new_devices_set - last_devices_set
        diff['devices']['new'] = list(new_devices)

    # devices to compare (last and new devices sets intersection)
    devices = last_devices_set & new_devices_set
    # compare SMART snapshots
    smarts_diffs = {}
    for dev in devices:
        smart_diff = compare_smart(last_snapshot['devices'][dev],
                                   new_snapshot['devices'][dev])
        if smart_diff:
            smarts_diffs[dev] = smart_diff
    if smarts_diffs:
        diff['smarts'] = smarts_diffs

    return diff


def print_report(differences):
    devices = differences.get('devices', None)
    smarts = differences.get('smarts', None)

    # print_debug(devices)
    if devices:
        print('=== DEVICES SECTION ===')
        print()

        if devices.get('offline', None):
            print(f'Devices offline: {", ".join(devices["offline"])}')
        if devices.get('new', None):
            print(f'New devices: {", ".join(devices["new"])}')

        print()

    # print_debug(smarts)
    if smarts:
        print('=== S.M.A.R.T. section ===')
        print()
        print('DEVICE')
        print('\tID :: Name :: Last value :: New value')
        print()

        for dev in smarts.keys():
            print(dev)
            attrs = smarts[dev]
            # print_debug(attrs)
            for attr in attrs.keys():
                values = attrs[attr]
                print(f"\t{attr} :: {values['name']} :: {values['last']}"
                      f" :: {values['new']}")


if __name__ == "__main__":
    save = True  # to save the new snapshot or not by default
    # make snapshot
    new_snapshot = make_snapshot()
    # load last snapshot
    last_snapshot = load_json(SNAPSHOT_FILENAME)

    # new_snapshot = load_json('snapshot_1.json')
    # last_snapshot = load_json('snapshot_2.json')

    # if last snapshot exists, compare it with new one
    if last_snapshot:
        print_debug('Will compare')
        differences = compare_snapshots(
            last_snapshot, new_snapshot)
        # if shapshots are different, print report
        if differences:
            print_debug("SMART changes found")
            print('S.M.A.R.T. changes found')
            print()
            print(f"Last snapshot timestamp: {last_snapshot['timestamp']}")
            print(f" New snapshot timestamp: {new_snapshot['timestamp']}")
            print()
            print_report(differences)
            print()
            # waiting for user action
            save_cmd = input("Commit SMART changes [y/N]? ")
            if save_cmd != 'y':
                save = False
            else:
                save = True
        else:
            print_debug('No differences')
    # save new snapshot
    if save:
        print_debug('Will save')
        save_json(new_snapshot, SNAPSHOT_FILENAME)
    else:
        print_debug('Will not save')
