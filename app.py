import sys, os, subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QInputDialog,
    QCheckBox, QScrollArea, QComboBox, QTextEdit, QDialog, QDialogButtonBox
)
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt

class AddSizesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter des Tailles")
        self.setModal(True)
        self.resize(300, 200)
        
        layout = QVBoxLayout()
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Entrez les tailles une par ligne, par exemple:\n128x128\n256x256")
        layout.addWidget(self.text_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_text(self):
        return self.text_edit.toPlainText()

class ImageResizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Redimensionneur d'Images")
        self.setGeometry(100, 100, 500, 600)
        self.setAcceptDrops(True)
        self.image_path = ""
        self.output_dir = ""
        self.sizes = [(16,16), (32,32), (64,64), (128,128), (256,256), (192,192), (512,512)]
        self.base_name = "icon"
        self.format = "png"
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # Image Selection Layout
        image_layout = QHBoxLayout()
        self.image_label = QLabel("Aucune image sélectionnée")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedHeight(200)
        image_layout.addWidget(self.image_label)
        select_image_btn = QPushButton("Sélectionner une Image")
        select_image_btn.clicked.connect(self.select_image)
        image_layout.addWidget(select_image_btn)
        main_layout.addLayout(image_layout)

        # Sizes Selection Layout
        sizes_layout = QVBoxLayout()
        sizes_header = QLabel("Tailles à redimensionner :")
        sizes_layout.addWidget(sizes_header)
        self.sizes_widget = QWidget()
        self.sizes_vbox = QVBoxLayout()
        self.size_checkboxes = []
        for size in self.sizes:
            cb = QCheckBox(f"{size[0]}x{size[1]}")
            cb.setChecked(True)
            self.size_checkboxes.append(cb)
            self.sizes_vbox.addWidget(cb)
        self.sizes_widget.setLayout(self.sizes_vbox)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.sizes_widget)
        sizes_layout.addWidget(scroll)
        sizes_buttons_layout = QHBoxLayout()
        add_size_btn = QPushButton("Ajouter des Tailles")
        add_size_btn.clicked.connect(self.add_size)
        remove_size_btn = QPushButton("Supprimer une Taille")
        remove_size_btn.clicked.connect(self.remove_size)
        select_all_btn = QPushButton("Tout Sélectionner")
        select_all_btn.clicked.connect(self.select_all_sizes)
        deselect_all_btn = QPushButton("Tout Désélectionner")
        deselect_all_btn.clicked.connect(self.deselect_all_sizes)
        sizes_buttons_layout.addWidget(add_size_btn)
        sizes_buttons_layout.addWidget(remove_size_btn)
        sizes_buttons_layout.addWidget(select_all_btn)
        sizes_buttons_layout.addWidget(deselect_all_btn)
        sizes_layout.addLayout(sizes_buttons_layout)
        main_layout.addLayout(sizes_layout)

        # Base Name and Format Layout
        base_name_layout = QHBoxLayout()
        base_name_label = QLabel("Nom de base :")
        self.base_name_input = QLineEdit(self.base_name)
        format_label = QLabel("Format :")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["png", "jpg", "bmp", "gif", "svg"])
        base_name_layout.addWidget(base_name_label)
        base_name_layout.addWidget(self.base_name_input)
        base_name_layout.addWidget(format_label)
        base_name_layout.addWidget(self.format_combo)
        main_layout.addLayout(base_name_layout)

        # Output Directory Layout
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Répertoire de sortie : Non sélectionné")
        self.output_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        output_layout.addWidget(self.output_label)
        select_output_btn = QPushButton("Sélectionner un Répertoire")
        select_output_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(select_output_btn)
        main_layout.addLayout(output_layout)

        # Resize Button
        resize_btn = QPushButton("Redimensionner les Images")
        resize_btn.clicked.connect(self.resize_images)
        main_layout.addWidget(resize_btn)

        central_widget.setLayout(main_layout)

    def select_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif *.svg)"])
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.image_path = selected_files[0]
                pixmap = QPixmap(self.image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.image_label.width(),
                        self.image_label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                    # Set output directory to the image's directory
                    self.output_dir = os.path.dirname(self.image_path)
                    self.output_label.setText(f"Répertoire de sortie : {self.output_dir}")

    def add_size(self):
        dialog = AddSizesDialog(self)
        if dialog.exec():
            sizes_text = dialog.get_text()
            if sizes_text:
                lines = sizes_text.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        parts = line.lower().split('x')
                        if len(parts) != 2:
                            raise ValueError
                        width = int(parts[0].strip())
                        height = int(parts[1].strip())
                        if (width, height) not in self.sizes:
                            self.sizes.append((width, height))
                            cb = QCheckBox(f"{width}x{height}")
                            cb.setChecked(True)
                            self.size_checkboxes.append(cb)
                            self.sizes_vbox.addWidget(cb)
                    except:
                        QMessageBox.warning(
                            self,
                            "Format Incorrect",
                            f"Format incorrect pour la taille : {line}. Utilisez largeur x hauteur, par exemple 128x128."
                        )

    def remove_size(self):
        selected_sizes = [cb for cb in self.size_checkboxes if cb.isChecked()]
        if not selected_sizes:
            QMessageBox.warning(
                self,
                "Aucune Sélection",
                "Veuillez sélectionner une taille à supprimer en cochant la case."
            )
            return
        for cb in selected_sizes:
            size_text = cb.text()
            parts = size_text.lower().split('x')
            if len(parts) == 2:
                try:
                    width = int(parts[0].strip())
                    height = int(parts[1].strip())
                    if (width, height) in self.sizes:
                        self.sizes.remove((width, height))
                except:
                    pass
            self.size_checkboxes.remove(cb)
            self.sizes_vbox.removeWidget(cb)
            cb.deleteLater()

    def select_all_sizes(self):
        for cb in self.size_checkboxes:
            cb.setChecked(True)

    def deselect_all_sizes(self):
        for cb in self.size_checkboxes:
            cb.setChecked(False)

    def select_output_dir(self):
        dir_dialog = QFileDialog(self)
        dir_dialog.setFileMode(QFileDialog.FileMode.Directory)
        dir_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        if dir_dialog.exec():
            selected_dirs = dir_dialog.selectedFiles()
            if selected_dirs:
                self.output_dir = selected_dirs[0]
                self.output_label.setText(f"Répertoire de sortie : {self.output_dir}")

    def resize_images(self):
        if not self.image_path:
            QMessageBox.warning(
                self,
                "Aucune Image",
                "Veuillez sélectionner une image à redimensionner."
            )
            return
        selected_sizes = [size for cb, size in zip(self.size_checkboxes, self.sizes) if cb.isChecked()]
        if not selected_sizes:
            QMessageBox.warning(
                self,
                "Aucune Taille",
                "Veuillez sélectionner au moins une taille de redimensionnement."
            )
            return
        if not self.output_dir:
            QMessageBox.warning(
                self,
                "Aucun Répertoire de Sortie",
                "Veuillez sélectionner un répertoire de sortie."
            )
            return
        self.base_name = self.base_name_input.text().strip()
        if not self.base_name:
            QMessageBox.warning(
                self,
                "Nom de Base Vide",
                "Veuillez entrer un nom de base pour les fichiers redimensionnés."
            )
            return
        self.format = self.format_combo.currentText()
        original_pixmap = QPixmap(self.image_path)
        if original_pixmap.isNull():
            QMessageBox.critical(
                self,
                "Erreur",
                "Impossible de charger l'image sélectionnée."
            )
            return
        for width, height in selected_sizes:
            resized_pixmap = original_pixmap.scaled(
                width,
                height,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            new_filename = f"{self.base_name}-{width}x{height}.{self.format}"
            save_path = os.path.join(self.output_dir, new_filename)
            if self.format.lower() == "svg":
                # QPixmap does not support saving SVG, notify the user
                QMessageBox.warning(
                    self,
                    "Format Incompatible",
                    f"Le format SVG n'est pas pris en charge pour le redimensionnement raster. Taille: {width}x{height}."
                )
                continue
            if not resized_pixmap.save(save_path, self.format.upper()):
                QMessageBox.warning(
                    self,
                    "Erreur d'Enregistrement",
                    f"Impossible d'enregistrer l'image {new_filename}."
                )
        self.open_output_dir()
        QMessageBox.information(
            self,
            "Terminé",
            "Les images ont été redimensionnées avec succès."
        )

    def open_output_dir(self):
        if not self.output_dir:
            return
        try:
            if sys.platform.startswith('darwin'):
                subprocess.call(['open', self.output_dir])
            elif os.name == 'nt':
                os.startfile(self.output_dir)
            elif os.name == 'posix':
                subprocess.call(['xdg-open', self.output_dir])
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erreur",
                f"Impossible d'ouvrir le répertoire de sortie.\nErreur : {e}"
            )

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                if os.path.isfile(file_path) and any(
                    file_path.lower().endswith(ext) for ext in ['.png','.xpm','.jpg','.jpeg','.bmp','.gif', '.svg']
                ):
                    self.image_path = file_path
                    pixmap = QPixmap(self.image_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            self.image_label.width(),
                            self.image_label.height(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.image_label.setPixmap(scaled_pixmap)
                        # Set output directory to the image's directory
                        self.output_dir = os.path.dirname(self.image_path)
                        self.output_label.setText(f"Répertoire de sortie : {self.output_dir}")

def main():
    app = QApplication(sys.argv)
    window = ImageResizer()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
