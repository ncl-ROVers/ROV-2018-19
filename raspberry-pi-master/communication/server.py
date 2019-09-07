"""
Server
******

Description
===========

This module is used to handle the information exchange with high and low-level layers of the system. It uses threading
and a :class:`DataManager` to handle the data flow between connected components.

Functionality
=============

Server
------

The :class:`Server` class provides a TCP-based data exchange with the surface, as well as sets up the communication
means with the Arduino-s.

Arduino
-------

The :class:`Arduino` class is responsible for information flow between the Raspberry Pi and an Arduino, over serial.

Execution
---------

To start the communication, you should create an instance of :class:`Server` and call :func:`run`, for example::

    server = Server(port=50000)
    server.run()

Functions & classes
-------------------

.. note::

    Remember that the code is further described by in-line comments and docstrings.

The following list shortly summarises the functionality of each code component within the :class:`Server` class:

    1. :class:`DataError` is a support class to handle custom exceptions
    2. :func:`__init__` uses the arguments passed in the execution command to build the server
    3. :func:`_init_high_level` initialises the communication with the surface
    4. :func:`_init_low_level` initialises the communication with the low-level components
    5. :func:`_listen_high_level` runs an infinite loop to keep exchanging the data with the surface
    6. :func:`_listen_low_level` calls the :class:`Arduino` connection functions
    7. :func:`_handle_data` receives and sends the data to the surface
    8. :func:`_on_surface_disconnected` handles the connection loss with the surface control station
    9. :func:`run` starts the high and low level communication

The following list shortly summarises the functionality of each code component within the :class:`Arduino` class:

    1. :class:`DataError` is a support class to handle custom exceptions
    2. :func:`__init__` uses the arguments passed in the execution command to build the serial connection
    3. :func:`_handle_data` receives and sends the data to the connected arduino
    4. :func:`_listen` runs an infinite loop to keep exchanging the data with the connected arduino
    5. :func:`connect` starts the communication

Modifications
=============

The only functions that could require modification are :func:`_on_surface_disconnected` and :func:`_handle_data` in both
:class:`Server` and :class:`Arduino`, as the module expands. You should also consider modifying the `self._TIMEOUT`
value within :func:`_init_high_level`, as well tune any constants inside :class:`Arduino`'s :func:`__init__`.

Additionally, if the general setup of Arduino-s changes (for example more get added), you will have to adjust the
:class:`Server`'s :func:`__init__` (`tty` ports) as well as :func:`_init_low_level` (`arduino_ids`).

Authorship
==========

Kacper Florianski
"""

import socket
from communication.data_manager import *
from serial import Serial, SerialException
from json import dumps, loads, JSONDecodeError
from time import sleep
from threading import Thread


class Server:

    # Custom exception to handle data errors
    class DataError(Exception):
        pass

    def __init__(self, *, ip='0.0.0.0', port=50000):
        """
        Constructor function used to initialise the communication by calling the corresponding init methods.

        .. warning::

            You should avoid changing the ip address parameter and leave it at its default state, to ensure portability
            of the communication code.

        Remember to adjust the `ports` list if the ports change.

        :param ip: Raspberry Pi's IP address
        :param port: Raspberry Pi's port
        """

        # Initialise the data manager
        self._dm = DataManager()

        # Initialise communication with surface
        self._init_high_level(ip=ip, port=port)

        # Initialise communication with Arduino-s
        self._init_low_level(ports=["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2"])

    def _init_high_level(self, ip: str, port: int):
        """
        Function used to initialise communication with the surface.

        It is recommended that you change the `self._TIMEOUT` to adjust the delay on timeout with surface.

        :param ip: Raspberry Pi's IP
        :param port: Raspberry Pi's port
        """

        # Initialise the process to handle parallel communication
        self._process = Thread(target=self._listen_high_level)

        # Save the host and port information
        self._ip = ip
        self._port = port

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

    def _init_low_level(self, ports: list):
        """
        Function used to initialise communication with the Arduino-s.

        Remember to adjust the `arduino_ids` variable if the IDS change.

        :param ports: List of Arduino ports
        """

        # Declare a set of clients to remember
        self._clients = set()

        # Declare a list of ports to remember
        self._ports = ports

        # Initialise a list of ids to assign the Arduino-s to each port
        arduino_ids = [ARDUINO_I, ARDUINO_T, ARDUINO_M]

        # Iterate over each port and create corresponding clients
        for i in range(len(self._ports)):

            # Create an instance of the Arduino and store it
            self._clients.add(Arduino(self._dm, self._ports[i], arduino_ids[i]))

    def _listen_high_level(self):
        """
        Function used to run a continuous connection with the surface.

        Runs an infinite loop that performs re-connection to the connected client as well as exchanges data with it, via
        non-blocking send and receive functions. The data exchanged is JSON-encoded.
        """

        # Never stop the server once it was started
        while True:

            # Inform that the server is ready to receive a connection
            print("{} is waiting for a client...".format(self._socket.getsockname()))

            # Wait for a connection (accept function blocks the program until a client connects to the server)
            self._client_socket, self._client_address = self._socket.accept()

            # Set a non-blocking connection to timeout on receive/send
            self._client_socket.setblocking(False)

            # Set the timeout
            self._client_socket.settimeout(self._TIMEOUT)

            # Inform that a client has successfully connected
            print("Client with address {} connected".format(self._client_address))

            while True:

                # Attempt to handle the data, break in case of errors
                try:
                    self._handle_data()
                except self.DataError:
                    break

            # Run clean up / connection lost info etc.
            self._on_surface_disconnected()

    def _listen_low_level(self):
        """
        Function used to run a continuous connection with the Arduino-s.

        The :func:`Arduino.connect` function has a similar functionality to the :func:`_listen_high_level` function,
        and is further described in ints corresponding documentation.
        """

        # Iterate over assigned clients
        for client in self._clients:

            # Connect to the Arduino
            client.connect()

    def _on_surface_disconnected(self):
        """
        Function used to clean up any resources when the connection to surface is closed.

        This function should be modified with the expansion of the stream to accommodate any additional resources that
        must be cleaned.
        """

        # Close the socket
        self._client_socket.close()

        # Inform that the connection has been closed
        print("Connection from {} address closed successfully".format(self._client_address))

        # Set the keys to their default values, BEWARE: might add keys that haven't yet been received from surface
        self._dm.set(SURFACE, default=True)

    def _handle_data(self):
        """
        Function used to receive and send the processed data to the surface.

        Any data-related modifications should be introduced here, preferably encapsulated in another function.
        """

        # Once connected, keep receiving and sending the data, raise exception in case of errors
        try:
            data = self._client_socket.recv(4096)

            # If 0-byte was received, close the connection
            if not data:
                raise self.DataError

        except (ConnectionResetError, ConnectionAbortedError, socket.timeout):
            raise self.DataError

        # Convert bytes to string, remove the white spaces, ignore any invalid data
        try:
            data = data.decode("utf-8").strip()
        except UnicodeDecodeError:
            data = None

        # Handle valid data
        if data:

            # Attempt to decode from JSON, inform about invalid data received
            try:
                self._dm.set(SURFACE, **loads(data))
            except JSONDecodeError:
                print("Received invalid data: {}".format(data))

        # Send the current state of the data manager, break in case of errors
        try:
            self._client_socket.sendall(bytes(dumps(self._dm.get(SURFACE)), encoding="utf-8"))

        except (ConnectionResetError, ConnectionAbortedError, socket.timeout):
            raise self.DataError

    def run(self):
        """
        Function used to run all communication.
        """

        # Start the communication with surface's process
        self._process.start()

        # Open the communication with lower-levels with the server's process as the parent process
        self._listen_low_level()


