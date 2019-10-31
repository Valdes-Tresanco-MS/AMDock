#!/bin/python
import sys
from checker import Checker
from file_loader import *
from info_tab import Help
from input_tab import Program_body
from lobby_tab import Lobby
from output_file import OutputFile
from result_tab import Results
from setting_tab import Configuration_tab
from variables import Variables, WorkersAndScripts, Text_and_ToolTip, Objects
from PyQt4 import QtGui, QtCore
__version__ = "1.1.2 For Windows and Linux"


class AMDock(QtGui.QMainWindow):
    def __init__(self):
        super(AMDock, self).__init__()
        QtGui.QMainWindow.__init__(self)

        self.checker = Checker(self)
        self.output2file = OutputFile(self)
        self.loader = Loader(self)
        self.v = Variables()
        self.ws = WorkersAndScripts()
        self.tt = Text_and_ToolTip()
        self.objects = Objects()

        with open(self.objects.style_file) as f:
            self.setStyleSheet(f.read())

        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap(self.objects.home_icon_white), QtGui.QIcon.Active, QtGui.QIcon.Off)
        self.icon.addPixmap(QtGui.QPixmap(self.objects.home_icon_white), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.icon.addPixmap(QtGui.QPixmap(self.objects.home_icon_white), QtGui.QIcon.Selected, QtGui.QIcon.Off)
        self.icon.addPixmap(QtGui.QPixmap(self.objects.home_icon_white), QtGui.QIcon.Disabled, QtGui.QIcon.Off)
        self.icon.addPixmap(QtGui.QPixmap(self.objects.home_icon), QtGui.QIcon.Selected, QtGui.QIcon.On)
        self.icon.addPixmap(QtGui.QPixmap(self.objects.home_icon), QtGui.QIcon.Active, QtGui.QIcon.On)

        ##--TABS
        self.main_window = QtGui.QTabWidget(self)
        self.setCentralWidget(self.main_window)

        ##--Tabs for Docking Options
        self.lobby = Lobby(self)
        self.main_window.addTab(self.lobby, self.icon, "")
        self.program_body = Program_body(self)
        self.main_window.addTab(self.program_body, "Docking Options")
        self.main_window.setTabEnabled(1, False)

        ##Tabs for result analysis
        self.result_tab = Results(self)
        self.main_window.addTab(self.result_tab, "Results Analysis")
        self.main_window.setTabEnabled(2, False)

        # **Configurations_Tab
        self.configuration_tab = Configuration_tab(self)
        self.main_window.addTab(self.configuration_tab, "Configuration")

        # ** Help_Tab
        self.help_tab = Help(self)
        self.main_window.addTab(self.help_tab, "Info")

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(self)
        self.version = QtGui.QLabel("Version: %s" % __version__)
        self.statusbar.addWidget(self.version)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtGui.QMessageBox.Yes,
                                           QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            try:
                self.program_body.worker.__del__()
            except:
                pass
            try:
                self.result_tab.bestw.__del__()
            except:
                pass
            try:
                self.result_tab.bestwB.__del__()
            except:
                pass
            try:
                self.result_tab.allw.__del__()
            except:
                pass
            try:
                self.result_tab.allwB.__del__()
            except:
                pass
            try:
                self.program_body.b_pymol.__del__()
            except:
                pass
            try:
                self.program_body.b_pymolB.__del__()
            except:
                pass
            try:
                self.program_body.complexw.__del__()
            except:
                pass
            event.accept()
        else:
            event.ignore()

from splash_screen import SplashScreen
from variables import Objects as ob

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    app_icon = QtGui.QIcon()
    dw = QtGui.QDesktopWidget()
    app_icon.addFile('images/amdock_icon.png', QtCore.QSize(16, 20))
    app_icon.addFile('images/amdock_icon.png', QtCore.QSize(24, 30))
    app_icon.addFile('images/amdock_icon.png', QtCore.QSize(32, 40))
    app_icon.addFile('images/amdock_icon.png', QtCore.QSize(48, 60))
    app_icon.addFile('images/amdock_icon.png', QtCore.QSize(223, 283))
    app.setStyle("cleanlooks")
    app.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(ob.app_icon)))
    app.setApplicationName('AMDock: Assisted Molecular Docking for AutoDock and AutoDock Vina')
    splash = SplashScreen(QtGui.QPixmap(ob.splashscreen_path), app)
    main = AMDock()
    splash.finish(main)
    main.setMinimumSize(1080, 740)
    main.resize(1080, int(dw.height()*0.9))
    main.setWindowTitle('AMDock: Assisted Molecular Docking with AutoDock4 and AutoDock Vina')
    main.setWindowIcon(app_icon)
    main.show()
    if splash.import_error():
        sys.exit(app.exec_())
    else:
        sys.exit(app.exit(1))
