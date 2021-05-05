'''
Snapshot structure:
#1 Timestamp (Date and time)
#2 Devices (List of device records, see below)

Device record structure:
#1 Model (string)
#2 Serial Number (string)
#3 Attributes (list of strings)

{'timestamp': {
    'device': {
        'attributes': [list of strings]
    }
}
'''

from pySMART import Device
import subprocess
from datetime import datetime
import json
import os


class SMARTSnapshotDB:
    def __init__(self, db_filename='snapshots.json'):
        self.__db_filename = db_filename
        self.__snapshots = {}

        self.__load()

    def print_(self, depth=0):
        if depth <= 3:
            for ss_key in self.__snapshots.keys():
                print(f'Timestamp: {ss_key}')

                if depth <= 2:
                    snapshot = self.__snapshots[ss_key]
                    for dev_key in snapshot.keys():
                        print(f'\tDevice: {dev_key}')

                        if depth <= 1:
                            attributes = snapshot[dev_key]
                            for attr in attributes:
                                print(f'\t\t{attr}')

    def __load(self):
        if os.path.exists(self.__db_filename) and \
           os.path.isfile(self.__db_filename):
            db_string = ''
            with open(self.__db_filename, 'r') as f:
                db_string = f.read()
            self.__snapshots = json.loads(db_string)

    def save(self):
        with open(self.__db_filename, 'w') as f:
            f.write(json.dumps(self.__snapshots))

    def __get_mountpoints(self):
        mp_strings = subprocess.run('smartctl.exe --scan',
                                    capture_output=True) \
            .stdout.decode('utf-8').split('\r\n')

        mp_list = []
        for string in mp_strings:
            if string.endswith('ATA device'):
                mp_list.append(string.split(' ')[0])

        return mp_list

    def __get_smart_attr_list(self, dev_attrs):
        attr_list = []
        for attr in dev_attrs:
            if attr:
                attr_list.append(str(attr))
        return attr_list

    def make(self):
        snapshot = {}
        timestamp = str(datetime.utcnow())

        mountpoints = self.__get_mountpoints()
        for mountpoint in mountpoints:
            device = Device(mountpoint)
            key = device.model + '::' + device.serial
            snapshot[key] = self.__get_smart_attr_list(device.attributes)

        self.__snapshots[timestamp] = snapshot

    def compare(self, younger_ss_offset=0, older_ss_offset=1):
        warnings = False

        ss_max_id = len(self.__snapshots) - 1
        ss_keys = list(self.__snapshots.keys())

        if younger_ss_offset > ss_max_id:
            print(f'Error: younger_ss_offset is out of index.\n'
                  f'Valid offset is up to {ss_max_id}')
            return False
        else:
            yng_ss_key = ss_keys[-1-younger_ss_offset]

        if older_ss_offset > ss_max_id:
            print(f'Error: older_ss_offset is out of index.\n'
                  f'Valid offset is up to {ss_max_id}')
            return False
        else:
            old_ss_key = ss_keys[-1-older_ss_offset]

        print(f'Comparing snapshots...\n'
              f'younger snapshot: offset <{younger_ss_offset}> '
              f'timestamp <{yng_ss_key}>\n'
              f'older snapshot: offset <{older_ss_offset}> '
              f'timestamp <{old_ss_key}>')

        old_dev_keys = list(self.__snapshots[old_ss_key].keys())
        yng_dev_keys = list(self.__snapshots[yng_ss_key].keys())
        for old_dev_key in old_dev_keys:
            if old_dev_key in yng_dev_keys:
                # compare SMART attributes
                yng_dev_keys.remove(old_dev_key)
            else:
                print(f'Warning: device <{old_dev_key}> is offline now!')
                warnings = True

        if yng_dev_keys:
            print('Warning: new devices is online now:')
            for key in yng_dev_keys:
                print(f'<{key}>')
            warnings = True

        if warnings:
            print('There were some warnings during compare!')
            # input('Press enter to continue...')


if __name__ == "__main__":
    ssdb = SMARTSnapshotDB()
    # ssdb.make()
    ssdb.print_(depth=2)
    ssdb.compare(1, 2)
    # ssdb.save()
