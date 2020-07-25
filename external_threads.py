import queue
import blueP
import time


blueClass = blueP.Blue()

def producer(queue, event):
    print(event.is_set())
    if event.is_set() == True:
        lista_dispositivos = blueClass.get_bluetooth_devices()
        queue.put(lista_dispositivos)
        event.clear()

