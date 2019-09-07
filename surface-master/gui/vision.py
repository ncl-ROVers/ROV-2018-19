from PySide2.QtWidgets import *
from PySide2.QtGui import QPixmap
from gui.tools import Tabs, ShapeDetectionCamera, get_manager, CAMERAS_COUNT
from vision.tools import count_shapes, Colour, Shape
from os import path
from cv2 import selectROI, destroyAllWindows, resize
from threading import Thread

RES = path.join(path.normpath(path.dirname(__file__)), "res", "vision")

# Declare the real dimensions of the reference object
REFERENCE_WIDTH = 57.2
REFERENCE_HEIGHT = 57.2


class Vision(QWidget):

    def __init__(self):
        super(Vision, self).__init__()

        # Initialise the outer layout
        layout = QVBoxLayout()

        # Initialise the shapes count and store a reference to it
        self.shapes_count = ShapesCount()

        # Build the layout
        layout.addWidget(Tabs())
        layout.addWidget(CameraPreviews())
        layout.addWidget(self.shapes_count)

        # Set the loading screen layout
        self.setLayout(layout)


class ShapesCount(QWidget):

    def __init__(self):
        super(ShapesCount, self).__init__()

        # Initialise the outer layout
        layout = QHBoxLayout()

        # Initialise the shape references
        self.shapes = {
            Shape.SQUARE: QLabel(),
            Shape.TRIANGLE: QLabel(),
            Shape.RECTANGLE: QLabel(),
            Shape.CIRCLE: QLabel()
        }

        # Initialise the image references to solve the visual task
        image_references = {
            Shape.SQUARE: "square.png",
            Shape.TRIANGLE: "triangle.png",
            Shape.RECTANGLE: "rectangle.png",
            Shape.CIRCLE: "circle.png"
        }

        # Iterate over the shapes
        for shape in Shape:

            # Initialise an image representation
            image = QLabel()

            # Update label with the referencing image
            image.setPixmap(QPixmap(path.join(RES, image_references[shape])).scaledToWidth(50))

            # Add the image representation to the layout
            layout.addWidget(image)

            # Set the initial text
            self.shapes[shape].setText("0")

            # Add the shape reference to the layout
            layout.addWidget(self.shapes[shape])

        # Set the final layout
        self.setLayout(layout)


class CameraPreviews(QWidget):

    def __init__(self):
        super(CameraPreviews, self).__init__()

        # Initialise the final layout
        layout = QHBoxLayout()

        # Populate the fields
        for i in range(CAMERAS_COUNT):

            # Add the camera's vertical layout
            inner_layout = QVBoxLayout()

            # Add the camera instance
            camera = ShapeDetectionCamera(i)

            # Add shape recognition button
            shape_button = QPushButton()
            shape_button.clicked.connect(self._on_click_shape_recognition_closure(i))
            shape_button.setText("Recognise shapes using camera {}".format(i))

            # Add dimensions estimation button
            dimensions_button = QPushButton()
            dimensions_button.clicked.connect(self._on_click_dimensions_estimation_closure(i))
            dimensions_button.setText("Estimate dimensions using camera {}".format(i))

            # Add the camera and the buttons to the layout
            inner_layout.addWidget(camera)
            inner_layout.addWidget(shape_button)
            inner_layout.addWidget(dimensions_button)

            # Wrap the layout and add it to the wrappers
            wrapper = QWidget()
            wrapper.setLayout(inner_layout)

            # Add the wrapper to the final layout
            layout.addWidget(wrapper)

        # Set the layout
        self.setLayout(layout)

    def _on_click_shape_recognition_closure(self, button_id):
        """
        Closure for the shape recognition button's on click event.

        :param button_id: Id of the button (therefore id of the camera)
        :return: Enclosed callback function
        """

        def _on_click_shape_recognition():
            """
            Function used to handle on click events raised by the shaper recognition buttons.
            """

            # Get the :class:`ShapesCount` reference
            shapes_count = get_manager(self).get_current_screen().shapes_count

            # Find the shapes
            shapes, _ = count_shapes(get_manager(self).streams[button_id].frame, Colour.BLACK)

            # Iterate over the shapes
            for shape in Shape:

                # Update the reference text
                shapes_count.shapes[shape].setText(str(shapes[shape]))

        # Return the enclosed function
        return _on_click_shape_recognition

    def _on_click_dimensions_estimation_closure(self, button_id):
        """
        Closure for the shape recognition button's on click event.

        :param button_id: Id of the button (therefore id of the camera)
        :return: Enclosed callback function
        """

        def _on_click_dimensions_estimation():

            # Run the ROI selection in a separate process
            Thread(target=inner).start()

        def inner():
            """
            Function used to handle on click events raised by the shaper recognition buttons.
            """

            # Get the current frame
            frame = get_manager(self).streams[button_id].frame

            # Resize the frame
            frame = resize(frame, (frame.shape[1]*3, frame.shape[0]*3))

            # Get the reference object's ROI
            reference_roi = selectROI("Select reference object", frame, showCrosshair=False)

            # Crop the reference ROI
            reference_roi = frame[int(reference_roi[1]):int(reference_roi[1] + reference_roi[3]),
                            int(reference_roi[0]):int(reference_roi[0] + reference_roi[2])]

            # Destroy the window
            destroyAllWindows()

            # Get the target object's ROI
            target_roi = selectROI("Select target object", frame, showCrosshair=False)

            # Crop the target ROI
            target_roi = frame[int(target_roi[1]):int(target_roi[1] + target_roi[3]),
                         int(target_roi[0]):int(target_roi[0] + target_roi[2])]

            # Destroy the window
            destroyAllWindows()

            # Calculate the ratio between the ROI-s
            ratio = target_roi.shape[1] / reference_roi.shape[1], target_roi.shape[0] / reference_roi.shape[0]

            # Calculate the real dimensions of the target
            width, height = ratio[0] * REFERENCE_WIDTH, ratio[1] * REFERENCE_HEIGHT

            # Print out the dimensions
            print("Target's dimensions are {} x {}".format(width, height))

        # Return the enclosed function
        return _on_click_dimensions_estimation
