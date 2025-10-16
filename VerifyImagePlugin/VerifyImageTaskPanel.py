# PySide2 Task Panel UI for VerifyImagePlugin

from typing import Optional

try:
    from PySide2 import QtCore, QtGui, QtWidgets
except Exception as e:
    # Allow import outside FreeCAD runtime where PySide2 may not be available
    raise ImportError("PySide2 is required to use the UI inside FreeCAD.") from e

import os

class VerifyImageTaskPanel(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Verify with Image")
        self.image_path: Optional[str] = None

        # Widgets
        instruction = QtWidgets.QLabel("1. Align the 3D model to match your photo's perspective.")
        instruction.setWordWrap(True)

        self.uploadButton = QtWidgets.QPushButton("Upload Photo…")
        self.imagePreviewLabel = QtWidgets.QLabel()
        self.imagePreviewLabel.setFixedSize(320, 240)
        self.imagePreviewLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.imagePreviewLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.imagePreviewLabel.setText("No image selected")

        self.verifyButton = QtWidgets.QPushButton("Run Verification")
        self.verifyButton.setEnabled(False)

        self.resultsLabel = QtWidgets.QLabel("")
        self.overlayResultLabel = QtWidgets.QLabel()
        self.overlayResultLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.overlayResultLabel.setMinimumSize(320, 240)
        self.overlayResultLabel.setFrameShape(QtWidgets.QFrame.Box)

        # Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(instruction)

        row = QtWidgets.QHBoxLayout()
        row.addWidget(self.uploadButton)
        row.addStretch(1)
        layout.addLayout(row)

        layout.addWidget(self.imagePreviewLabel)
        layout.addWidget(self.verifyButton)
        layout.addWidget(self.resultsLabel)
        layout.addWidget(self.overlayResultLabel)
        layout.addStretch(1)

        # Connections
        self.uploadButton.clicked.connect(self.open_file_dialog)
        self.verifyButton.clicked.connect(self.start_verification)

    # FreeCAD TaskPanel API hooks
    def getStandardButtons(self):
        # Use default OK/Cancel if integrated as a TaskPanel; return 0 to hide.
        return 0

    def open_file_dialog(self):
        dlg = QtWidgets.QFileDialog(self, "Select an image", os.path.expanduser("~"))
        dlg.setNameFilters(["Images (*.png *.jpg *.jpeg *.bmp)"])
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        if dlg.exec_():
            paths = dlg.selectedFiles()
            if paths:
                self.image_path = paths[0]
                pix = QtGui.QPixmap(self.image_path)
                if not pix.isNull():
                    self.imagePreviewLabel.setPixmap(pix.scaled(self.imagePreviewLabel.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
                    self.verifyButton.setEnabled(True)
                else:
                    self.imagePreviewLabel.setText("Failed to load image")
                    self.verifyButton.setEnabled(False)

    def start_verification(self):
        if not self.image_path:
            QtWidgets.QMessageBox.warning(self, "No image", "Please select an image first.")
            return

        self.resultsLabel.setText("Processing…")
        QtWidgets.QApplication.processEvents()

        try:
            try:
                from .ImageProcessor import ImageProcessor
            except Exception:
                from ImageProcessor import ImageProcessor  # type: ignore

            processor = ImageProcessor()

            cad_contour = processor.generate_cad_silhouette()
            physical_contour, original_photo = processor.process_physical_image(self.image_path)

            if cad_contour is None or physical_contour is None:
                QtWidgets.QMessageBox.critical(self, "Error", "Could not extract contours from CAD view or photo.")
                self.resultsLabel.setText("")
                return

            score = processor.compare_silhouettes(cad_contour, physical_contour)
            overlay_image = processor.create_overlay_image(original_photo, cad_contour, physical_contour)

            if score < 0.05:
                self.resultsLabel.setText(f"✅ Verification Passed! Deviation: {score:.2f}")
            else:
                self.resultsLabel.setText(f"❌ Verification Failed! Deviation: {score:.2f}")

            # Convert overlay_image (BGR numpy array) to QPixmap
            if overlay_image is not None:
                height, width, channels = overlay_image.shape
                bytes_per_line = channels * width
                image = QtGui.QImage(overlay_image.data, width, height, bytes_per_line, QtGui.QImage.Format_BGR888)
                pix = QtGui.QPixmap.fromImage(image)
                self.overlayResultLabel.setPixmap(pix.scaled(self.overlayResultLabel.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Processing error", str(e))
            self.resultsLabel.setText("")
