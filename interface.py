from PIL import Image, ImageTk
import threading
import tkinter as tk
import tkinter.font
import blueP
import queue
import external_threads
import errno

blueClass = blueP.Blue()

class GUI:
    state = True
    pip = queue.Queue()

    def __init__(self, master):
        self.master = master
        self.bigfont = tkinter.font.Font(family="Helvetica",size=9)

        self.button = tk.Button(master=self.master, text="Load", height=2)
        self.button.grid(row=1, column=0, sticky=tk.W, padx=2)

        self.image = Image.open('/home/juan/Documents/Learning_python/bluetooth_project/images/bluetooth_image.png')
        self.bt_icon = ImageTk.PhotoImage(self.image)
        self.canvas = tk.Canvas(master, width = 30, height = 30) 
        self.canvas.create_image(15,15,image=self.bt_icon)
        self.canvas.grid(row=1, column=0, sticky=tk.W, padx=60)
  
        self.listBox = tk.Listbox(master=master, font=self.bigfont, width=26, height=6)
        self.listBox.grid(row=2, column=0,  sticky="we", padx=2)

    def handle_button_click(self, event):   
        self.listBox.delete(0,tk.END)
        self.event = threading.Event()
        self.event.set()
        thread_get_bt_devices = threading.Thread(target=external_threads.producer, args=(self.pip, self.event,), daemon=True)
        thread_get_bt_devices.start()
        self.master.after(100, self.process_queue, self.pip)

    def hide_bt_icon(self):
        self.canvas.grid_remove()

    def show_bt_icon(self):
        self.canvas.grid()

    def process_queue(self, queue):
        try:
            blueClass.devices_list = queue.get(0)
            self.pop_listBox()
            self.show_bt_icon()
        except Exception as e:         
            if self.state == True:
                self.state = False
                self.hide_bt_icon()
            else:
                self.state = True
                self.show_bt_icon()
    
            self.master.after(300, self.process_queue, queue)

    def pop_listBox(self):
        for device in blueClass.devices_list:
                self.listBox.insert(tk.END, " " + str(device.get("name").upper())  + " ?")

    def handle_listBox_click(self, event):
        
        selected_line = int(str(self.listBox.curselection()[0]))
        selected_device = dict()
        selected_device = blueClass.devices_list[selected_line].copy()      
        battery_level = blueClass.get_battery_level(selected_device)
        self.listBox.delete(selected_line)
        self.listBox.insert(selected_line, " " + selected_device.get("name").upper() + " " +  str(battery_level) + "%")


window = tk.Tk()
window.title("Headsets")
window.geometry("190x130")
main_ui = GUI(window)

main_ui.button.bind("<Button-1>", main_ui.handle_button_click)
main_ui.listBox.bind('<Double-1>', main_ui.handle_listBox_click)

window.mainloop()

