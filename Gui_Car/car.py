# threading -supports multi-threading for concurrent task execution
import threading

# numpy - provides numerical and array operations, particularly for handling multidimensional arrays
import numpy as np

# serial - communication with external devices through serial ports, used for Arduino communication
import serial

# PyQt5 - enables GUI creation using Python with the Qt framework
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QLineEdit, QWidget

# matplotlib - offers 2D plotting for creating charts and visualizations
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.cm as cm

# seaborn - Enhances the visual aesthetics of matplotlib plots and provides statistical data visualization tools
import seaborn as sns

# Define a Window class that inherits from QMainWindow
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        # Instance variables for communication with Arduino and data retrieval control
        self.arduino = None  # Represents the Serial connection to the Arduino (initialized as None)
        self.data = False  # Flag to control data retrieval from Arduino (False by default)

        # Main UI setups
        self.setWindowTitle('Car Controller')  # Set the window title
        self.setGeometry(100, 100, 600, 400)  # Set the window's position and size
        widget = QWidget(self)  # Create a main widget
        self.setCentralWidget(widget)  # Set the main widget for the window

        # Set the main layout
        self.main_layout = QVBoxLayout(widget)  # Create a vertical box layout for the main widget

        # Create a sub-layout for the plot and control buttons
        self.sub_layout = QHBoxLayout()  # Create a horizontal box layout for the sub-layout

        # Create a Figure and attach it to a FigureCanvas
        self.fig = Figure()  # Create a matplotlib Figure
        self.canvas = FigureCanvas(self.fig)  # Create a FigureCanvas to display the Figure
        self.ax = self.fig.add_subplot(111)  # Create a subplot in the Figure
        self.ax.set_xlim([0, 60])  # Set the x-axis limits for the subplot
        self.ax.set_ylim([0, 60])  # Set the y-axis limits for the subplot
        self.ax.set_xticks([x for x in range(-10, 70, 10)])  # Set x-axis ticks at regular intervals
        self.ax.set_yticks([x for x in range(-10, 70, 10)])  # Set y-axis ticks at regular intervals

        # Create the side layout for buttons and textbox
        self.side_layout = QVBoxLayout()

        # Create buttons and textbox
        self.forward_btn = QPushButton("FORWARD", self)
        self.left_btn = QPushButton("LEFT", self)
        self.right_btn = QPushButton("RIGHT", self)
        self.backward_btn = QPushButton("BACKWARD", self)
        self.stop_btn = QPushButton("STOP", self)
        self.textbox = QLineEdit(self)
        self.textbox.setDisabled(True)  # Disable the QLineEdit to prevent user input
        self.getdata_btn = QPushButton("Get Data", self)
        self.stopgetdata_btn = QPushButton("Stop Get Data", self)

        # Connect buttons to their functions
        self.forward_btn.clicked.connect(self.move_forward)
        self.left_btn.clicked.connect(self.move_left)
        self.right_btn.clicked.connect(self.move_right)
        self.backward_btn.clicked.connect(self.move_backward)
        self.stop_btn.clicked.connect(self.Stop_move)
        self.getdata_btn.clicked.connect(self.get_data)
        self.stopgetdata_btn.clicked.connect(self.stop_get_data)

        # Add widgets to the side layout
        self.side_layout.addWidget(self.forward_btn)
        self.side_layout.addWidget(self.left_btn)
        self.side_layout.addWidget(self.right_btn)
        self.side_layout.addWidget(self.backward_btn)
        self.side_layout.addWidget(self.stop_btn)
        self.side_layout.addWidget(self.textbox)
        self.side_layout.addWidget(self.getdata_btn)
        self.side_layout.addWidget(self.stopgetdata_btn)

        # Add widgets to the sub-layout
        self.sub_layout.addWidget(self.canvas, 80)  # 80% width for the plot
        self.sub_layout.addLayout(self.side_layout, 20)  # 20% width for the side buttons

        # Add the sub-layout to the main layout
        self.main_layout.addLayout(self.sub_layout, 3)  # 75% height for the sub layout

        # Create a QHBoxLayout for the bottom layout, where buttons will be horizontally aligned
        self.bottom_layout = QHBoxLayout()

        # Create two QPushButton widgets for "SERIAL OPEN" and "SERIAL CLOSE" actions
        self.serial_open_btn = QPushButton("SERIAL OPEN", self)
        self.serial_close_btn = QPushButton("SERIAL CLOSE", self)

        # Add the "SERIAL OPEN" and "SERIAL CLOSE" buttons to the bottom layout horizontally
        self.bottom_layout.addWidget(self.serial_open_btn)
        self.bottom_layout.addWidget(self.serial_close_btn)

        # Connect button clicks to their respective functions:
        self.serial_open_btn.clicked.connect(self.serial_open)
        self.serial_close_btn.clicked.connect(self.serial_close)

        # Add the bottom layout to the main layout
        self.main_layout.addLayout(self.bottom_layout, 1)  # 25% height for the bottom layout

    def move_forward(self):
        print('CAR MOVING FORWARD')
        self.send_command_to_arduino('Forward')   # Send the command "Forward" to the Arduino

    def move_left(self):
        print('CAR MOVING LEFT')
        self.send_command_to_arduino('Left')   # Send the command "Left" to the Arduino

    def move_right(self):
        print('CAR MOVING RIGHT')
        self.send_command_to_arduino('Right')  # Send the command "Right" to the Arduino

    def Stop_move(self):
        print('CAR STOP MOVE')
        self.send_command_to_arduino('Stop')   # Send the command "Stop" to the Arduino

    def move_backward(self):
        print('CAR MOVING BACKWARD')
        self.send_command_to_arduino('Backward')  # Send the command "Backward" to the Arduino

    def get_data(self):
        self.data = True  # Set the data flag to True, enabling data retrieval
        # Start a new thread to run the Data_graph method in the background for continuous data retrieval
        data_retrieval_thread = threading.Thread(target=self.Data_graph)
        data_retrieval_thread.start()

    def stop_get_data(self):
        self.data = False  # Set the data flag to False, stopping data retrieval

    def Data_graph(self):
        # Send the command 'Data' to the Arduino to start data transmission
        self.send_command_to_arduino('Data')

        # Initialize variables to store data and times
        times = 0
        values = []
        for i in range(4):
            values.append([])

        # Continuous data retrieval loop as long as self.data is True
        while self.data:
            value = self.read_from_arduino()

            # Check the received data and process accordingly
            if value not in ["Stop", "Next"]:
                # Convert the received data to float and append it to the current 'times' index in values
                value = float(value)
                print(value)
                values[times].append(value)
            elif value == "Next":
                # When "Next" is received, it indicates a new set of data is starting, so increment 'times'
                times += 1
            else:
                # When "Stop" is received, stop the data retrieval loop by setting self.data to False
                self.data = False

        # After data retrieval is finished, print the collected data for each 'times' index
        for i in range(len(values)):
            print("i: " + str(i))
            print(values[i])

        # Extract data from the first index of 'values' and reshape it to form a 10xN matrix
        values = np.array(values[0])
        print(values)
        print(len(values))
        values = values[:len(values) - len(values) % 10]
        data = values.reshape(10, -1)
        # Create a heatmap using seaborn and display it on the GUI
        cmap = cm.get_cmap("inferno")
        heatmap = sns.heatmap(data, vmin=min(values), vmax=max(values), cmap=cmap, annot=True, fmt=".2f", ax=self.ax)
        # Show the updated plot on the GUI
        self.canvas.draw()

    def serial_open(self):   # Replace 'COM8' with your Arduino's port
        try:
            self.arduino = serial.Serial('COM8', 9600)  # Connect to the Arduino board
            # Check if the connection was successful and show a popup message accordingly:
            if self.arduino.is_open:
                self.show_popup('Serial connection opened successfully')
            else:
                self.show_popup('Failed to open serial connection')
        except serial.SerialException as e:
            self.show_popup(f'Failed to open serial connection: {e}')

    def serial_close(self):
        if self.arduino and self.arduino.is_open:
            # Check if there is an open connection and close it if present
            self.arduino.close()

    def send_command_to_arduino(self, command):
        # The input 'command' is expected to be a string, which is encoded before sending
        if self.arduino is not None and self.arduino.is_open:
            self.arduino.write(command.encode())

    def read_from_arduino(self):
        # It returns the received data as a decoded string with leading and trailing whitespaces removed
        if self.arduino is not None and self.arduino.is_open:
            return self.arduino.readline().decode().strip()

    def show_popup(self, text):
        # The message box is shown using .exec_() to block the application until the user closes it
        msg = QMessageBox()
        msg.setWindowTitle("Message Box")
        msg.setText(text)
        x = msg.exec_()

    def closeEvent(self, event):
        # It ensures that if there is an open serial connection, it is properly closed
        if self.arduino is not None and self.arduino.is_open:
            self.arduino.close()


app = QApplication([])
window = Window()
window.show()
app.exec()