# Bluetooth_project
GUI application to present the battery level of bluetooth headsets in linux (Inspired by TheWeirdDev project)

*This application uses dbus modules. It will not work on windows.

# How to run this application:

1. Install Dependencies:
```bash
sh setup.sh
```

2. Double click the executable file or run on terminal
```bash
python main.py
```

Note:
if you see errors like-

```
    In file included from bluez/btmodule.c:20:
    bluez/btmodule.h:5:10: fatal error: bluetooth/bluetooth.h: No such file or directory
        5 | #include <bluetooth/bluetooth.h>
          |          ^~~~~~~~~~~~~~~~~~~~~~~
    compilation terminated.
    error: command 'x86_64-linux-gnu-gcc' failed with exit status 1
```

install libbluetooth-dev

```
sudo apt install libbluetooth-dev
```

optional step: run add_to_interface to put the program in your system menu

# How to use it

(1) Press de load button to get all paired headsets.

(2) Double click the headset name that appeared in the list and wait for the battery indicator.



# Donate

### <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=SMXHLS6XWHQPC">Click to donate</a>






# Credits

https://github.com/TheWeirdDev/

Icons made by:

icon king: https://freeicons.io/profile/3

Smashicons: https://www.flaticon.com/br/autores/smashicons

