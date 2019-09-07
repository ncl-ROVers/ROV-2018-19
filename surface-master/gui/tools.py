import qimage2ndarray
from PySide2.QtWidgets import *
from PySide2.QtCore import QTimer, QSize
from PySide2.QtGui import QPixmap
from enum import Enum
from cv2 import cvtColor, COLOR_BGR2RGB
from vision.tools import count_shapes, Colour
import communication.data_manager as dm

# Declare the number of cameras
CAMERAS_COUNT = 3

# Declare constants for the video streams
SMALL_VIDEO_WIDTH = 320
SMALL_VIDEO_HEIGHT = 240

# Declare constants for the dimensions of each component
TABS_HEIGHT = 300


def get_manager(widget):
    """
    Function used to recursively get the :class:`Manager` managing the screens.

    :return: Manager instance
    """

    # Get current parent
    parent = widget.parent()

    # Keep looking for the parent
    while parent is not None:

        # Check if the current parent is a manager
        if "Manager" in repr(parent):
            return parent

        # Otherwise keep looking for the manager instance
        else:
            parent = parent.parent()

    # Return none if manager wasn't found
    return None


class Screen(Enum):
    """
    Enumeration of the available screens.
    """

    Loading = 0
    Home = 1
    Controls = 2
    Vision = 3


class TabButton(QPushButton):
    """
    Class used to extend the QPushButton functionality to create a custom tab button.

    :param text: Text to be displayed on the button
    :param screen: Screen to switch to
    """

    def __init__(self, text: str, screen: Screen):
        super(TabButton, self).__init__()

        # Store the text and the screen references
        self._text = text
        self._screen = screen

        # Set the visual representation
        self.setText(self._text)

        # Register the on click functionality
        self.clicked.connect(self._on_click)

    def _on_click(self):

        # Fetch the manager
        manager = get_manager(self)

        # Switch the screen
        manager.switch(self._screen)


class Tabs(QWidget):
    """
    Class used to build the navigation tabs.
    """

    def __init__(self):
        super(Tabs, self).__init__()

        # Build the outer layout
        layout = QHBoxLayout()

        # Build the buttons
        home = TabButton("Home", Screen.Home)
        controls = TabButton("Controls", Screen.Controls)
        vision = TabButton("Vision", Screen.Vision)

        # Add the buttons to the layout
        layout.addWidget(home)
        layout.addWidget(controls)
        layout.addWidget(vision)

        # Set the layout
        self.setLayout(layout)


class Camera(QLabel):

    def __init__(self, stream_id: int):
        super(Camera, self).__init__()

        # Set the video size
        self.setFixedSize(QSize(320, 240))

        # Store the id reference
        self._id = stream_id

        # Initialise the timer
        self._timer = QTimer()

        # Connect the timeout with the new frame display
        self._timer.timeout.connect(self._next_frame)

        # Start the timer
        self._timer.start()

    def _next_frame(self):

        # Fetch the frame
        frame = get_manager(self).streams[self._id].frame

        # Check if a valid frame was caught
        if frame is not None:

            # Convert the frame colour
            frame = cvtColor(frame, COLOR_BGR2RGB)

            # Create a new image frame
            frame = qimage2ndarray.array2qimage(frame)

            # Set the frame to visible
            self.setPixmap(QPixmap.fromImage(frame))

    def switch_stream(self, stream_id: int):

        # Override the stream id information
        self._id = stream_id


class ShapeDetectionCamera(Camera):

    def _next_frame(self):

        # Fetch the frame
        frame = get_manager(self).streams[self._id].frame

        # Check if a valid frame was caught
        if frame is not None:

            # Update the frame with the shapes detection vision algorithm
            shapes, frame = count_shapes(frame, Colour.BLACK)

            # Convert the frame colour
            frame = cvtColor(frame, COLOR_BGR2RGB)

            # Create a new image frame
            frame = qimage2ndarray.array2qimage(frame)

            # Set the frame to visible
            self.setPixmap(QPixmap.fromImage(frame))


class Sensor(QLabel):

    def __init__(self, key: str):
        super(Sensor, self).__init__()

        # Store the key reference
        self._key = key

        # Set the initial text
        self.setText("{}: ...".format(self._key))

    def update_data(self):

        # Only handle valid keys
        try:

            # Fetch the value from the data manager and update the text
            self.setText("{}: {}".format(self._key, dm.get_data(self._key)[self._key]))

        except KeyError:
            pass
