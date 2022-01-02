import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import subprocess

class Help(QWidget):
    def __init__(self, parent=None):
        super(Help, self).__init__(parent)
        self.AMDock = parent
        self.setObjectName("help_tab")

        self.version_box = QGroupBox(self)
        self.version_box.setTitle("Version")
        self.version_label = QLabel(self.version_box)
        self.version_label.setText(self.AMDock.version)

        self.documentation_box = QGroupBox(self)
        self.documentation_box.setTitle("Documentation")

        self.documentation_label = QLabel(self.documentation_box)
        self.documentation_label.setText('The documentation (Manual and Tutorials) are available here')

        self.documentation_button = QPushButton(self.documentation_box)
        self.documentation_button.setText('Documentation')
        self.documentation_button.clicked.connect(lambda : subprocess.call(['xdg-open',self.AMDock.manual]))

        self.citing_box = QGroupBox(self)
        self.citing_box.setTitle("Cite Us")

        self.citing_label = QLabel(self.citing_box)
        self.citing_label.setText('Valdes-Tresanco, M.S., Valdes-Tresanco, M.E., Valiente, P.A. and Moreno E. AMDock: a '
                                  'versatile graphical tool for assisting molecular docking with Autodock Vina and '
                                  'Autodock4. Biol Direct 15, 12 (2020). https://doi.org/10.1186/s13062-020-00267-2')
        self.citing_label.setWordWrap(True)
        self.citing_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.reference_box = QGroupBox(self)
        self.reference_box.setTitle("References")

        self.reference_label = QTextEdit()
        self.reference_label.setReadOnly(True)
        self.reference_label.setFrameStyle(QFrame.NoFrame)
        self.reference_label.setLineWrapMode(QTextEdit.WidgetWidth)
        self.reference_label.setWordWrapMode(QTextOption.WordWrap)
        self.reference_label.setText(self.AMDock.reference)

        self.reference_sarea = QScrollArea(self.reference_box)
        self.reference_sarea.setWidget(self.reference_label)
        self.reference_sarea.setWidgetResizable(True)

        self.version_box_layout = QHBoxLayout(self.version_box)
        self.version_box_layout.addWidget(self.version_label)

        self.doc_box_layout = QHBoxLayout(self.documentation_box)
        self.doc_box_layout.addWidget(self.documentation_label)
        self.doc_box_layout.addStretch()
        self.doc_box_layout.addWidget(self.documentation_button)

        self.citing_box_layout = QHBoxLayout(self.citing_box)
        self.citing_box_layout.addWidget(self.citing_label)

        self.reference_box_layout = QHBoxLayout(self.reference_box)
        self.reference_box_layout.addWidget(self.reference_sarea)

        self.info_tab_layout = QVBoxLayout(self)
        self.info_tab_layout.addWidget(self.version_box)
        self.info_tab_layout.addWidget(self.documentation_box)
        self.info_tab_layout.addWidget(self.citing_box)
        self.info_tab_layout.addWidget(self.reference_box)
