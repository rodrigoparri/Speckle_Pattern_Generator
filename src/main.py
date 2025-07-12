import sys
import numpy as np
from PySide6.QtWidgets import (
    QApplication ,QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QFormLayout,
    QSpinBox, QLabel, QSizePolicy, QPushButton
)
from PySide6.QtGui import QImage, QPixmap


class ImageWidget(QWidget):

    def __init__(self, array):
        super().__init__()
        self.layout = QVBoxLayout()
        self.render_window = QLabel()

        self.qimage = self.numpy_to_image(array)
        self.render_window.setPixmap(QPixmap.fromImage(self.qimage))

        self.layout.addWidget(self.render_window)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setLayout(self.layout)

    @staticmethod
    def numpy_to_image(array: np.ndarray):
        if array.ndim == 2:
            height, width = array.shape
            qimage = QImage(array.data, width, height, QImage.Format.Format_Grayscale8)
        else:
            raise ValueError("Unsupported array type: expected 2D grayscale")
        return qimage.copy()

    def set_image(self):
        pass

class ParameterWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.layout = QFormLayout()

        # height parameter
        self.pattern_height_widget = QSpinBox()
        self.pattern_height_widget.setRange(0, 1000)
        # width parameter
        self.pattern_width_widget = QSpinBox()
        self.pattern_width_widget.setRange(0, 1000)
        # speckle diameter parameter
        self.pattern_diameter_widget = QSpinBox()
        self.pattern_diameter_widget.setRange(0, 100)
        # dpi parameter
        self.pattern_dpi_widget = QSpinBox()
        self.pattern_dpi_widget.setRange(1, 1200)
        # grid step parameter
        self.pattern_step_widget = QSpinBox()
        self.pattern_step_widget.setRange(0, 500)
        # size randomness parameter
        self.pattern_size_rand_widget = QSpinBox()
        self.pattern_size_rand_widget.setRange(0, 100)
        # position randomness parameter
        self.pattern_position_rand_widget = QSpinBox()
        self.pattern_position_rand_widget.setRange(0, 100)
        # regenerate button
        self.pattern_regen_widget = QPushButton()
        self.pattern_regen_widget.setText("Apply")
        self.pattern_regen_widget.setFixedSize(100,30)


        self.layout.addRow(" Height (mm)", self.pattern_height_widget)
        self.layout.addRow(" Width (mm)", self.pattern_width_widget)
        self.layout.addRow(" Diameter (mm)", self.pattern_diameter_widget)
        self.layout.addRow(" Dpi (dot per inch)", self.pattern_dpi_widget)
        self.layout.addRow(" Grid step (% of diameter)", self.pattern_step_widget)
        self.layout.addRow(" Size randomness (%)", self.pattern_size_rand_widget)
        self.layout.addRow(" Position randomness (%)", self.pattern_position_rand_widget)
        self.layout.addRow("",self.pattern_regen_widget)

        self.setLayout(self.layout)


class MainWindow(QMainWindow):

    trial_array = np.random.rand(500,500).astype(np.float32)
    def __init__(self):
        super().__init__()
        self.setFixedSize(750, 550)

        self.main_widget = QWidget()
        self.main_layout = QHBoxLayout(self.main_widget)

        self.data = ParameterWidget()
        self.image = ImageWidget(self.trial_array)

        self.main_layout.addWidget(self.data, 1)
        self.main_layout.addWidget(self.image, 4)

        self.setCentralWidget(self.main_widget)

    def wire_connections(self):
        #self.data.pattern_regen_widget.connect()
        pass

if __name__ == "__main__":

    App = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(App.exec())
