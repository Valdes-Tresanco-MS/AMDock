from PyQt4 import QtGui, QtCore
import os, subprocess


class Help(QtGui.QWidget):
    def __init__(self, parent = None):
        super(Help, self).__init__(parent)
        self.parent = parent
        self.setObjectName("help_tab")

        self.version_box = QtGui.QGroupBox(self)
        self.version_box.setTitle("Version")
        self.version_label = QtGui.QLabel(self.version_box)
        self.version_label.setText('Build 1.1.0')

        self.documentation_box = QtGui.QGroupBox(self)
        self.documentation_box.setTitle("Documentation")

        self.documentation_label = QtGui.QLabel(self.documentation_box)
        self.documentation_label.setText('The documentation (Manual and Tutorials) are available here')

        self.documentation_button = QtGui.QPushButton(self.documentation_box)
        self.documentation_button.setText('Documentation')
        self.documentation_button.clicked.connect(lambda : subprocess.call(['xdg-open',self.parent.ws.manual]))

        self.citing_box = QtGui.QGroupBox(self)
        self.citing_box.setTitle("Cite Us")

        self.citing_label = QtGui.QLabel(self.citing_box)
        self.citing_label.setText('AMDock: a graphical tool for assisting molecular docking with Autodock-Vina and Autodock4')

        self.reference_box = QtGui.QGroupBox(self)
        self.reference_box.setTitle("References")

        self.reference_label = QtGui.QTextEdit()
        self.reference_label.setReadOnly(True)
        self.reference_label.setFrameStyle(QtGui.QFrame.NoFrame)
        self.reference_label.setLineWrapMode(QtGui.QTextEdit.WidgetWidth)
        self.reference_label.setWordWrapMode(QtGui.QTextOption.WordWrap)
        self.reference_label.setText(self.parent.tt.reference)

        self.reference_sarea = QtGui.QScrollArea(self.reference_box)
        self.reference_sarea.setWidget(self.reference_label)
        self.reference_sarea.setWidgetResizable(True)

        self.version_box_layout = QtGui.QHBoxLayout(self.version_box)
        self.version_box_layout.addWidget(self.version_label)

        self.doc_box_layout = QtGui.QHBoxLayout(self.documentation_box)
        self.doc_box_layout.addWidget(self.documentation_label)
        self.doc_box_layout.addStretch()
        self.doc_box_layout.addWidget(self.documentation_button)

        self.citing_box_layout = QtGui.QHBoxLayout(self.citing_box)
        self.citing_box_layout.addWidget(self.citing_label)

        self.reference_box_layout = QtGui.QHBoxLayout(self.reference_box)
        self.reference_box_layout.addWidget(self.reference_sarea)

        self.info_tab_layout = QtGui.QVBoxLayout(self)
        self.info_tab_layout.addWidget(self.version_box)
        self.info_tab_layout.addWidget(self.documentation_box)
        self.info_tab_layout.addWidget(self.citing_box)
        self.info_tab_layout.addWidget(self.reference_box)

