import os
import json
import subprocess
from pySMART import Device
from datetime import datetime


SNAPSHOT_FILENAME = "snapshot.json"
CONFIG_FILENAME = "config.json"
DEFAULT_CONFIG = {'devices': {'*'}, 'attr_ids': {'*'}}


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
    result['raw'] = attr[69:].strip()
    return result


def get_device_smart(device, attr_ids):
    smart = {}
    for attr in device.attributes:
        # if attr is not empty...
        if attr:
            # get values from string
            parsed_attr = parse_attr_string(str(attr))
            attr_id, attr_raw = parsed_attr['id'], parsed_attr['raw']
            # add attribute accordingly to "attributes" set
            if "*" in attr_ids or attr_id in attr_ids:
                smart[attr_id] = attr_raw
    return smart


def make_snapshot(config=DEFAULT_CONFIG):
    devices = config['devices']
    attr_ids = config['attr_ids']
    # get storage devices' mountpoints from smartctl output
    # (pySMART DeviceList not working)
    mp_strings = subprocess.run('smartctl.exe --scan', capture_output=True) \
        .stdout.decode('utf-8').split('\r\n')
    # get ATA devices only
    mp_list = []
    for string in mp_strings:
        if string.endswith('ATA device'):
            mp_list.append(string.split(' ')[0])
    dev_list = []
    for mountpoint in mp_list:
        # add devices accordingly to "devices" set
        if "*" in devices or mountpoint in devices:
            dev_list.append(Device(mountpoint))

    smarts = {}
    for device in dev_list:
        device_name = f'{device.model} :: {device.serial}'
        device_smart = get_device_smart(device, attr_ids)
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
    config = {'devices': {'*'}, 'attr_ids': {'5', '196', '197'}}
    new_snapshot = make_snapshot(config)
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
    # save_json(new_snapshot, SNAPSHOT_FILENAME)
