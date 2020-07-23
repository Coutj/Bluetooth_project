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
    blueClass.get_bluetooth_devices()

    index = 0
    for device in blueClass.devices_list:
        listBox.insert(index, device[1] + " - " + device[0]  + " ?")
        index= index + 1

def handle_listBox_click(event):
    selected_line = listBox.curselection()
    listBox_string = listBox.get(selected_line)
    listBox_string_split = listBox_string.split(" ")

    address = listBox_string_split[len(listBox_string_split) - 2]
    selected_device = []
    for device in blueClass.devices_list:
        if device[0] == address:
            selected_device = device
            
    battery_level = blueClass.get_battery_level(selected_device)
    listBox.delete(selected_line)
    listBox_string = selected_device[1] + " - " +selected_device[0]
    listBox.insert(selected_line, listBox_string + " " +  str(battery_level) + "%")

button.bind("<Button-1>", handle_button_click)
listBox.bind('<Double-1>', handle_listBox_click)

window.mainloop()
