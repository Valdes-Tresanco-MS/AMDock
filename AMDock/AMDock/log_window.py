from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignal
import sys

class LogWindow(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        screen = QtGui.QDesktopWidget().screenGeometry()
        mysize = self.geometry()
        self.hpos = (screen.width() - mysize.width()) / 2
        self.vpos = 170
        self.setGeometry(QtCore.QRect(self.hpos + 100, self.vpos, 600, 500))
        self.setModal(False)
        self.parent = parent
        layout = QtGui.QVBoxLayout()

        font = QtGui.QFont('Courier New')
        font.setPointSize(10)
        font.setKerning(False)
        self.textedit = QtGui.QTextEdit(self)
        self.textedit.setFont(font)
        self.textedit.setReadOnly(True)
        self.textedit.append('Welcome to AMDock\nVersion 1.1.0 Licence GPL3\n')
        self.textedit.append('AMDOCK: IP Defining Initial Parameters...')
        layout.addWidget(self.textedit)
        self.parent.log_view.stateChanged.connect(lambda: self.ch_state(self.parent.log_view))
        self.finished.connect(self.closed)
        if self.parent.log_view.isChecked():
            self.show()

        self.setLayout(layout)

    def closed(self):
        self.parent.log_view.setChecked(False)

    def ch_state(self, st):
        if st.isChecked() == False:
            self.close()
        else:
            self.show()

    def insert_text(self, text):
        self.textedit.ap
