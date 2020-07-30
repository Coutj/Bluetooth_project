import errno
import bluetooth
import dbus
import time

class Blue():

    devices_list = []
    
    def send(self, sock, message):
        ''' send messages to bluetooth device'''
        sock.send(b"\r\n" + message + b"\r\n")

    def proxyobj(self, bus, path, interface):
        ''' commodity to apply an interface to a proxy object '''
        obj = bus.get_object('org.bluez', path)
        return dbus.Interface(obj, interface)

    def filter_by_interface(self, objects, interface_name):
        """ filters the objects based on their support
            for the specified interface """
        result = []
        for path in objects.keys():
            interfaces = objects[path]
            for interface in interfaces.keys():
                if interface == interface_name:
                    result.append(path)
        return result
    
    def get_device_port(self, device_address,):
        services = bluetooth.find_service(address=device_address)
        headphone_profile = [('111E', 263,)]
        port = 0
        for dici in services:
            profile = dici.get("profiles")
            if  profile == headphone_profile and profile:
                port = dici.get("port")
                break

        return port

    def get_bluetooth_devices(self):

        bus = dbus.SystemBus()

        # we need a dbus object manager
        manager = self.proxyobj(bus, "/", "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()

        # once we get the objects we have to pick the bluetooth devices.
        # They support the org.bluez.Device1 interface
        devices = self.filter_by_interface(objects, "org.bluez.Device1")

        bt_devices = []
        
        for device in devices:
            obj = self.proxyobj(bus, device, 'org.freedesktop.DBus.Properties')
            bt_devices.append({
                "name": str(obj.Get("org.bluez.Device1", "Name")),
                "address": str(obj.Get("org.bluez.Device1", "Address")),
                "port": self.get_device_port(str(obj.Get("org.bluez.Device1", "Address")))
            })  

        headphone_devices = list()
        for device in bt_devices:
            if device.get("port") != 0:
                headphone_devices.append(device)

        self.devices_list = headphone_devices.copy()

        return self.devices_list

    def get_battery_level(self, device):
        
        address = str(device.get("address"))
        port = int(device.get("port"))

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
                    #print(f"Battery level for {device} is {blevel}%")
                    con_open = False
                else:
                    con_open = True
                    #print(line)
                    
            socket.close()
            return blevel

        except OSError as e:
            #print(f"{str(device.get("name"))} is offline", e)
            pass

