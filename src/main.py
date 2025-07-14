import sys
import numpy as np
from PySide6.QtWidgets import (
    QApplication ,QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QFormLayout, QGridLayout,
    QSpinBox, QDoubleSpinBox, QLabel, QPushButton, QGroupBox
)
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt
from speckle_generator import image_speckle

GROUP_BOX_STYLESHEET = """
                   QGroupBox {
                       border: 1px solid gray;
                       border-radius: 3px;
                       margin-top: 10px;
                   }
                   QGroupBox::title {
                       subcontrol-origin: margin;
                       left: 10px;
                       padding: 0 3px 0 3px;
                   }
               """

class ImageWidget(QWidget):

    window_side = 500
    def __init__(self, array):
        super().__init__()
        self.layout = QVBoxLayout()
        self.render_window = QLabel()
        self.render_window.setFixedSize(self.window_side, self.window_side)
        self.render_window.setStyleSheet("background-color: white")
        self.render_window.setFrameStyle(1)
        self.render_window.setLineWidth(1)
        # initialize qimage with default values in image_speckle
        self.qimage = self.numpy_to_image(array)
        self.update_pixmap()

        self.layout.addWidget(self.render_window)
        self.setLayout(self.layout)

    @staticmethod
    def numpy_to_image(array: np.ndarray):
        if array.ndim == 2:
            height, width = array.shape
            qimage = QImage(array.data, width, height, width, QImage.Format.Format_Grayscale8)
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
                self.render_window.width(), self.render_window.height(),
                aspectMode=Qt.AspectRatioMode.KeepAspectRatioByExpanding, mode=Qt.TransformationMode.FastTransformation
            )
            self.render_window.setPixmap(scaled_pixmap)

class ParameterWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.data_box = QGroupBox("Data")
        self.data_box.setMaximumHeight(250)
        self.data_box.setStyleSheet(GROUP_BOX_STYLESHEET)

        self.generate_box = QGroupBox("Generate")
        self.generate_box.setMaximumHeight(70)
        self.generate_box.setStyleSheet(GROUP_BOX_STYLESHEET)
        self.generate_layout = QHBoxLayout()

        self.layout = QFormLayout()
        self.default_values = {
            "height" : 50,
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
        self.grid_step_widget.setRange(0.5, 10)
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
        self.regen_widget = QPushButton("Apply")
        self.regen_widget.setFixedSize(100,30)
        # invert button
        self.invert_widget = QPushButton("Invert")
        self.invert_widget.setFixedSize(100, 30)
        #Load defaults button
        self.defaults_button = QPushButton("Set defaults")
        self.defaults_button.setFixedSize(100, 30)

        self.layout.addRow(" Height (mm)", self.height_widget)
        self.layout.addRow(" Width (mm)", self.width_widget)
        self.layout.addRow(" Diameter (mm)", self.diameter_widget)
        self.layout.addRow(" Dpi (dot per inch)", self.dpi_widget)
        self.layout.addRow(" Grid step (% of diameter)", self.grid_step_widget)
        self.layout.addRow(" Minimum diameter (% of diameter)", self.min_diameter_widget)
        self.layout.addRow(" Position randomness (% of diameter)", self.rand_position_widget)

        self.generate_layout.addWidget(self.invert_widget)
        self.generate_layout.addWidget(self.regen_widget)
        self.generate_layout.addWidget(self.defaults_button)

        self.data_box.setLayout(self.layout)
        self.generate_box.setLayout(self.generate_layout)

        self.main_layout.addWidget(self.data_box)
        self.main_layout.addWidget(self.generate_box)

        self.setLayout(self.main_layout)

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


class ResultsWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.results_box = QGroupBox("Results")
        self.results_box.setMaximumHeight(150)

        self.results_layout = QGridLayout()

        self.speckle_density_label = QLabel("Density:")
        self.MIG_label = QLabel("MIG:")
        self.autocorrelation_map = QLabel("Autocorrelation Map")
        self.speckle_density_result_label = QLabel("%")
        self.MIG_result_label = QLabel("31")
        self.autocorrelation_map_generate_button = QPushButton("Generate")

        self.results_layout.addWidget(self.speckle_density_label, 0, 0)
        self.results_layout.addWidget(self.MIG_label, 1, 0)
        self.results_layout.addWidget(self.autocorrelation_map, 2, 0)
        self.results_layout.addWidget(self.speckle_density_result_label, 0, 1)
        self.results_layout.addWidget(self.MIG_result_label, 1, 1)
        self.results_layout.addWidget(self.autocorrelation_map_generate_button, 2, 1)

        self.results_box.setLayout(self.results_layout)
        self.main_layout.addWidget(self.results_box)

        self.setLayout(self.main_layout)


class SaveWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QHBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.save_group = QGroupBox("Save")
        self.save_layout = QHBoxLayout()

        self.save_button = QPushButton("Save as")
        self.save_params = QPushButton("Save Parameters")

        self.save_layout.addWidget(self.save_button)
        self.save_layout.addWidget(self.save_params)

        self.save_group.setLayout(self.save_layout)

        self.main_layout.addWidget(self.save_group)

        self.setLayout(self.main_layout)

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setFixedSize(900, 550)
        self.setWindowTitle("Speckle Generator - Rodrigo Parrilla")

        self.main_widget = QWidget()
        self.main_layout = QGridLayout(self.main_widget)

        self.data = ParameterWidget()
        self.results = ResultsWidget()
        self.save = SaveWidget()

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
        # Flag storing whether the image is inverted. False by default
        self.is_inverted = False
        self.wire_connections()


        self.main_layout.addWidget(self.data, 0, 0)
        self.main_layout.addWidget(self.image, 0, 1, 3, 1)
        self.main_layout.addWidget(self.results, 1, 0)
        self.main_layout.addWidget(self.save, 2, 0)

        self.setCentralWidget(self.main_widget)

    def wire_connections(self):
        self.data.regen_widget.clicked.connect(self.update_image)
        self.data.invert_widget.clicked.connect(self.invert_image)

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
        if self.is_inverted:
            self.image.set_image(~array)
        else:
            self.image.set_image(array)

    def invert_image(self):
        self.is_inverted = not self.is_inverted
        self.update_image()

if __name__ == "__main__":

    App = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(App.exec())
