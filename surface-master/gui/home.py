import PySide2.QtCore as QtCore
from PySide2.QtWidgets import *
from gui.tools import Tabs, Camera, Sensor


class Home(QWidget):

    def __init__(self):
        super(Home, self).__init__()

        # Initialise the outer layout
        layout = QVBoxLayout()

        # Initialise the inner top layout
        top_layout = QHBoxLayout()

        # Align the top items
        top_layout.setAlignment(QtCore.Qt.AlignTop)

        # Build the top layout
        top_layout.addWidget(Tabs())
        top_layout.addWidget(Camera(0))
        top_layout.addWidget(Camera(1))
        top_layout.addWidget(Camera(2))

        # Create a wrapper for the top layout
        top_wrapper = QWidget()
        top_wrapper.setLayout(top_layout)
        top_wrapper.setFixedHeight(240)

        # Initialise the middle-layer layout
        middle_layout = QHBoxLayout()

        # Align the middle items
        middle_layout.setAlignment(QtCore.Qt.AlignHCenter)

        # Initialise the sensor's list
        self._sensors = list()

        # Initialise the sensors
        self._sensors.append(Sensor("Sen_IMU_X"))
        self._sensors.append(Sensor("Sen_IMU_Y"))
        self._sensors.append(Sensor("Sen_IMU_Z"))
        self._sensors.append(Sensor("Sen_IMU_Temp"))
        self._sensors.append(Sensor("Sen_Temp"))
        self._sensors.append(Sensor("Sen_PH"))
        self._sensors.append(Sensor("Sen_Sonar_Dist"))
        self._sensors.append(Sensor("Sen_Sonar_Conf"))

        # Iterate over the sensors
        for sensor in self._sensors:

            # Add the sensor to the widget
            middle_layout.addWidget(sensor)

        # Create a wrapper for the middle layout
        middle_wrapper = QWidget()
        middle_wrapper.setLayout(middle_layout)

        # Build the final layout
        layout.addWidget(top_wrapper)
        layout.addWidget(middle_wrapper)

        # Set the loading screen layout
        self.setLayout(layout)

        # Initialise the timer
        self._timer = QtCore.QTimer()

        # Connect the timeout with reading the sensor values
        self._timer.timeout.connect(self._read_sensors)

        # Start the timer
        self._timer.start()

    def _read_sensors(self):

        # Iterate over the sensors
        for sensor in self._sensors:

            # Update the sensor text
            sensor.update_data()
