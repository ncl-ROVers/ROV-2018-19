"""
High-level software
*******************

Description
===========

This module is used to run the surface control station.

Functionality
=============

Execution
---------

To start the code, you should execute the following command::

    python main.py

where `python` is the python's version.

Modifications
=============

You should modify this module as much as needed.

.. warning::

    Remember to initialise all components first, and start them later (so that you can have a loading screen).

Authorship
==========

Kacper Florianski
"""

import communication.data_manager as dm
from communication.connection import Connection
from communication.video_stream import VideoStream
from gui.manager import Manager
from gui.tools import Screen, CAMERAS_COUNT
from PySide2.QtWidgets import QApplication
from os import path
from subprocess import Popen

# Declare path to this file
MAIN_PATH = path.normpath(path.dirname(__file__))


if __name__ == "__main__":

    # Initialise the ip
    ip = 'localhost'  # local testing
    ip = "169.254.246.235"  # ROV pi
    # ip = "169.254.231.182"  # Kacper's personal pi

    # Inform that the initialisation phase has started
    print("Initialising...")

    # Create a new QT application instance
    app = QApplication()

    # Create a new Manager instance
    manager = Manager()

    # Get the loading screen
    loading = manager.get_current_screen()

    # Clear the cache on start
    dm.clear()

    # Set some default values for the sonar
    dm.set_data(Sen_Sonar_Start=5, Sen_Sonar_Len=30)

    # Update the progress
    loading.progress = 10

    # Initialise and start the server connection
    connection = Connection(ip=ip, port=50000)

    # Initialise the port iterator
    port = 50010

    # Initialise the video streams
    streams = [VideoStream(ip=ip, port=p) for p in range(port, port + CAMERAS_COUNT)]

    # Update the progress
    loading.progress = 30

    # Inform that the connection execution phase has started
    print("Starting connections...")

    # Start the main server connection
    connection.connect()

    # Start the video streams
    for stream in streams:
        stream.stream()

    # Register the streams in the GUI
    manager.register_streams(streams)

    # Update the progress
    loading.progress = 60

    # Inform that the components phase has started
    print("Preparing the controller...")

    # Build the controller's command and run it
    Popen("python " + path.join(MAIN_PATH, "control", "controller.py"))

    # Update the progress
    loading.progress = 80

    # Inform that the GUI phase has started
    print("Starting the interactive GUI")

    # Switch the screen when finished loading other components
    manager.switch(Screen.Home)

    # Start the application
    app.exec_()
