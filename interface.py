import tkinter as tk
import blueP

blueClass = blueP.Blue()

window = tk.Tk()
window.geometry("300x100")

top_frame = tk.Frame(master=window, height=30)
top_frame.pack(fill=tk.BOTH)

button = tk.Button(master=top_frame, text="Load")
button.place(x=4, y=2)

'''info_frame = tk.Frame(master=top_frame, height=20, width=20, bg='green')
info_frame.place(x=70, y=6)'''

listBox_frame = tk.Frame(master=window)
listBox_frame.pack(fill=tk.BOTH)
listBox = tk.Listbox(master=listBox_frame)
listBox.pack(expand = True, fill=tk.BOTH, side=tk.BOTTOM)


def handle_button_click(event):
   
    print("cliquei")
    listBox.delete(0,tk.END)
    blueClass.get_bluetooth_devices()
    index = 0
    for device in blueClass.devices_list:
        listBox.insert(index, str(device.get("name"))  + " ?")
        index += 1

def handle_listBox_click(event):
    
    selected_line = int(str(listBox.curselection()[0]))
    selected_device = dict()
    selected_device = blueClass.devices_list[selected_line].copy()      
    battery_level = blueClass.get_battery_level(selected_device)
    listBox.delete(selected_line)
    listBox.insert(selected_line, selected_device.get("name") + " " +  str(battery_level) + "%")

button.bind("<Button-1>", handle_button_click)
listBox.bind('<Double-1>', handle_listBox_click)

window.mainloop()
