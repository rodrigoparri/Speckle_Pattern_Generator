import sys
import numpy as np
import json
import ctypes
from pathlib import Path
import os
from PySide6.QtWidgets import (
    QApplication ,QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QFormLayout, QGridLayout,
    QSpinBox, QDoubleSpinBox, QLabel, QPushButton, QGroupBox, QFileDialog
)
from PySide6.QtGui import QImage, QPixmap, QIcon, QPainter, QPageSize
from PySide6.QtCore import Qt, QRectF, QLocale
from PySide6.QtPrintSupport import QPrinter, QPrintPreviewDialog
from speckle_generator import image_speckle, MIG, density

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

WINDOW_LOGO_PATH = Path("assets/logo.png")
DOCUMENTATION_PATH = Path("doc/Speckle_Pattern_Generator_Documentation.pdf")

def resource_path(relative_path: Path) -> Path:
    """
    Get absolute path to resource.
    """
    # check if run from bundle
    if hasattr(sys, "_MEIPASS") and getattr(sys, "frozen", False):
        print("run from bundle")
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = Path(".")
    else:
        base_path = Path(__file__).resolve().parent.parent
    return base_path / relative_path

class ImageWidget(QWidget):

    window_side = 500
    def __init__(self, array):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.render_window = QLabel()
        self.render_window.setFixedSize(self.window_side, self.window_side)
        self.render_window.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.render_window.setToolTip("Your image is scaled to fully fill the render window to ensure the pattern is clearly visible")
        #self.render_window.setStyleSheet("background-color: white")
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
        self.main_layout.setContentsMargins(1, 15, 1, 10)

        self.data_box = QGroupBox("Parameters")
        self.data_box.setMaximumHeight(250)
        self.data_box.setStyleSheet(GROUP_BOX_STYLESHEET)

        self.generate_box = QGroupBox("Generate")
        self.generate_box.setMaximumHeight(70)
        self.generate_box.setStyleSheet(GROUP_BOX_STYLESHEET)
        self.generate_layout = QHBoxLayout()

        self.layout = QFormLayout()
        self.default_values = {
            "height" : 50,
            "width" : 50,
            "diameter" : 0.5,
            "min_diameter" : 60,
            "dpi" : 300,
            "grid_step" : 1,
            "rand_pos" : 25
        }
        #(min value, max value)
        min_max_height = (10, 250)
        min_max_width = (10, 200)
        min_max_diameter = (0.01, 100)
        min_max_dpi = (1, 1200)
        min_max_grid_step = (0.5, 10)
        min_max_mindiameter = (1, 100)
        min_max_pos_rand = (0, 200)

        # height parameter
        self.height_widget = QSpinBox()
        self.height_widget.setRange(min_max_height[0], min_max_height[1])
        self.height_widget.setValue(self.default_values["height"])
        self.height_widget.setToolTip(f"Image height in mm, Min: {min_max_height[0]} Max: {min_max_height[1]}")
        # width parameter
        self.width_widget = QSpinBox()
        self.width_widget.setRange(min_max_width[0], min_max_width[1])
        self.width_widget.setValue(self.default_values["width"])
        self.width_widget.setToolTip(f"Image width in mm, Min: {min_max_width[0]} Max: {min_max_width[1]}")
        # speckle diameter parameter
        self.diameter_widget = QDoubleSpinBox()
        self.diameter_widget.setRange(min_max_diameter[0], min_max_diameter[1])
        self.diameter_widget.setSingleStep(0.01)
        self.diameter_widget.setLocale(QLocale(QLocale.Language.English))
        self.diameter_widget.setValue(self.default_values["diameter"])
        self.diameter_widget.setToolTip(f"Diameter in mm, Min: {min_max_diameter[0]}, Max: {min_max_diameter[1]}")
        # minimum diameter parameter
        self.min_diameter_widget = QSpinBox()
        self.min_diameter_widget.setRange(min_max_mindiameter[0], min_max_mindiameter[1])
        self.min_diameter_widget.setValue(self.default_values["min_diameter"])
        self.min_diameter_widget.setToolTip(f"Minium diameter of speckle as % of max diameter Min: {min_max_mindiameter[0]}, Max: {min_max_mindiameter[1]}")
        # dpi parameter
        self.dpi_widget = QSpinBox()
        self.dpi_widget.setRange(min_max_dpi[0], min_max_dpi[1])
        self.dpi_widget.setValue(self.default_values["dpi"])
        self.dpi_widget.setToolTip(f"Resolution in dot per inch, Min: {min_max_dpi[0]}, Max: {min_max_dpi[1]}")
        # grid step parameter
        self.grid_step_widget = QDoubleSpinBox()
        self.grid_step_widget.setRange(min_max_grid_step[0], min_max_grid_step[1])
        self.grid_step_widget.setSingleStep(0.01)
        self.grid_step_widget.setLocale(QLocale(QLocale.Language.English))
        self.grid_step_widget.setValue(self.default_values["grid_step"])
        self.grid_step_widget.setToolTip(f"Span between grid axis in mm, Min: {min_max_grid_step[0]}, Max: {min_max_grid_step[1]}")
        # position randomness parameter
        self.rand_position_widget = QSpinBox()
        self.rand_position_widget.setRange(min_max_pos_rand[0], min_max_pos_rand[1])
        self.rand_position_widget.setValue(self.default_values["rand_pos"])
        self.rand_position_widget.setToolTip(f"Random position radius as % of maximum diameter, Min: {min_max_pos_rand[0]}, Max: {min_max_pos_rand[1]}")
        # regenerate button
        self.regen_widget = QPushButton("Regenerate ▶")
        self.regen_widget.setFixedSize(100,30)
        # invert button
        self.invert_widget = QPushButton("Inverse")
        self.invert_widget.setFixedSize(100, 30)
        #Load defaults button
        self.defaults_button = QPushButton("Set defaults")
        self.defaults_button.setFixedSize(100, 30)

        self.layout.addRow(f" Height (mm) [{min_max_height[0]}-{min_max_height[1]}]", self.height_widget)
        self.layout.addRow(f" Width (mm) [{min_max_width[0]}-{min_max_width[1]}]", self.width_widget)
        self.layout.addRow(f" Maximum diameter (mm) [{min_max_diameter[0]}-{min_max_diameter[1]}]", self.diameter_widget)
        self.layout.addRow(f" Minimum diameter (%) [{min_max_mindiameter[0]}-{min_max_mindiameter[1]}]", self.min_diameter_widget)
        self.layout.addRow(f" Resolution (dpi) [{min_max_dpi[0]}-{min_max_dpi[1]}", self.dpi_widget)
        self.layout.addRow(f" Grid step (%) [{min_max_grid_step[0]}-{min_max_grid_step[1]}]", self.grid_step_widget)
        self.layout.addRow(f" Position randomness (%) [{min_max_pos_rand[0]}-{min_max_pos_rand[1]}]", self.rand_position_widget)

        self.generate_layout.addWidget(self.defaults_button)
        self.generate_layout.addWidget(self.invert_widget)
        self.generate_layout.addWidget(self.regen_widget)

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

    def set_default_values(self):
        self.height_widget.setValue(self.default_values["height"])
        self.width_widget.setValue(self.default_values["width"])
        self.diameter_widget.setValue(self.default_values["diameter"])
        self.dpi_widget.setValue(self.default_values["dpi"])
        self.grid_step_widget.setValue(self.default_values["grid_step"])
        self.min_diameter_widget.setValue(self.default_values["min_diameter"])
        self.rand_position_widget.setValue(self.default_values["rand_pos"])

    def set_values(self, values:dict):
        self.height_widget.setValue(values["height"])
        self.width_widget.setValue(values["width"])
        self.diameter_widget.setValue(values["diameter"])
        self.dpi_widget.setValue(values["dpi"])
        self.grid_step_widget.setValue(values["grid_step"])
        self.min_diameter_widget.setValue(values["min_diameter"])
        self.rand_position_widget.setValue(values["rand_pos"])


class ResultsWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.setContentsMargins(1, 1, 1, 1)
        self.results_box = QGroupBox("Results")
        self.results_box.setMaximumHeight(150)

        self.results_layout = QGridLayout()

        self.speckle_density_label = QLabel("Speckle Density:")
        self.MIG_label = QLabel("MIG:")
        self.autocorrelation_map = QLabel("Correlation coefficient_ZNSSD:")
        self.speckle_density_result_label = QLabel("%")
        self.speckle_density_result_label.setToolTip("Percentage of black pixels over the total pixel amount")
        self.MIG_result_label = QLabel("31")
        self.MIG_result_label.setToolTip("""Mean Intensity Gradient of the image being 0 intensity
         black pixels and 255 intensity white pixels""")
        self.autocorrelation_map_generate_label = QLabel("---------")
        self.autocorrelation_map_generate_label.setToolTip("""Zero normalized sum of the square differences 
        correlation coefficient""")

        self.results_layout.addWidget(self.speckle_density_label, 0, 0)
        self.results_layout.addWidget(self.MIG_label, 1, 0)
        self.results_layout.addWidget(self.autocorrelation_map, 2, 0)
        self.results_layout.addWidget(self.speckle_density_result_label, 0, 1)
        self.results_layout.addWidget(self.MIG_result_label, 1, 1)
        self.results_layout.addWidget(self.autocorrelation_map_generate_label, 2, 1)

        self.results_box.setLayout(self.results_layout)
        self.main_layout.addWidget(self.results_box)

        self.setLayout(self.main_layout)

    def set_MIG_result(self, result):
        self.MIG_result_label.setText(f"{result:.3f}")

    def set_density_result(self, result):
        self.speckle_density_result_label.setText(f"{result:.3f}%")

class SaveWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.main_layout = QHBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.main_layout.setContentsMargins(1, 10, 1, 10)

        self.save_group = QGroupBox("Save")
        self.save_layout = QHBoxLayout()

        self.save_button = QPushButton("Save Image as")
        self.save_params_button = QPushButton("Save Parameters")
        self.print_button = QPushButton("Print")

        self.save_layout.addWidget(self.save_params_button)
        self.save_layout.addWidget(self.save_button)
        self.save_layout.addWidget(self.print_button)

        self.save_group.setLayout(self.save_layout)

        self.main_layout.addWidget(self.save_group)

        self.setLayout(self.main_layout)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        #print(Path(__file__))
        #print(resource_path(WINDOW_LOGO_PATH))
        self.setWindowTitle("Speckle Pattern Generator - Windows - v.1.0")
        self.setWindowIcon(QIcon(str(resource_path(WINDOW_LOGO_PATH))))

        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.save_as_action = self.file_menu.addAction("Save Image as...")
        self.save_params_action = self.file_menu.addAction("Save parameters")
        self.load_params_action = self.file_menu.addAction("Load parameters")
        self.print_action = self.file_menu.addAction("Print")
        self.documentation_action = self.menu_bar.addAction("Documentation")

        self.main_widget = QWidget()
        self.main_layout = QGridLayout(self.main_widget)
        self.main_layout.setSpacing(5)

        self.parameters = ParameterWidget()
        self.results = ResultsWidget()
        self.save = SaveWidget()
        self.author = QLabel("Author: Rodrigo Parrilla Mesas 2025. License:")

        self.values = self.gather_values()
        self.array = image_speckle(
                self.values["width"],
                self.values["height"],
                self.values["diameter"],
                self.values["dpi"],
                self.values["grid_step"],
                self.values["min_diameter"],
                self.values["rand_pos"]
            )
        self.inverted_array = ~self.array

        self.mig = MIG(self.array)
        self.update_MIG()

        self.density = density(self.array)
        self.update_density()

       #Create first image with defaults
        self.image = ImageWidget(self.array)
        # Flag storing whether the image is inverted. False by default
        self.is_inverted = False

        self.main_layout.addWidget(self.image, 0, 1, 3, 1)
        self.main_layout.addWidget(self.parameters, 0, 0)
        self.main_layout.addWidget(self.results, 1, 0)
        self.main_layout.addWidget(self.save, 2, 0)
        self.main_layout.addWidget(self.author, 3, 0, 1, 1)

        self.wire_connections()
        self.setCentralWidget(self.main_widget)
        self.setFixedSize(900, 600)
        self.show()
        #center screen
        screen = QApplication.primaryScreen().availableGeometry()
        app_window = self.geometry()
        move_x = (screen.width() - app_window.width()) // 2
        move_y = (screen.height() - app_window.height()) // 2
        self.move(move_x, move_y)

    def wire_connections(self):
        self.parameters.regen_widget.clicked.connect(self.update_image)
        self.parameters.invert_widget.clicked.connect(self.invert_image)
        self.parameters.defaults_button.clicked.connect(self.parameters.set_default_values)

        self.save.save_params_button.clicked.connect(self.save_parameters)
        self.save.save_button.clicked.connect(self.save_file)
        self.save.print_button.clicked.connect(self.print_preview)

        self.save_params_action.triggered.connect(self.save_parameters)
        self.save_as_action.triggered.connect(self.save_file)
        self.load_params_action.triggered.connect(self.load_parameters)
        self.documentation_action.triggered.connect(self.show_documentation)


    def gather_values(self):
        values = self.parameters.get_values()
        return values

    def update_array(self):
        self.values  = self.gather_values()
        # create array
        self.array = image_speckle(
            self.values["width"],
            self.values["height"],
            self.values["diameter"],
            self.values["dpi"],
            self.values["grid_step"],
            self.values["min_diameter"],
            self.values["rand_pos"]
        )
        self.inverted_array = ~self.array

    def update_image(self):
        self.update_array()
        self.update_MIG()
        self.update_density()
        self.image.set_image(self.array)

    def invert_image(self):
        self.is_inverted = not self.is_inverted
        if self.is_inverted:
            self.image.set_image(self.inverted_array)
        else:
            self.image.set_image(self.array)

    def update_MIG(self):
        self.mig = MIG(self.array)
        self.results.set_MIG_result(self.mig)

    def update_density(self):
        self.density = density(self.array)
        self.results.set_density_result(self.density)

    def save_file(self):
        save_path, _ = QFileDialog.getSaveFileName(self,  "Save File", "",
        "PNG Image (*.png);;JPEG Image (*.jpg);;BMP Image (*.bmp);;All Files (*)"
        )
        self.image.qimage.save(save_path)

    def save_parameters(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "",
            "JSON file (*.json)"
        )
        if not save_path:
            return
        else:
            with open(f"{save_path}", "w", encoding="utf8") as outfile:
                file = json.dumps(self.values)
                outfile.write(file)

    def load_parameters(self):
        load_path, _ = QFileDialog.getOpenFileName(self, "Load File", "",
            "JSON file (*.json)"
        )
        if not load_path:
            return
        else:
            with open(f"{load_path}", "r", encoding="utf8") as infile:
                self.values = json.load(infile)
                self.parameters.set_values(self.values)
                self.update_image()

    def print_preview(self):
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setPageSize(QPageSize.PageSizeId.A4)
        printer.setResolution(self.values["dpi"])
        print_preview = QPrintPreviewDialog(printer, self)
        print_preview.paintRequested.connect(self.render_to_print)
        print_preview.exec()

    def render_to_print(self, printer):
        painter = QPainter(printer)
        image = self.image.qimage
        image_width = self.image.qimage.width()
        image_height = self.image.qimage.height()
        dpi = self.values["dpi"]
        mm_to_px = dpi / 25.4
        left_margin = (210 * mm_to_px - image_width) / 2
        top_margin = (270 * mm_to_px - image_height) / 2
        target_rect = QRectF(left_margin, top_margin, image_width, image_height)
        painter.drawImage(target_rect, image)
        text_target_rect = QRectF(20 * mm_to_px, 280 * mm_to_px, 100 * mm_to_px, 10 * mm_to_px)
        painter.drawText(text_target_rect, f"Density: {self.density:.3f}%  MIG: {self.mig:.3f}")
        painter.end()

    def show_documentation(self):
        os.startfile(os.path.normpath(str(resource_path(DOCUMENTATION_PATH))))

if __name__ == "__main__":
    myappid = 'Speckle_Pattern_Generator_v1.0'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    App = QApplication(sys.argv)
    App.setWindowIcon(QIcon(str(resource_path(WINDOW_LOGO_PATH))))
    main_window = MainWindow()
    sys.exit(App.exec())
