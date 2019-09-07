"""
Data Manager
************

Description
===========

Data Manager is used to maintain different states of data across the system.

Functionality
=============

DataManager
-----------

The :class:`DataManager` class provides data dispatching functionality to relay information from the surface control
station to the Arduino-s and vice-versa.

Execution
---------

You should simply create an instance of the :class:`DataManager`::

    dm = DataManager()


Functions & classes
-------------------

.. note::

    Remember that the code is further described by in-line comments and docstrings.

The following list shortly summarises the functionality of each code component within the :class:`DataManager` class:

    1. :func:`__init__` builds the manager
    2. :func:`get` accesses the data
    3. :func:`set` modifies the data

Modifications
=============

It is recommended that you adjust the module-level constants:

    1. Unique ids to change the surface or Arduino identifiers (`SURFACE`, `ARDUINO_T` etc.)
    2. `DEFAULT` constant to specify which values are default for each key
    3. `RAMP_RATE` to modify how quickly should the values be changing

Additionally, you should modify the :func:`__init__` function, especially the `self._transmission_keys` mapping.

Authorship
==========

Kacper Florianski
"""

# Declare constants to easily access the resources (ids)
SURFACE = 0
ARDUINO_T = "Ard_T"
ARDUINO_M = "Ard_M"
ARDUINO_I = "Ard_I"

# Declare some default values
THRUSTER_IDLE = 1500

# Declare default key, value pairs to set the values on connection loss with surface
DEFAULT = {
    "Thr_FP": THRUSTER_IDLE,
    "Thr_FS": THRUSTER_IDLE,
    "Thr_AP": THRUSTER_IDLE,
    "Thr_AS": THRUSTER_IDLE,
    "Thr_TFP": THRUSTER_IDLE,
    "Thr_TFS": THRUSTER_IDLE,
    "Thr_TAP": THRUSTER_IDLE,
    "Thr_TAS": THRUSTER_IDLE,
    "Thr_M": THRUSTER_IDLE,
    "Mot_R": THRUSTER_IDLE,
    "Mot_G": THRUSTER_IDLE,
    "Mot_F": THRUSTER_IDLE,
}

# Declare constant for slowly changing up all values
RAMP_RATE = 2


class DataManager:

    def __init__(self):
        """
        Constructor function used to initialise the data manager.

        You should adjust the corresponding cache creation and mapping elements depending on the number and
        functionality of the Arduino-s.

        The `self._transmission_keys` variable is especially important, as each key within specifies which values should
        be sent to which device. For example, by adding "status_T" to `SURFACE` key, the value under that key
        (and the key) will be sent to surface (wherever it comes from, `ARDUINO_T` or `ARDUINO_M` - doesn't matter).
        """

        # Create the cache
        self._surface = dict()
        self._arduino_T = dict()
        self._arduino_M = dict()
        self._arduino_I = dict()

        # Create a dictionary mapping each index to corresponding location
        self._data = {
            SURFACE: self._surface,
            ARDUINO_T: self._arduino_T,
            ARDUINO_M: self._arduino_M,
            ARDUINO_I: self._arduino_I
        }

        # Create a dictionary mapping each index to a set of networking keys
        self._transmission_keys = {
            SURFACE: {"status_T", "status_M", "status_I", "Sen_IMU_X", "Sen_IMU_Y", "Sen_IMU_Z", "Sen_IMU_Temp",
                      "Sen_IMU_AccX", "Sen_IMU_AccY", "Sen_IMU_AccZ", "Sen_Dep_Pres", "Sen_Dep_Temp", "Sen_Dep_Dep",
                      "Sen_Temp", "Sen_PH", "Sen_Sonar_Dist", "Sen_Sonar_Conf", "Sen_Metal"},
            ARDUINO_T: {"Thr_FP", "Thr_FS", "Thr_AP", "Thr_AS", "Thr_TFP", "Thr_TFS", "Thr_TAP", "Thr_TAS",
                        "Mot_R", "Mot_G", "Mot_F"},
            ARDUINO_M: {"Thr_M"},
            ARDUINO_I: {"Sen_Sonar_Start", "Sen_Sonar_Len"}
        }

        # Create a key to ID lookup for performance reasons
        self._keys_lookup = {v: k for k, values in self._transmission_keys.items() if k != SURFACE for v in values}

    def get(self, index, *args) -> dict:
        """
        Function used to access the cached values.

        Example of usage::

            partial_data = get(SURFACE, "Mot_G")  # returns a dictionary with a single entry
            full_data = get(SURFACE)  # returns a dictionary with several entries

        :param index: Device index to specify which device to retrieve the data from
        :param args: Keys to retrieve (returns all keys if no args are passed)
        :param transmit: Boolean to specify if only the transmission data should be retrieved
        :return: Dictionary of the data
        """

        # Return selected data or full dictionary if no args passed
        return {key: self._data[index][key] for key in args if key in self._transmission_keys[index]} if args else \
            {key: self._data[index][key] for key in self._transmission_keys[index] if key in self._data[index]}

    def set(self, index, default=False, **kwargs):
        """
        Function used to modify the cache.

        Example of usage::

            set(SURFACE, Mot_G=1500)  # Does self._surface["Mot_G"] = 1500

        .. warning::

            You must provide all keys in `self._transmission_keys`.

        :param index: Device index to specify which device's data should be modified
        :param default: If default is set to true then the ROV sets all the values according to the default dictionary.
        :param kwargs: Key, value pairs of data to modify.
        """

        # If the default values are to be set
        if default:

            # Iterate over the default key, value pairs
            for key, value in DEFAULT.items():

                # Set the data dictionary to the default values
                self._data[self._keys_lookup[key]][key] = value

        # If it is standard communication
        else:

            # Iterate over all kwargs' key, value pairs
            for key, value in kwargs.items():

                # If index passed is (from) surface, update the corresponding Arduino transmission data
                if index == SURFACE:

                    # Check if the key wasn't yet registered
                    if key not in self._data[self._keys_lookup[key]]:
                        self._data[self._keys_lookup[key]][key] = value

                    else:
                        # Calculate the difference between passed and registered values
                        difference = self._data[self._keys_lookup[key]][key] - value

                        # Ramp up/down to avoid big current changes
                        if difference > 0:
                            self._data[self._keys_lookup[key]][key] -= RAMP_RATE
                        elif difference < 0:
                            self._data[self._keys_lookup[key]][key] += RAMP_RATE

                # If index passed is (from) an Arduino, update the corresponding surface transmission data
                else:

                    # Update the corresponding surface value
                    self._data[SURFACE][key] = value
