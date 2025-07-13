import sys
import numpy as np
from PySide6.QtWidgets import (
    QApplication ,QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QFormLayout,
    QSpinBox, QDoubleSpinBox, QLabel, QSizePolicy, QPushButton
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from speckle_generator import image_speckle

class ImageWidget(QWidget):

    window_side = 500
    def __init__(self, array):
        super().__init__()
        self.layout = QVBoxLayout()
        self.render_window = QLabel()
        self.render_window.setFixedSize(self.window_side, self.window_side)
        # initialize qimage with default values in image_speckle
        self.qimage = self.numpy_to_image(array)
        self.update_pixmap()

        self.layout.addWidget(self.render_window)
        self.setLayout(self.layout)

    @staticmethod
    def numpy_to_image(array: np.ndarray):
        if array.ndim == 2:
            height, width = array.shape
            qimage = QImage(array.data, width, height, QImage.Format.Format_Grayscale8)
        else:
            raise ValueError("Unsupported array type: expected 2D grayscale")
        return qimage.copy()

    def set_image(self, new_array):
        """
        Creates a new QImage from a new array and stores it in self.qimage. It´s the external interface to set a new image
        :param new_array:
        :return:
        """
        self.qimage = self.numpy_to_image(new_array)
        self.update_pixmap()

    def update_pixmap(self):
        if self.qimage:
            scaled_pixmap = QPixmap.fromImage(self.qimage).scaled(
                self.render_window.height(), self.render_window.width(),
                aspectMode=Qt.KeepAspectRatio, mode=Qt.FastTransformation
            )
            self.render_window.setPixmap(scaled_pixmap)

class ParameterWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QFormLayout()
        # dictionary containing all values
        self.default_values = {
            "height" : 25,
            "width" : 25,
            "diameter" : 0.5,
            "dpi" : 300,
            "grid_step" : 1,
            "min_diameter" : 50,
            "rand_pos" : 100
        }

        # height parameter
        self.height_widget = QSpinBox()
        self.height_widget.setRange(10, 1000)
        self.height_widget.setValue(self.default_values["height"])
        # width parameter
        self.width_widget = QSpinBox()
        self.width_widget.setRange(10, 1000)
        self.width_widget.setValue(self.default_values["width"])
        # speckle diameter parameter
        self.diameter_widget = QDoubleSpinBox()
        self.diameter_widget.setRange(0.01, 100)
        self.diameter_widget.setSingleStep(0.01)
        self.diameter_widget.setValue(self.default_values["diameter"])
        # dpi parameter
        self.dpi_widget = QSpinBox()
        self.dpi_widget.setRange(1, 1200)
        self.dpi_widget.setValue(self.default_values["dpi"])
        # grid step parameter
        self.grid_step_widget = QDoubleSpinBox()
        self.grid_step_widget.setRange(0.7, 10)
        self.grid_step_widget.setSingleStep(0.01)
        self.grid_step_widget.setValue(self.default_values["grid_step"])
        # minimum diameter parameter
        self.min_diameter_widget = QSpinBox()
        self.min_diameter_widget.setRange(1, 100)
        self.min_diameter_widget.setValue(self.default_values["min_diameter"])
        # position randomness parameter
        self.rand_position_widget = QSpinBox()
        self.rand_position_widget.setRange(0, 100)
        self.rand_position_widget.setValue(self.default_values["rand_pos"])
        # regenerate button
        self.regen_widget = QPushButton()
        self.regen_widget.setText("Apply")
        self.regen_widget.setFixedSize(100,30)


        self.layout.addRow(" Height (mm)", self.height_widget)
        self.layout.addRow(" Width (mm)", self.width_widget)
        self.layout.addRow(" Diameter (mm)", self.diameter_widget)
        self.layout.addRow(" Dpi (dot per inch)", self.dpi_widget)
        self.layout.addRow(" Grid step (% of diameter)", self.grid_step_widget)
        self.layout.addRow(" Size randomness (%)", self.min_diameter_widget)
        self.layout.addRow(" Position randomness (%)", self.rand_position_widget)
        self.layout.addRow("",self.regen_widget)

        self.setLayout(self.layout)

    def get_values(self):
        self.values = {
            "height": self.height_widget.value(),
            "width": self.width_widget.value(),
            "diameter": self.diameter_widget.value(),
            "dpi": self.dpi_widget.value(),
            "grid_step": self.grid_step_widget.value(),
            "min_diameter": self.min_diameter_widget.value(),
            "rand_pos": self.rand_position_widget.value()
        }
        return self.values


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setFixedSize(750, 550)

        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)

        self.data = ParameterWidget()
        self.values = self.gather_values()

       #Create first image with defaults
        self.image = ImageWidget(
            image_speckle(
                self.values["width"],
                self.values["height"],
                self.values["diameter"],
                self.values["dpi"],
                self.values["grid_step"],
                self.values["min_diameter"],
                self.values["rand_pos"]
            )
        )
        self.wire_connections()

        self.main_layout.addWidget(self.data, 1)
        self.main_layout.addWidget(self.image, 4)

        self.setCentralWidget(self.main_widget)


    def wire_connections(self):
        self.data.regen_widget.clicked.connect(self.update_image)

    def gather_values(self):
        values = self.data.get_values()
        return values

    def update_image(self):
        self.values  = self.gather_values()
        # create array
        array = image_speckle(
            self.values["width"],
            self.values["height"],
            self.values["diameter"],
            self.values["dpi"],
            self.values["grid_step"],
            self.values["min_diameter"],
            self.values["rand_pos"]
        )
        self.image.set_image(array)

if __name__ == "__main__":

    App = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(App.exec())
