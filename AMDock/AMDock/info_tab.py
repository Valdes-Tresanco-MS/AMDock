from PyQt4 import QtGui, QtCore
import os


class Help(QtGui.QWidget):
    def __init__(self, parent = None):
        super(Help, self).__init__(parent)
        self.parent = parent
        self.setObjectName("help_tab")

        self.version_box = QtGui.QGroupBox(self)
        self.version_box.setGeometry(QtCore.QRect(5, 5, 890, 45))
        self.version_box.setTitle("Version")
        self.version_label = QtGui.QLabel(self.version_box)
        self.version_label.setText('Build 1.0.0')
        self.version_label.setGeometry(QtCore.QRect(10, 15, 300, 25))

        self.documentation_box = QtGui.QGroupBox(self)
        self.documentation_box.setGeometry(QtCore.QRect(5, 60, 890, 50))
        self.documentation_box.setTitle("Documentation")

        self.documentation_label = QtGui.QLabel(self.documentation_box)
        self.documentation_label.setText('The documentation (Manual and Tutorials) are available here')
        self.documentation_label.setGeometry(QtCore.QRect(10, 15, 400, 25))

        self.documentation_button = QtGui.QPushButton(self.documentation_box)
        self.documentation_button.setGeometry(QtCore.QRect(420, 15, 100, 25))
        self.documentation_button.setText('Documentation')
        self.documentation_button.clicked.connect(lambda : os.startfile(self.parent.ws.manual))

        self.citing_box = QtGui.QGroupBox(self)
        self.citing_box.setGeometry(QtCore.QRect(5, 115, 890, 70))
        self.citing_box.setTitle("Cite Us")

        self.citing_label = QtGui.QLabel(self.citing_box)
        self.citing_label.setText('AMDock: a graphical tool for assisting molecular docking with Autodock-Vina and Autodock4')
        self.citing_label.setGeometry(QtCore.QRect(10, 15, 850, 25))

        self.reference_box = QtGui.QGroupBox(self)
        self.reference_box.setGeometry(QtCore.QRect(5,190 , 890, 400))
        self.reference_box.setTitle("References")

        self.tempWidget = QtGui.QWidget()
        self.tempWidget.setGeometry(QtCore.QRect(0, 0, 860, 610))

        self.reference_label = QtGui.QLabel(self.tempWidget)
        self.reference_label.setText(self.parent.tt.reference)
        self.reference_label.setGeometry(QtCore.QRect(10, 5, 840, 600))
        # self.reference_label.setWordWrap(True)

        self.reference_sarea = QtGui.QScrollArea(self.reference_box)
        self.reference_sarea.setGeometry(QtCore.QRect(5, 20, 880, 375))
        self.reference_sarea.setWidget(self.tempWidget)



