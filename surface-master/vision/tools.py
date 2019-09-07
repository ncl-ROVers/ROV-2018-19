"""
Vision tools
************

Description
===========

This module provides computer vision tools to solve vision-related tasks.

Functionality
=============

Execution
---------

You should simply import the module and call the functions::

    from vision import tools as vt
    shapes, shapes_frame = vt.count_shapes(frame, vt.Colour.BLACK)

where `frame` is the frame to count the shapes from.

Functions & classes
-------------------

.. note::

    Remember that the code is further described by in-line comments and docstrings.

The following list shortly summarises the functionality of each code component within this module:

    1. :class:`Colour` enumerates possible colours
    2. :class:`Shape` enumerates possible colours
    3. :func:`extract_contours` extracts contours from a frame
    4. :func:`filter_by_colour` filters a frame by discarding each object with not-matching colour
    5. :func:`detect_shape` detects a shape based on a contour
    6. :func:`count_shapes` counts and draws the shapes
    7. :func:`extract_dimensions` extracts width and height of an object
    8. :func:`split_frame` splits the frame into 9 sub-frames
    9. :func:`find_centroids` finds and draws centres of the middle row and middle column

Modifications
=============

It is recommended that you adjust the constants as follows:

    1. HSV ranges to adjust the colour recognition
    2. Contour constants to adjust their detection and visual display
    3. Text constants to adjust its visual display
    4. Point constants to adjust the centroid-related visuals

You should also modify/expand the functions to enhance their behaviour.

Authorship
==========

Kacper Florianski
"""

import cv2
import numpy as np
from enum import Enum
from imutils.perspective import order_points
from scipy.spatial.distance import euclidean

# --= Define HSV ranges =--

# Define constants for the red hsv ranges
RED_MIN_LOW = np.array([0, 80, 80], np.uint8)
RED_MAX_LOW = np.array([4, 255, 255], np.uint8)
RED_MIN_HIGH = np.array([174, 80, 80], np.uint8)
RED_MAX_HIGH = np.array([180, 255, 255], np.uint8)

# Define constants for the blue hsv ranges
BLUE_MIN = np.array([90, 120, 120], np.uint8)
BLUE_MAX = np.array([120, 255, 255], np.uint8)

# Define constants for the black hsv ranges
BLACK_MIN = np.array([0, 0, 0], np.uint8)
BLACK_MAX = np.array([180, 255, 75], np.uint8)

# -== Define contour-related constants =--

# The smaller the value the smaller the shapes that are rated as valid (too small value will result in a lot of noise)
CONTOUR_SIZE_BOUND = 1/500

# Used in polynomial approximation, not recommended to change
CONTOUR_EPSILON_FRACTION = 0.04

# Used in detecting whether a shape is a square
CONTOUR_RATIO_TOLERANCE = 0.15

# Thickness of the contour line
CONTOUR_THICKNESS = 2

# Colour of the contour line (BGR)
CONTOUR_COLOUR = (0, 0, 255)

# -== Define text-related constants =--

# Text font
TEXT_FONT = cv2.FONT_HERSHEY_SIMPLEX

# Text size
TEXT_SCALE = 0.5

# TExt thickness
TEXT_THICKNESS = 1

# Text colour (BGR)
TEXT_COLOUR = (255, 255, 255)

# -== Define point-related constants =--

# Colours of the points (BGR)
POINT_COLOUR_A = (0, 255, 0)
POINT_COLOUR_B = (255, 0, 0)

# Radius of the points
POINT_RADIUS_SMALL = 5
POINT_RADIUS_BIG = 10


class Colour(Enum):
    """
    Enumeration of allowed colours.
    """

    RED = "Red"
    BLUE = "Blue"
    BLACK = "Black"


class Shape(Enum):
    """
    Enumeration of allowed shapes.
    """

    CIRCLE = "Circle"
    TRIANGLE = "Triangle"
    RECTANGLE = "Rectangle"
    SQUARE = "Square"


