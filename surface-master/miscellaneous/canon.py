"""
Canon calculations
******************

Description
===========

This module provides calculations required to complete the canon measurements task.

Functionality
=============

Execution
---------

You should simply import the module::

    import canon

To verify the code with the MATE examples, you should run this module::

    python canon.py

Functions & classes
-------------------

.. note::

    Remember that the code is further described by in-line comments and docstrings.

The following list shortly summarises the functionality of each code component within this module:

    1. :class:`Foundry` enumerates possible foundries
    2. :func:`get_canon_volume` calculates the volume of the canon
    3. :func:`get_canon_lift_force` calculates the force needed to lift the canon
    4. :func:`get_canon_weight` returns the weight of the canon in kilograms
    5. :func:`is_liftable` checks if the ROV is capable of lifting the canon

Modifications
=============

This module is specific to MATE 2019 competition and should not be modified.

Authorship
==========

Margarita Kourounioti

Modified by
-----------

Kacper Florianski
"""

from math import pi
from enum import Enum

# Declare the standard gravitational acceleration
GRAVITY = 9.80665

# Declare the metal densities
IRON = 7870
BRONZE = 8030

# Declare the lift capability of the ROV
ROV_LIFT_CAPABILITY = 139.302


class Foundry(Enum):
    """
    Enumeration of allowed foundries.
    """

    AF = "Augusta Foundry"
    BF = "Bellona Foundry"
    FPF = "Fort Pitt Foundry"
    TF = "Tredegar Foundry"


def get_canon_volume(radius_1: float, radius_2: float, radius_3: float, length: float) -> float:
    """
    Function used to calculate the volume of the canon.

    The inputs should be in centimeters.

    :param radius_1: R1 radius of the canon
    :param radius_2: R2 radius of the canon
    :param radius_3: R3 radius of the canon
    :param length: Length of the canon
    :return: Volume of the canon (in cm^3)
    """

    # Calculate the volume of the inner cylinder
    cylinder_volume = pi * (radius_2**2) * length

    # Calculate the volume of the cone
    cone_volume = (1/3)*pi*length*(radius_1**2+radius_1*radius_3+radius_3**2)

    # Return the volume of the canon
    return cone_volume - cylinder_volume


def get_canon_lift_force(foundry: Foundry, canon_volume: float) -> float:
    """
    Function used to calculate the force needed to lift the canon.

    :param foundry: Canon foundry
    :param canon_volume: Volume of the canon
    :return: Force required to lift the canon (in Newtons)
    """

    # Check if the canon is made of iron or bronze
    if foundry == Foundry.BF or foundry == Foundry.TF or foundry == Foundry.FPF:
        density = IRON
    else:
        density = BRONZE

    # Return the lift force
    return density * canon_volume * GRAVITY * (10 ** -6)


def get_canon_weight(lift_force: float) -> float:
    """
    Function used to express the canon weight in kilograms.

    :param lift_force: Force needed to lift the canon
    :return: Weight in kilograms
    """

    # Return the weight (in kilograms)
    return lift_force / GRAVITY


def is_liftable(lift_force: float) -> bool:
    """
    Function used to check if the ROV has enough lift capability to carry the canon.

    :param lift_force: Force needed to lift the canon
    :return: True if the ROV is able to lift the canon, False otherwise
    """

    # Return the result of the comparison
    return True if ROV_LIFT_CAPABILITY > lift_force else False


if __name__ == '__main__':

    # Declare the example values
    R1, R2, R3, L = 5.3, 2.8, 7.7, 46

    # Get the real values
    # R1, R2, R3, L = float(input("R1: ")), float(input("R2: ")), float(input("R3: ")), float(input("L: "))

    # Calculate the example results
    V = get_canon_volume(R1, R2, R3, L)
    F = get_canon_lift_force(Foundry.BF, V)
    W = get_canon_weight(F)
    LF = is_liftable(F)

    # Print the results
    print("Volume: {}, Lift force: {}, Weight: {}, Lift ability: {}".format(V, F, W, LF))
