import errno
import bluetooth

class Blue():

    devices_list = []

    def send(self, sock, message):
        sock.send(b"\r\n" + message + b"\r\n")

    def get_bluetooth_devices(self):
        devices = bluetooth.discover_devices(lookup_names=True)
        services = bluetooth.find_service()
        headphone_class = ['111E','1203']

        devices_index = 0
        drop_devices =[]
        for device in devices:
            for item in services:
                if item.get('host') == device[0]:
                    if item.get('service-classes') == headphone_class:
                        port = ()
                        port += (item.get('port'),)
                        devices[devices_index] += port
                        break
                    else:
                        drop_devices.append(devices_index)
                        break
            devices_index += 1

        for index in drop_devices:
            del devices[index]

        self.devices_list = devices.copy()

    def get_battery_level(self, device):
        
        address = device[0]
        port = device[2]

        try:
            socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            socket.connect((address, port))

            con_open = True
            while con_open:

                line = socket.recv(128)
                blevel = -1

                if b"BRSF" in line:
                    self.send(socket, b"+BRSF: 1024")
                    self.send(socket, b"OK")
                elif b"CIND=" in line:
                    self.send(socket, b"+CIND: (\"battchg\",(0-5))")
                    self.send(socket, b"OK")
                elif b"CIND?" in line:
                    self.send(socket, b"+CIND: 5")
                    self.send(socket, b"OK")
                elif b"BIND=?" in line:
                    self.send(socket, b"+BIND: (2)")
                    self.send(socket, b"OK")
                elif b"BIND?" in line:
                    self.send(socket, b"+BIND: 2,1")
                    self.send(socket, b"OK")
                elif b"XAPL=" in line:
                    self.send(socket, b"+XAPL: iPhone,7")
                    self.send(socket, b"OK")
                elif b"IPHONEACCEV" in line:
                    parts = line.strip().split(b',')[1:]
                    if len(parts) > 1 and (len(parts) % 2) == 0:
                        parts = iter(parts)
                        params = dict(zip(parts, parts))
                        if b'1' in params:
                            blevel = (int(params[b'1']) + 1) * 10
                elif b"BIEV=" in line:
                    params = line.strip().split(b"=")[1].split(b",")
                    if params[0] == b"2":
                        blevel = int(params[1])
                else:
                    self.send(socket, b"OK")

                if blevel != -1:
                    print(f"Battery level for {device[1]} is {blevel}%")
                    con_open = False
                else:
                    con_open = True
                    print(line)
                    
            socket.close()
            return blevel

        except OSError as e:
            print(f"{device} is offline", e)