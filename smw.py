import os
import json
import subprocess
from pySMART import Device
from datetime import datetime


SNAPSHOT_FILENAME = "snapshot.json"
CONFIG_FILENAME = "config.json"
DEFAULT_CONFIG = {'dev_filter': {'*'}, 'attr_filter': {'*'}}


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

    smarts = {}
    for device in dev_list:
        device_name = f'{device.model} :: {device.serial}'
        device_smart = get_device_smart(device)
        smarts[device_name] = device_smart

    snapshot = {}
    snapshot['timestamp'] = str(datetime.utcnow())
    snapshot['devices'] = smarts

    return snapshot


def compare_snapshots(last_snapshot, new_snapshot, attributes):
    pass


def print_report(difference):
    pass


if __name__ == "__main__":
    # load config
    config = load_json(CONFIG_FILENAME)
    # make snapshot
    # config = {'dev_filter': {'*'}, 'attr_filter': {'*'}}
    new_snapshot = make_snapshot()
    print(new_snapshot)
    # load last snapshot
    last_snapshot = load_json(SNAPSHOT_FILENAME)
    # if last snapshot exists, compare two snapshots
    if last_snapshot:
        difference = compare_snapshots(last_snapshot, new_snapshot,
                                       config['attributes'])
        # if shapshots are different, print report
        if difference:
            print("Differences found!")
            print_report(difference)
            # waiting for user action
            input("Press Enter to exit...")
    # save new snapshot
    save_json(new_snapshot, SNAPSHOT_FILENAME)
