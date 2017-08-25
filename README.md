You need BlueZ 5 and python dbus and GObject.

The code is mostly inspired by BlueZ python example,
see https://git.kernel.org/pub/scm/bluetooth/bluez.git/tree/test

Code have been tested on BlueZ 5.45.

To run the chat example you need.
Two devices with Bluetooth enabled :)

To pair both device using bluetoothctl.
Then run the server on one machine:
./BlueZchat.py -s
And the client on another one:
./BlueZchat.py -c
