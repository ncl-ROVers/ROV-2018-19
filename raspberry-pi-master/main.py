"""
Middle-level software
*********************

Description
===========

This module is used to run the Raspberry Pi, and is executed on boot.

Functionality
=============

Execution
---------

To start the code, you should execute the following command::

    python main.py

where `python` is the python's version.

Functions & classes
-------------------

.. note::

    Remember that the code is further described by in-line comments and docstrings.

The following list shortly summarises the functionality of each code component within the :class:`VideoStream` class:

    1. :func:`find_camera_ids` checks which video captures are valid (which ids are the cameras under)

Modifications
=============

You should modify this module as much as needed.

Authorship
==========

Kacper Florianski
"""

from communication.server import Server
from sys import platform
from subprocess import Popen
from os import path
from cv2 import VideoCapture

# Declare path to this file
MAIN_PATH = path.normpath(path.dirname(__file__))

# Declare the number of camera captures to test
CAMERA_CAPTURES_COUNT = 8


def find_camera_ids():
    """
    Function used to determine which video capture ids are associated with cameras.

    :return: Set of valid ids
    """

    # Initialise the ids set
    camera_ids = set()

    # Create a new video capture instance
    temp = VideoCapture()

    # Crawl over the possible ids
    for camera_id in range(CAMERA_CAPTURES_COUNT):

        # Assign a new id to the video capture
        temp.open(camera_id)

        # Fetch the frame
        _, frame = temp.read()

        # If the frame is valid
        if frame is not None:

            # Add the id to the set
            camera_ids.add(camera_id)

        # Release the current camera id
        temp.release()

    # Remove the video capture instance
    del temp

    # Return the final result
    return camera_ids


if __name__ == "__main__":

    # Inform that the initialisation phase has started
    print("Loading...")

    # Initialise the server
    server = Server(port=50000)

    # Initialise the camera capture identifiers
    camera_ids = find_camera_ids()

    # Initialise the port iterator
    port = 50010

    # Build the initial command by fetching the correct python version
    if "win" in platform.lower():
        command = ["python"]
    else:
        command = ["python3.6"]

    # Add the video stream argument to the command
    command.append(path.join(MAIN_PATH, "communication", "video_stream.py"))

    # Inform that the execution phase has started
    print("Starting tasks...")

    # Start the server
    server.run()

    # Start the video streams
    for camera_id in camera_ids:

        # Run the stream
        Popen(command + [str(camera_id), str(port)])

        # Increase the operator
        port += 1

    # Inform that the code has fully executed
    print("Tasks initialised and started successfully")
