import PySide2.QtCore as QtCore
from PySide2.QtWidgets import *
from os import path


# Declare path to the resources
RES = path.join(path.normpath(path.dirname(__file__)), "res", "loading")


class Loading(QWidget):

    def __init__(self):
        super(Loading, self).__init__()

        # Declare the minimum and the maximum points
        self._MIN = 0
        self._MAX = 100

        # Initialise the progress tracker
        self._progress = 0

        # Initialise the loading bar
        self._bar = QProgressBar()

        # Add styling to the progress bar
        self._bar.setRange(self._MIN, self._MAX)
        self._bar.text()

        # Initialise the text label
        self._label = QLabel()

        # Add styling to the text label
        self._label.setText("Loading ...".format(self._MIN, self._MAX))
        self._label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        # Initialise the outer layout
        layout = QVBoxLayout()

        # Add the widgets
        layout.addWidget(self._bar)
        layout.addWidget(self._label)

        # Align all the items
        layout.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        # Set the loading screen layout
        self.setLayout(layout)

    @property
    def progress(self):
        """
        Getter for the current loading progress.

        :return: Loading progress
        """

        return self._progress

    @progress.setter
    def progress(self, value):
        """
        Setter for the loading progress.

        Throws a :class:`ValueError` if the value is not in the valid range.
        """

        # Check if the value is between valid range
        if self._MIN <= value <= self._MAX:

            # Set the progress
            self._progress = value
            self._bar.setValue(value)

        # Otherwise raise a value error
        else:
            raise ValueError
