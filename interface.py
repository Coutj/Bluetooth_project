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
    pip_devices = queue.Queue()
    pip_battery = queue.Queue()

    def __init__(self, master):
        self.master = master
        self.master.title("Headsets")
        self.master.geometry("190x130")
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
        self.disable_button()
        self.listBox.delete(0,tk.END)
        self.event = threading.Event()
        self.event.set()
        thread_get_bt_devices = threading.Thread(target=external_threads.get_headsets_devices, args=(self.pip_devices, self.event,), daemon=True)
        thread_get_bt_devices.start()
        self.master.after(100, self.process_queue_get_devices)

    def hide_bt_icon(self):
        self.canvas.grid_remove()
        
    def show_bt_icon(self):
        self.canvas.grid()
   
    def process_queue_get_devices(self):
        try:
            message = self.pip_devices.get(block=False)
            blueClass.devices_list = message
            self.pop_listBox()
            self.show_bt_icon()
            self.enable_button()
        except Exception as e:         
            if self.state == True:
                self.state = False
                self.hide_bt_icon()
            else:
                self.state = True
                self.show_bt_icon()
    
            self.master.after(300, self.process_queue_get_devices)

    def process_queue_get_battery(self, device_index):
        try:
            message = self.pip_battery.get(block=False)
            message = " " +str(message) + "%"
            self.add_battery_level_lb(message, device_index)
            self.show_bt_icon()
            self.enable_button()
        except Exception as e:
            if self.state == True:
                self.state = False
                self.hide_bt_icon()
            else:
                self.state = True
                self.show_bt_icon()
                
            self.master.after(100, self.process_queue_get_battery, device_index)

    def enable_button(self):
        self.button.configure(state=tk.NORMAL)
        main_ui.button.bind("<Button-1>", main_ui.handle_button_click)
        
    def disable_button(self):
        self.button.config(state=tk.DISABLED)
        main_ui.button.unbind("<Button-1>")

    def pop_listBox(self):
        self.listBox.delete(0, tk.END)

        for device in blueClass.devices_list:
                self.listBox.insert(tk.END, " " + str(device.get("name").upper()) + " ?")

    def add_battery_level_lb(self, battery_level, index):
        line_text = self.listBox.get(index).split(" ")
        line_text = line_text[1:len(line_text) - 1]

        new_line = " "
        for word in line_text:
            new_line += word + " "

        new_line += str(battery_level)
        self.listBox.delete(index)
        self.listBox.insert(index, new_line)

    def handle_listBox_click(self, event):
        self.disable_button()
        selected_line = int(str(self.listBox.curselection()[0]))
        selected_device = dict()
        selected_device = blueClass.devices_list[selected_line].copy()

        self.event = threading.Event()
        self.event.set()
        thread_get_battery_level = threading.Thread(target=external_threads.get_battery_level, args=(self.pip_battery, self.event, selected_device,), daemon=True)
        thread_get_battery_level.start()
    
        self.master.after(100, self.process_queue_get_battery, selected_line)


window = tk.Tk()
main_ui = GUI(window)
main_ui.button.bind("<Button-1>", main_ui.handle_button_click)
main_ui.listBox.bind('<Double-1>', main_ui.handle_listBox_click)

window.mainloop()

