from PyQt5 import QtWidgets, QtCore, QtGui
import queue
import threading
import sys

import blueP
import external_threads
from GUI import GUI

class main_window(QtWidgets.QMainWindow):

    state = True
    pip_devices = queue.Queue()
    pip_battery = queue.Queue()
    process_queue_get_battery_delay = 200
    process_queue_get_devices_delay = 300
    limit_time_to_reach_device = 100 * process_queue_get_battery_delay
    process_battery_timer = 0

    def __init__(self):
        super(main_window, self).__init__()
        self.ui = GUI.Ui_window()
        self.ui.setupUi(self)
        self.ui.load_button.clicked.connect(self.handle_button_click)
        self.ui.listBox.doubleClicked.connect(self.handle_listBox_click)

    def handle_button_click(self):
        self.disable_button()
        self.ui.listBox.clear()
        self.event = threading.Event()
        self.event.set()
        thread_get_bt_devices = threading.Thread(target=external_threads.get_headsets_devices, args=(self.pip_devices, self.event,), daemon=True)
        thread_get_bt_devices.start()
        QtCore.QTimer.singleShot(100, self.process_queue_get_devices)

    def handle_listBox_click(self, event):
        self.disable_button()     
        selected_line = self.ui.listBox.currentRow()
        selected_device = dict()
        selected_device = blueClass.devices_list[selected_line].copy()
        self.event = threading.Event()
        self.event.set()
        thread_get_battery_level = threading.Thread(target=external_threads.get_battery_level, args=(self.pip_battery, self.event, selected_device,), daemon=True)
        thread_get_battery_level.start()
        QtCore.QTimer.singleShot(100, lambda: self.process_queue_get_battery(selected_line))

    def process_queue_get_devices(self):
        try:
            self.pip_devices.get(block=False)
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

            QtCore.QTimer.singleShot(self.process_queue_get_devices_delay, self.process_queue_get_devices)

    def process_queue_get_battery(self, device_index):
        try:
            self.process_battery_timer += self.process_queue_get_battery_delay 
            message = self.pip_battery.get(block=False)
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
            
            if self.process_battery_timer >= self.limit_time_to_reach_device:
                self.info_message("Impossible to reach {}".format(blueClass.devices_list[device_index].get("name")))
                self.enable_button()
                self.show_bt_icon()
                self.process_battery_timer = 0
            else:
                QtCore.QTimer.singleShot(self.process_queue_get_battery_delay, lambda: self.process_queue_get_battery(device_index))

    def pop_listBox(self):
        for device in blueClass.devices_list:
            self.ui.listBox.addItem(str(device.get("name").upper()))   

    def add_battery_level_lb(self, battery_level, index):
        self.ui.listBox.takeItem(index)
        
        font = QtGui.QFont()
        font.setPointSize(11)
        item = QtWidgets.QListWidgetItem(blueClass.devices_list[index].get("name").upper())
        item.setFont(font)
        widget = QtWidgets.QWidget()
        widgetLayout = QtWidgets.QHBoxLayout()
        widgetLayout.setContentsMargins(200,2,0,2)
        progressBar = self.listbox_progressBar(battery_level)   
        widgetLayout.addWidget(progressBar)
        widget.setLayout(widgetLayout)
        
        self.ui.listBox.insertItem(index, item)
        self.ui.listBox.setItemWidget(item, widget)
    
    def disable_button(self):
        self.ui.load_button.setEnabled(False)

    def enable_button(self):
        self.ui.load_button.setEnabled(True)

    def show_bt_icon(self):
        self.ui.bt_icon.show()

    def hide_bt_icon(self):
        self.ui.bt_icon.hide()

    def listbox_progressBar(self, battery_level):
        #progress bar
        battery_level = int(battery_level)
        font = QtGui.QFont()
        font.setPointSize(9)
        battery_bar = QtWidgets.QProgressBar(self.ui.centralwidget)
        battery_bar.setFont(font)
        battery_bar.setProperty("value", battery_level)
        battery_bar.setObjectName("battery_bar") 
        battery_bar.setMaximumWidth(50)
        battery_bar.setMaximumHeight(16)
        
        return battery_bar

    def info_message(self, message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Info")
        msg.exec()

if __name__ == "__main__":
    blueClass = blueP.Blue()
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    application = main_window()
    application.show()

    sys.exit(app.exec_())