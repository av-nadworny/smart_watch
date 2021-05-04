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


if __name__ == "__main__":
    ssdb = SMARTSnapshotDB()
    # ssdb.make()
    ssdb.print_(depth=2)
    ssdb.save()
