# smart_watch
S.M.A.R.T. attributes changing watcher

## Purposes
**Smart_watch** is a system utility for supervision of the ATA devices' SMART
attributes. If you need to be aware of the health of your drives, this script
can probably be useful to you.

## Description
**Smart_watch** makes snapshots of the devices' SMART attributes lists and saves
them to the local file. Next time it runs, the script compares previously saved
snapshot with new one and warns you about the changes found in the attributes
and devices you are interested in.

## Operating system / Programming language
Initially, **smart_watch** is developed and used under Windows 10 operating system
and Python 3.9.4. The ability to run on other OS/PL versions has not been
specially researched yet.

## Requirements
* Python interpreter installed
* Python pySMART module installed
* smartctl binary in **smart_watch** folder / system PATH / fully installed

## Using
Run **smw.py** script for the first time and explore the **"snapshot.json"** file
that just appeared for the devices names and SMART attributes IDs which you need.
Write them to the **DEFAULT_FILTER** variable in the **smw.py** script as you can
see in example:

    DEFAULT_FILTER = {
        'devices': {
            'WDC WD20EARX-00PASB0 :: WD-xxxxxxxxx523',
            'WDC WD20EARX-00PASB0 :: WD-xxxxxxxxx347',
            'ST500DM002-1BD142 :: WxxxxxxR'
            },
        'attributes': {'5', '196', '197'}
    }

or you can always to use all the devices and attributes:

    DEFAULT_FILTER = {
        'devices': {'*'},
        'attributes': {'*'}
    }

but watching all of attributes is "little" unefficient I think.

Finally, you may need to autorun **smw.py** script for each start of OS or more
often as you need.

Each time the script will find any changes of the specified attributes or
devices onlines/offlines, the script will warn you about it and wait for your
action.