class Arduino:

    # Custom exception to handle data errors
    class DataError(Exception):
        pass

    def __init__(self, dm: DataManager, port: str, arduino_id):
        """
        Constructor function used to initialise the communication with an Arduino.

        You should modify:

            1. `self._WRITE_TIMEOUT` constant to specify the timeout value (seconds) for sending to an Arduino.
            2. `self._READ_TIMEOUT` constant to specify the timeout value (seconds) for receiving from an Arduino.
            3. `self._RECONNECT_DELAY` constant to specify the delay value (seconds) on connection loss.

        :param dm: Shared between threads :class:`DataManager` instance
        :param port: Raspberry Pi's tty port to which the Arduino is connected to
        :param arduino_id: Unique identifier of the Arduino (specified in :mod:`data_manager`)
        """

        # Store the data manager reference
        self._dm = dm

        # Store the port information
        self._port = port

        # Store the id information
        self._id = arduino_id

        # Initialise the serial information
        self._serial = Serial(baudrate=115200)
        self._serial.port = self._port

        # Initialise the timeout constants
        self._WRITE_TIMEOUT = 1
        self._READ_TIMEOUT = 1

        # Set the read and write timeouts
        self._serial.write_timeout = self._WRITE_TIMEOUT
        self._serial.timeout = self._READ_TIMEOUT

        # Initialise the reconnection delay constant to offload some computing power
        self._RECONNECT_DELAY = 1

        # Initialise the thread
        self._thread = Thread(target=self._listen)

    def _handle_data(self):
        """
        Function used to receive and send the processed data to an Arduino.

        Any data-related modifications should be introduced here, preferably encapsulated in another function.
        """

        # Send current state of the data
        self._serial.write(bytes(dumps(self._dm.get(self._id)) + "\n", encoding='utf-8'))

        # Read until the specified character is found ("\n" by default)
        data = self._serial.read_until()

        # Convert bytes to string, remove white spaces, ignore invalid data
        try:
            data = data.decode("utf-8").strip()
        except UnicodeDecodeError:
            data = None

        # Handle valid data
        if data:

            try:
                # Attempt to decode the JSON data
                data = loads(data)

                # Only handle dictionaries populated with values
                if data:

                    # Override the ID
                    self._id = data["deviceID"]

                    # Update the Arduino data (and the surface data)
                    self._dm.set(self._id, **data)

            except JSONDecodeError:
                print("Received invalid data: {}".format(data))
                raise self.DataError
            except KeyError:
                print("Received valid data with invalid ID: {}".format(data))
                raise self.DataError

    def _listen(self):
        """
        Function used to run a continuous connection with an Arduino.

        Runs an infinite loop that performs re-connection to the connected client as well as exchanges data with it, via
        non-blocking write and read_until functions. The data exchanged is JSON-encoded.
        """

        # Run an infinite loop to never close the connection
        while True:

            # Inform about a connection attempt
            print("Connecting to port {}...".format(self._port))

            # Keep exchanging the data or re-connecting
            while True:

                # If the connection is closed
                if not self._serial.is_open:

                    try:
                        # Attempt to open a serial connection
                        self._serial.open()

                        # Inform about a successfully established connection
                        print("Successfully connected to port {}".format(self._port))

                    except SerialException:
                        sleep(self._RECONNECT_DELAY)
                        continue

                # Attempt to handle the data, break in case of errors
                try:
                    self._handle_data()
                except self.DataError:
                    pass
                except SerialException as e:
                    print("Connection to port {} lost, exception raised: \"{}\"".format(self._port, str(e)))
                    self._serial.close()
                    break

    def connect(self):
        """
        Function used to run the communication with an Arduino.
        """

        # Start the connection
        self._thread.start()
