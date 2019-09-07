import PySide2.QtCore as QtCore
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import *
from gui.tools import Tabs, Camera
from os import path

# Declare path to the resources
RES = path.join(path.normpath(path.dirname(__file__)), "res", "controls")


class Controls(QWidget):

    def __init__(self):
        super(Controls, self).__init__()

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

        # Initialise the controller image
        controller = QLabel()

        # Build the final layout
        layout.addWidget(top_wrapper)
        layout.addWidget(controller)

        # Build the image TODO: Fix
        controller.setPixmap(QPixmap(path.join(RES, "joystick.png")).scaled(controller.size(), QtCore.Qt.KeepAspectRatioByExpanding))

        # Align the image
        controller.setAlignment(QtCore.Qt.AlignHCenter)

        # Set the loading screen layout
        self.setLayout(layout)
