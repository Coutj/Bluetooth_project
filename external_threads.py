import queue
import blueP


blueClass = blueP.Blue()

def producer(queue, event):
    if event.is_set() == True:
        lista_dispositivos = blueClass.get_bluetooth_devices()
        queue.put(lista_dispositivos)
        event.clear()

