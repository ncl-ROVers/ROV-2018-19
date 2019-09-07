from PySide2.QtWidgets import *
from gui.loading import Loading
from gui.home import Home
from gui.tools import Screen
from gui.vision import Vision
from gui.controls import Controls


class Manager(QWidget):

    def __init__(self):
        super(Manager, self).__init__()

        # Initialise the base layout
        self._base = QHBoxLayout()

        # Initialise the list of screens
        self._screens = QStackedWidget()

        # Add the screens
        self._screens.addWidget(Loading())
        self._screens.addWidget(Home())
        self._screens.addWidget(Controls())
        self._screens.addWidget(Vision())

        # Populate the base layout with the screens widget
        self._base.addWidget(self._screens)

        # Set the base layout as the manager's layout
        self.setLayout(self._base)

        # Display the manager
        self.show()

    def switch(self, screen: Screen):
        """
        Function used to switch in between screens.

        :param screen: Screen to switch to
        """

        # Switch the screen
        self._screens.setCurrentIndex(screen.value)

        # Set the window title
        self.setWindowTitle(screen.name)

    def get_current_screen(self):
        """
        Function used to get a :class:`Screen` from the manager.

        :param screen: Enum of the screen to be retrieved
        :return: Retrieved screen
        """

        return self._screens.currentWidget()

    def register_streams(self, streams: list):

        # Remember the reference to the streams
        self.streams = streams