def extract_contours(frame: np.ndarray) -> list:
    """
    Function used to extract valid contours from a frame.

    :param frame: Frame with the objects to extract contours from (should be black and white)
    :return: Set of valid contours
    """

    # Find contours of objects
    contours = cv2.findContours(frame, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[0]

    # Initialise a set of valid contours
    valid_contours = list()

    # Iterate through each contour in the frame
    for contour in contours:

        # Check if the current contour is big enough to be considered valid
        if cv2.contourArea(contour) > frame.shape[0] * frame.shape[1] * CONTOUR_SIZE_BOUND:

            # Add the contour to the set
            valid_contours.append(contour)

    # Return the frame with contours
    return valid_contours


def filter_by_colour(frame: np.ndarray, colour: Colour) -> np.ndarray:
    """
    Function used to filter a frame by removing all objects which do not much the given :class:`Colour`.

    :param frame: Frame to filter
    :param colour: Colour to filter by
    :return: Filtered frame
    """

    # Convert the frame to the hsv colour range
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Manually check which colour was passed (this is due to red colour being handled in a different way)
    if colour == Colour.RED:

        # Thresh the frame to find the red colours, using defined constants
        red_low = cv2.inRange(hsv, RED_MIN_LOW, RED_MAX_LOW)
        red_high = cv2.inRange(hsv, RED_MIN_HIGH, RED_MAX_HIGH)

        # Join the threshes to extract all red colours
        hsv = cv2.addWeighted(red_low, 1.0, red_high, 1.0, 0.0)

    elif colour == Colour.BLUE:

        # Thresh the frame to find the blue colours, using defined constants
        hsv = cv2.inRange(hsv, BLUE_MIN, BLUE_MAX)

    else:

        # Thresh the frame to find the black colours, using defined constants
        hsv = cv2.inRange(hsv, BLACK_MIN, BLACK_MAX)

    # TODO: Possibly apply GaussianBlur or other vision kernels
    # hsv = cv2.GaussianBlur(hsv, (5, 5), 0)

    # Return the threshed frame
    return hsv


def detect_shape(contour: np.ndarray) -> Shape:
    """
    Function used to detect :class:`Shape` based on the contour provided.

    :param contour: Contour of the shape
    :return: Shape enum
    """

    # Computer the shape perimeter
    perimeter = cv2.arcLength(contour, True)

    # Approximate the shape
    approx = cv2.approxPolyDP(contour, CONTOUR_EPSILON_FRACTION * perimeter, True)

    # If triangle
    if len(approx) == 3:
        return Shape.TRIANGLE

    # If rectangle
    elif len(approx) == 4:

        # Extract the dimensions of the contour
        width, height = extract_dimensions(contour)

        # Ignore heights of 0
        if height != 0:

            # Compute the width to height ratio
            ratio = width / height

        # Assume it's a rectangle in case of invalid height
        else:
            ratio = 0

        # Check if the ratio is nearly 1 (is the shape a square)
        if 1 - CONTOUR_RATIO_TOLERANCE <= ratio <= 1 + CONTOUR_RATIO_TOLERANCE:
            return Shape.SQUARE
        else:
            return Shape.RECTANGLE

    # If circle
    else:
        return Shape.CIRCLE


def count_shapes(frame: np.ndarray, colour: Colour) -> (dict, np.ndarray):
    """
    Function used to count the number of specific :class:`Shape`s in an image.

    Additionally the function returns the original frame but with the contours draw and the description text added.

    .. note::

        While potentially useful for general tasks, this function was created to solve the benthic species problem.

    :param frame: Frame to count the shapes from
    :param colour: :class:`Colour` to find the shapes
    :return: :class:`Shape` to count mapping, frame
    """

    # Initialise the frame to draw the contours and the text onto
    new_frame = frame.copy()

    # Initialise the mapping
    shapes = dict()

    # Populate the shapes with initial values
    shapes[Shape.SQUARE] = 0
    shapes[Shape.RECTANGLE] = 0
    shapes[Shape.TRIANGLE] = 0
    shapes[Shape.CIRCLE] = 0

    # Iterate over the contours
    for contour in extract_contours(filter_by_colour(frame, colour)):

        # Detect the shape
        shape = detect_shape(contour)

        # Increase the counter for the shape
        shapes[shape] += 1

        # Calculate the moments of the contour
        moments = cv2.moments(contour)

        # Find the center points of the contour
        x = int(moments["m10"] / moments["m00"])
        y = int(moments["m01"] / moments["m00"])

        # Draw the contour onto the frame
        cv2.drawContours(new_frame, contour, -1, CONTOUR_COLOUR, CONTOUR_THICKNESS)

        # Find the text size
        text_size = cv2.getTextSize(shape.value, TEXT_FONT, TEXT_SCALE, TEXT_THICKNESS)

        # Draw the text onto the frame
        cv2.putText(new_frame, shape.value, (x - int(text_size[0][0]/2), y + int(text_size[0][1]/2)),
                    TEXT_FONT, TEXT_SCALE, TEXT_COLOUR, TEXT_THICKNESS)

    # Return the shapes dictionary
    return shapes, new_frame


def extract_dimensions(contour: np.ndarray) -> (float, float):
    """
    Function used to calculate rectangular pixel dimensions of a contour.

    :param contour: Contour of a shape to extract x, y dimensions from
    :return: Width, height of the shape
    """

    # Define a function to compute a midpoint between 2 points
    def midpoint(p0, p1): return (p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5

    # Find the minimum rectangular area
    box = cv2.minAreaRect(contour)

    # Find the points of the rectangle
    box = cv2.boxPoints(box)

    # Cast the points to ints
    box = np.array(box, dtype="int")

    # Order the box points correctly
    box = order_points(box)

    # Unpack the box points into separate variables
    top_left, top_right, bottom_right, bottom_left = box

    # Compute the midpoints and width, height
    height = euclidean(midpoint(top_left, top_right), midpoint(bottom_left, bottom_right))
    width = euclidean(midpoint(top_left, bottom_left), midpoint(top_right, bottom_right))

    # Return the sides
    return width, height


def split_frame(frame: np.ndarray) -> list:
    """
    Function used to split the frame into 9 segments.

    .. note::

        While potentially useful for general tasks, this function was created to solve the autonomous driving problem.

    Specifically, returns the frames (as list) with the following indexing::

        | 0 | 1 | 2 |
        | 3 | 4 | 5 |
        | 6 | 7 | 8 |

    :param frame: Frame to be split
    :return: List of segments
    """

    # Extract the height and width of each segment
    height, width = frame.shape[0] // 3, frame.shape[1] // 3

    # Initialise the segments list
    segments = list()

    # Extract the frame segments
    segments.append(frame[0:height, 0:width])
    segments.append(frame[0:height, width:2*width])
    segments.append(frame[0:height, 2*width:])
    segments.append(frame[height:2*height, 0:width])
    segments.append(frame[height:2*height, width:2*width])
    segments.append(frame[height:2*height, 2*width:])
    segments.append(frame[2*height:, 0:width])
    segments.append(frame[2*height:, width:2*width])
    segments.append(frame[2*height:, 2*width:])

    # Return the segments
    return segments


def find_centroids(frame: np.ndarray, colour: Colour) -> (tuple, tuple, np.ndarray):
    """
    Function used to find the balance centre of the middle 3 horizontal and vertical frames.

    Specifically, if the frames are in the following indexing format::

        | 0 | 1 | 2 |
        | 3 | 4 | 5 |
        | 6 | 7 | 8 |

    then the centroid points in (x, y) for row 3-4-5 and column 1-4-7 will be returned.

    Additionally the function returns the original frame but with the centroids found and the contours drawn.

    .. note::

        While potentially useful for general tasks, this function was created to solve the autonomous driving problem.

    :param frame: Frame to find the centroids from
    :param colour: Colour to filter the contours
    :return: (x, y) of the middle row, (x, y) of the middle column, frame with the visuals
    """

    # Make a copy of the frame
    drawing_frame = frame.copy()

    # Filter the frame by colour
    frame = filter_by_colour(frame, colour)

    # Extract and draw the contours
    cv2.drawContours(drawing_frame, extract_contours(frame), -1, CONTOUR_COLOUR, CONTOUR_THICKNESS)

    # Initialise the final coordinates (will be flattened to integers later)
    x_horizontal, y_horizontal, x_vertical, y_vertical = list(), list(), list(), list()

    # Split the frame into 9 segments
    frames = split_frame(frame)

    # Extract the middle horizontal set of frames
    horizontal = frames[3:6]

    # Extract the middle vertical set of frames
    vertical = [frames[1], frames[4], frames[7]]

    # Iterate over the horizontal frames
    for i, frame in enumerate(horizontal):

        # Extract the contours
        contours = extract_contours(frame)

        # Initialise the centroids sets
        x, y = list(), list()

        # Iterate over the contours
        for contour in contours:

            # Calculate the moments of the contour
            moments = cv2.moments(contour)

            # Find the center points of the contour and add it to the centroids sets
            x.append(int(moments["m10"] / moments["m00"]))
            y.append(int(moments["m01"] / moments["m00"]))

        # If any values were updated
        if len(x) > 0:

            # Calculate the final central points
            x = sum(x) // len(x)
            y = sum(y) // len(y)

            # Adjust the position based on which frame segment it is
            if i == 0:
                y += frame.shape[0]
            elif i == 1:
                y += frame.shape[0]
                x += frame.shape[1]
            else:
                y += frame.shape[0]
                x += 2 * frame.shape[1]

            # Add the final central points to the horizontal points set
            x_horizontal.append(x)
            y_horizontal.append(y)

            # Draw a circle marking the local centroid onto the frame
            cv2.circle(drawing_frame, (x, y), POINT_RADIUS_SMALL, POINT_COLOUR_A, -1)

    # Iterate over the vertical frames
    for i, frame in enumerate(vertical):

        # Extract the contours
        contours = extract_contours(frame)

        # Initialise the centroids sets
        x, y = list(), list()

        # Iterate over the contours
        for contour in contours:

            # Calculate the moments of the contour
            moments = cv2.moments(contour)

            # Find the center points of the contour and add it to the centroids sets
            x.append(int(moments["m10"] / moments["m00"]))
            y.append(int(moments["m01"] / moments["m00"]))

        # If any values were updated
        if len(x) > 0:

            # Calculate the final central points
            x = sum(x) // len(x)
            y = sum(y) // len(y)

            # Adjust the position based on which frame segment it is
            if i == 0:
                x += frame.shape[1]
            elif i == 1:
                y += frame.shape[0]
                x += frame.shape[1]
            else:
                y += 2 * frame.shape[0]
                x += frame.shape[1]

            # Add the final central points to the vertical points set
            x_vertical.append(x)
            y_vertical.append(y)

            # Draw a circle marking the local centroid onto the frame
            cv2.circle(drawing_frame, (x, y), POINT_RADIUS_SMALL, POINT_COLOUR_B, -1)

    # If any horizontal points were found
    if len(x_horizontal) > 0:

        # Calculate the final point and position it onto the frame correctly
        x_horizontal = sum(x_horizontal) // len(x_horizontal)
        y_horizontal = sum(y_horizontal) // len(y_horizontal)

        # Draw a cricle marking the final centroid onto the frame
        cv2.circle(drawing_frame, (x_horizontal, y_horizontal), POINT_RADIUS_BIG, POINT_COLOUR_A, -1)

    # If any horizontal points were found
    if len(x_vertical) > 0:

        # Calculate the final point and position it onto the frame correctly
        x_vertical = sum(x_vertical) // len(x_vertical)
        y_vertical = sum(y_vertical) // len(y_vertical)

        # Draw a cricle marking the final centroid onto the frame
        cv2.circle(drawing_frame, (x_vertical, y_vertical), POINT_RADIUS_BIG, POINT_COLOUR_B, -1)

    # Return the values and the frame
    return (x_horizontal, y_horizontal), (x_vertical, y_vertical), drawing_frame
