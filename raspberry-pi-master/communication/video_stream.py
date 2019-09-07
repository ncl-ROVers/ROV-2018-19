"""
Video Stream
************

Description
===========

This module is used to handle the visual data exchange with the surface.

Functionality
=============

VideoStream
-----------

The :class:`VideoStream` class provides a TCP-based streaming from a single camera. It also provides a simple main
function to create an instance of it and start exchanging the data.

.. warning::

    You should never create an instance of :class:`VideoStream` yourself, and instead execute this module in a separate
    process.

Execution
---------

To start the communication, you should execute the following command::

    python video_stream.py id port

where `id` is the identifier of the video capture, the `port` is the socket's port and `python` is the python's version.

Functions & classes
-------------------

.. note::

    Remember that the code is further described by in-line comments and docstrings.

The following list shortly summarises the functionality of each code component within the :class:`VideoStream` class:

    1. :class:`DataError` is a support class to handle custom exceptions
    2. :func:`__init__` uses the arguments passed in the execution command to build the stream
    3. :func:`_handle_data` receives and sends the data
    4. :func:`_next_frame` fetches the frame from the camera
    5. :func:`_on_surface_disconnected` handles the connection loss with the surface control station
    6. :func:`stream` runs an infinite loop to keep exchanging the data (frames)

Modifications
=============

The only functions that could require modification are :func:`_on_surface_disconnected` and :func:`_handle_data`, as
the module expands. You should also consider modifying the `self._TIMEOUT` value within :func:`__init__`.

Authorship
==========

Kacper Florianski
"""

import socket
from dill import dumps, PicklingError
from socket import timeout
from cv2 import VideoCapture, imencode
from cv2 import error as OpenCvError
from sys import argv


class VideoStream:

    # Custom exception to handle data errors
    class DataError(Exception):
        pass

    def __init__(self, camera_id: int, *, ip="0.0.0.0", port=50010):
        """
        Constructor function used to initialise the stream by setting up the communication and camera-related values.

        .. warning::

            You should avoid changing the ip address parameter and leave it at its default state, to ensure portability
            of the communication code.

        It is recommended that you change the `self._TIMEOUT` to adjust the delay on timeout with surface, as well as
        modify any `self._CAMERA` constants to adjust the resolution of streams.

        :param camera_id: Video Capture's ID
        :param ip: Raspberry Pi's IP address
        :param port: Raspberry Pi's port
        """

        # Save the host and port information
        self._ip = ip
        self._port = port

        # Store the video capture id
        self._camera_id = camera_id

        # Create the OpenCV's camera object
        self._camera = VideoCapture(camera_id)

        # Declare the camera resolution constants for low quality stream
        self._CAMERA_WIDTH = 320
        self._CAMERA_HEIGHT = 240

        # Apply the low resolution
        self._camera.set(3, self._CAMERA_WIDTH)
        self._camera.set(4, self._CAMERA_HEIGHT)

        # Declare the constant for the communication timeout with the surface
        self._TIMEOUT = 3

        # Initialise the socket for IPv4 addresses (hence AF_INET) and TCP (hence SOCK_STREAM)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the given address, inform about errors
        try:
            self._socket.bind((self._ip, self._port))
        except socket.error:
            print("Failed to bind socket to the given address {}:{} ".format(self._ip, self._port))

        # Tell the server to listen to only one connection
        self._socket.listen(1)

        # Initialise the frame-end string to mark when the frame was fully sent
        self._end_payload = bytes("Frame was successfully sent", encoding="ASCII")

    def _handle_data(self):
        """
        Function used to process the frames and send them to surface.

        Any frame-related modifications should be introduced here, preferably encapsulated in another function.
        """

        # Once connected, keep receiving and sending the data, raise exception in case of errors
        try:

            # Fetch the next frame
            frame = self._next_frame()

            # Only handle valid frames
            if frame is not None:

                # Send the frame
                self._client_socket.sendall(dumps(frame))

                # Mark that the frame was sent
                self._client_socket.sendall(self._end_payload)

                # Wait for the acknowledgement
                self._client_socket.recv(128)

        except (ConnectionResetError, ConnectionAbortedError, timeout, PicklingError):
            raise self.DataError

    def _next_frame(self):
        """
        Function used to fetch a frame from the registered camera.

        :return: OpenCV frame object (numpy array)
        """

        # Attempt to take the next frame
        try:
            # Fetch the frame information
            _, frame = self._camera.read()

            # Encode the frame
            _, frame = imencode(".jpg", frame)

            # Return the frame
            return frame

        except OpenCvError:
            return None

    def _on_surface_disconnected(self):
        """
        Function used to clean up any resources when the connection to surface is closed.

        This function should be modified with the expansion of the stream to accommodate any additional resources that
        must be cleaned.
        """

        # Close the socket
        self._client_socket.close()

        # Inform that the connection has been closed
        print("Video stream to {} closed successfully".format(self._client_address))

    def stream(self):
        """
        Function used to run a continuous connection with the surface.

        Runs an infinite loop that performs re-connection to the connected client as well as exchanges data with it, via
        non-blocking send and receive functions. The data exchanged is pickled using :mod:`dill`.
        """

        # Never stop the server once it was started
        while True:

            # Inform that the server is ready to receive a connection
            print("Video stream at {} is waiting for a client...".format(self._socket.getsockname()))

            # Wait for a connection (accept function blocks the program until a client connects to the server)
            self._client_socket, self._client_address = self._socket.accept()

            # Set a non-blocking connection to timeout on receive/send
            self._client_socket.setblocking(False)

            # Set the timeout
            self._client_socket.settimeout(self._TIMEOUT)

            # Inform that a client has successfully connected
            print("Client with address {} connected to video stream at {}".format(self._client_address, self._socket.getsockname()))

            while True:

                # Attempt to handle the data, break in case of errors
                try:
                    self._handle_data()
                except self.DataError:
                    break

            # Clean up
            self._on_surface_disconnected()


if __name__ == "__main__":

    # Build a new video stream and start streaming
    VideoStream(int(argv[1]), port=int(argv[2])).stream()
