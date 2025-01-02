from PyQt6 import QtWidgets, QtGui, QtCore
from pic_border_UI import BorderPresetManager
import sys
import json
import os

class BorderPresetGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.preset_manager = BorderPresetManager()
        self.logo_preview = QtWidgets.QLabel(self)  # Initialize logo_preview here
        self.logo_preview.setFixedSize(229, 100)
        self.user_settings = self.load_user_settings()
        self.logo_folder = "./logo"

        self.initUI()
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid gray;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QComboBox {
                padding: 5px;
                border: 1px solid gray;
                border-radius: 3px;
            }
            QLabel {
                font-weight: bold;
            }
            QProgressBar {
                text-align: center;
            }
        """)

    def load_user_settings(self):
        settings_path = 'user_settings.json'
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                return json.load(f)
        return {"last_used_preset": "", "last_used_logo": "", "input_folder": "", "output_folder": ""}

    def save_user_settings(self):
        settings_path = 'user_settings.json'
        with open(settings_path, 'w') as f:
            json.dump(self.user_settings, f, indent=4)

    def initUI(self):
        self.setWindowTitle("Image Border Preset Manager")
        main_layout = QtWidgets.QVBoxLayout()
        top_layout = QtWidgets.QHBoxLayout()

        # Left layout for logo and preset selection
        left_layout = QtWidgets.QVBoxLayout()

        # Logo selection combo box (from logo folder)
        self.logo_combo = QtWidgets.QComboBox(self)
        self.logo_combo.currentIndexChanged.connect(self.update_logo_preview)
        self.update_logo_combo()
        if self.user_settings["last_used_logo"]:
            self.logo_combo.setCurrentText(self.user_settings["last_used_logo"])
        left_layout.addWidget(QtWidgets.QLabel("Select Logo:"))
        left_layout.addWidget(self.logo_combo)

        # Logo preview
        left_layout.addWidget(self.logo_preview)

        # Preset selection
        self.preset_combo = QtWidgets.QComboBox(self)
        self.preset_combo.addItems(self.preset_manager.presets.keys())
        self.preset_combo.currentIndexChanged.connect(self.on_preset_select)
        left_layout.addWidget(QtWidgets.QLabel("Preset:"))
        left_layout.addWidget(self.preset_combo)

        # Buttons
        save_btn = QtWidgets.QPushButton("Save Preset", self)
        save_btn.clicked.connect(self.save_preset)
        new_btn = QtWidgets.QPushButton("New Preset", self)
        new_btn.clicked.connect(self.new_preset)
        left_layout.addWidget(save_btn)
        left_layout.addWidget(new_btn)

        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left_layout)
        top_layout.addWidget(left_widget, alignment=QtCore.Qt.AlignmentFlag.AlignTop)

        # Right layout for parameters and options
        right_layout = QtWidgets.QVBoxLayout()

        # Preset parameters
        self.params_frame = QtWidgets.QGroupBox("Parameters")
        params_layout = QtWidgets.QFormLayout()
        self.params_frame.setLayout(params_layout)
        right_layout.addWidget(self.params_frame)

        # Parameter entries
        self.param_vars = {}
        self.create_parameter_entries(params_layout)

        # Signature options
        self.signature_options_frame = QtWidgets.QGroupBox("Signature Options")
        signature_options_layout = QtWidgets.QFormLayout()
        self.signature_options_frame.setLayout(signature_options_layout)
        right_layout.addWidget(self.signature_options_frame)
        self.create_signature_options_entries(signature_options_layout)
        top_layout.addLayout(right_layout)
        main_layout.addLayout(top_layout)

        # Folders selection
        self.input_folder = QtWidgets.QLineEdit(self)
        self.input_folder.setText(self.user_settings["input_folder"])
        input_folder_btn = QtWidgets.QPushButton("Browse Input Folder", self)
        input_folder_btn.clicked.connect(self.browse_input_folder)
        main_layout.addWidget(QtWidgets.QLabel("Input Folder:"))
        main_layout.addWidget(self.input_folder)
        main_layout.addWidget(input_folder_btn)

        self.output_folder = QtWidgets.QLineEdit(self)
        self.output_folder.setText(self.user_settings["output_folder"])
        output_folder_btn = QtWidgets.QPushButton("Browse Output Folder", self)
        output_folder_btn.clicked.connect(self.browse_output_folder)
        main_layout.addWidget(QtWidgets.QLabel("Output Folder:"))
        main_layout.addWidget(self.output_folder)
        main_layout.addWidget(output_folder_btn)

        # Delete input files checkbox
        self.delete_input_checkbox = QtWidgets.QCheckBox("Delete input files after processing", self)
        main_layout.addWidget(self.delete_input_checkbox)

        # Process folder button
        folder_process_btn = QtWidgets.QPushButton("Process All in Folder", self)
        folder_process_btn.clicked.connect(self.process_all_images_in_folder)
        main_layout.addWidget(folder_process_btn)

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar(self)
        main_layout.addWidget(self.progress_bar)

        # Restore last used preset
        last_preset = self.user_settings["last_used_preset"]
        if last_preset in self.preset_manager.presets:
            idx = self.preset_combo.findText(last_preset)
            if idx >= 0:
                self.preset_combo.setCurrentIndex(idx)

        self.setLayout(main_layout)

    def update_logo_combo(self):
        logo_folder = self.logo_folder  # Update this path to your logo folder
        logos = [f for f in os.listdir(logo_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        self.logo_combo.clear()
        self.logo_combo.addItems(logos)
        self.update_logo_preview()

    def update_logo_preview(self):
        logo_folder = self.logo_folder  # Update this path to your logo folder
        logo_path = os.path.join(logo_folder, self.logo_combo.currentText())
        pixmap = QtGui.QPixmap(logo_path)
        self.logo_preview.setPixmap(pixmap.scaled(self.logo_preview.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        self.logo_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def create_parameter_entries(self, layout):
        parameters = [
            "border_width", "extra_bottom_height", "font_size",
            "signature_text", "font_path", "include_signature"
        ]
        for param in parameters:
            if param == "include_signature":
                var = QtWidgets.QCheckBox(self)
            else:
                var = QtWidgets.QLineEdit(self)
            self.param_vars[param] = var
            layout.addRow(param, var)

        # Logo size needs special handling for two values
        logo_size_layout = QtWidgets.QHBoxLayout()
        self.param_vars["logo_size_w"] = QtWidgets.QLineEdit(self)
        self.param_vars["logo_size_h"] = QtWidgets.QLineEdit(self)
        logo_size_layout.addWidget(self.param_vars["logo_size_w"])
        logo_size_layout.addWidget(QtWidgets.QLabel("x"))
        logo_size_layout.addWidget(self.param_vars["logo_size_h"])
        layout.addRow("logo_size", logo_size_layout)

    def create_signature_options_entries(self, layout):
        signature_options = [
            "first_half_text", "first_half_font_size",
            "second_half_text", "second_half_font_size"
        ]
        for option in signature_options:
            var = QtWidgets.QLineEdit(self)
            self.param_vars[option] = var
            layout.addRow(option, var)

        # Add color selection for first half and second half
        self.param_vars["first_half_color"] = QtWidgets.QPushButton("Select First Half Color", self)
        self.param_vars["first_half_color"].clicked.connect(lambda: self.select_color("first_half_color"))
        layout.addRow("first_half_color", self.param_vars["first_half_color"])

        self.param_vars["second_half_color"] = QtWidgets.QPushButton("Select Second Half Color", self)
        self.param_vars["second_half_color"].clicked.connect(lambda: self.select_color("second_half_color"))
        layout.addRow("second_half_color", self.param_vars["second_half_color"])

        # Add modify signature checkbox
        self.param_vars["modify_signature"] = QtWidgets.QCheckBox(self)
        layout.addRow("modify_signature", self.param_vars["modify_signature"])

    def select_color(self, param):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.param_vars[param].setStyleSheet(f"background-color: {color.name()}")
            self.param_vars[param].setText(color.name())

    def browse_image(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Image File", "", "Image files (*.jpg *.jpeg *.png)")
        if filename:
            self.image_path.setText(filename)

    def browse_input_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Input Folder", "")
        if folder:
            self.input_folder.setText(folder)
            self.user_settings["input_folder"] = folder
            self.save_user_settings()

    def browse_output_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Folder", "")
        if folder:
            self.output_folder.setText(folder)
            self.user_settings["output_folder"] = folder
            self.save_user_settings()

    def on_preset_select(self):
        preset_name = self.preset_combo.currentText()
        if preset_name in self.preset_manager.presets:
            preset = self.preset_manager.presets[preset_name]
            self.update_parameter_values(preset)
        # Store last used preset
        self.user_settings["last_used_preset"] = preset_name
        self.save_user_settings()

    def update_parameter_values(self, preset):
        for param, var in self.param_vars.items():
            if param == "logo_size_w":
                var.setText(str(preset["logo_size"][0]))
            elif param == "logo_size_h":
                var.setText(str(preset["logo_size"][1]))
            elif param == "include_signature":
                var.setChecked(preset[param])
            elif param in preset.get("signature_options", {}):
                if isinstance(var, QtWidgets.QPushButton):
                    var.setStyleSheet(f"background-color: {preset['signature_options'][param]}")
                    var.setText(preset["signature_options"][param])
                elif isinstance(var, QtWidgets.QCheckBox):
                    var.setChecked(preset["signature_options"][param])
                else:
                    var.setText(str(preset["signature_options"][param]))
            elif param in preset:
                var.setText(str(preset[param]))
            else:
                var.setText("")

    def get_parameter_values(self):
        values = {}
        signature_options = {}
        for param, var in self.param_vars.items():
            if param == "logo_size_w" or param == "logo_size_h":
                continue
            if param == "include_signature":
                values[param] = var.isChecked()
            elif param in ["first_half_text", "first_half_color", "first_half_font_size", "second_half_text", "second_half_color", "second_half_font_size", "modify_signature"]:
                if isinstance(var, QtWidgets.QPushButton):
                    signature_options[param] = var.text()
                elif isinstance(var, QtWidgets.QCheckBox):
                    signature_options[param] = var.isChecked()
                else:
                    signature_options[param] = var.text()
            else:
                values[param] = var.text()
        values["logo_size"] = [
            int(self.param_vars["logo_size_w"].text()),
            int(self.param_vars["logo_size_h"].text())
        ]
        values["signature_options"] = signature_options
        return values

    def save_preset(self, process:bool=False):
        preset_name = self.preset_combo.currentText()
        if not preset_name:
            QtWidgets.QMessageBox.critical(self, "Error", "Please select or create a preset name")
            return
        self.preset_manager.presets[preset_name] = self.get_parameter_values()
        self.preset_manager.save_presets()
        if not process:
            QtWidgets.QMessageBox.information(self, "Success", "Preset saved successfully!")

    def new_preset(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "New Preset", "Enter preset name:")
        if ok and name:
            self.preset_manager.presets[name] = self.get_parameter_values()
            self.preset_combo.addItem(name)
            self.preset_combo.setCurrentText(name)
            self.preset_manager.save_presets()

    def process_all_images_in_folder(self):
        folder = self.input_folder.text()
        output = self.output_folder.text()
        if not folder or not output:
            QtWidgets.QMessageBox.critical(self, "Error", "Please select both input and output folders")
            return
        # Save the current preset
        self.save_preset(process=True)
        # Use logo from combo
        logo_path = os.path.join(self.logo_folder, self.logo_combo.currentText())

        preset_name = self.preset_combo.currentText()
        delete_input = self.delete_input_checkbox.isChecked()
        image_files = [f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        total_files = len(image_files)
        self.progress_bar.setMaximum(total_files)
        self.progress_bar.setValue(0)

        for i, filename in enumerate(image_files):
            in_path = os.path.join(folder, filename)
            self.preset_manager.apply_preset(preset_name, in_path, logo_path, output, delete_input)
            self.progress_bar.setValue(i + 1)

        QtWidgets.QMessageBox.information(self, "Done", "All images processed!")

    def run(self):
        self.show()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui = BorderPresetGUI()
    gui.run()
    sys.exit(app.exec())