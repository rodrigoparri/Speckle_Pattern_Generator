import sys
import numpy as np
from PySide6.QtWidgets import (
    QApplication ,QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QFormLayout,
    QSpinBox, QLabel, QSizePolicy
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

        self.pattern_height_widget = QSpinBox()
        self.pattern_height_widget.setRange(0, 1000)


        self.layout.addRow("Image height (mm)", self.pattern_height_widget)

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

if __name__ == "__main__":

    App = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.showMaximized()
    sys.exit(App.exec())
