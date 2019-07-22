from PyQt4 import QtGui
from PyQt4 import QtCore
import sys

from checker import Checker
from file_loader import *
from lobby_tab import Lobby
from input_tab import Program_body
from setting_tab import Configuration_tab
from result_tab import Results
from info_tab import Help
from result2tab import Result_Analysis
from splash_screen import SplashScreen
from variables import Variables, WorkersAndScripts, Text_and_ToolTip,Objects
from output_file import OutputFile

__version__ = "1.0 For Windows and Linux"


class AMDock(QtGui.QMainWindow):
    def __init__(self, parent=None):
        #super(APDock, self).__init__(parent)
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

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(900,708)

        self.setMinimumSize(QtCore.QSize(900, 708))
        self.setMaximumSize(QtCore.QSize(900, 708))
        self.backgroundColor = self.hex2QColor("CDCDCD")

        self.borderRadius = 15
        self.draggable = True
        self.dragging_threshould = 5
        self.__mousePressPos = None
        self.__mouseMovePos = None
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
            ##--TITLE
        self.title = QtGui.QLabel(self)
        self.title.setGeometry(QtCore.QRect(10, -5, 770, 40))
        self.title.setObjectName("title")
        self.title.setText(self.tt.prog_title)

        ##--TABS
        self.windows = Lobby(self)
            ##--Tabs for Docking Options
        self.program_body = Program_body(self)
        self.windows.addTab(self.program_body, "Docking Options")

        ##Tabs for result analysis
        self.result_tab = Results(self)
        self.windows.addTab(self.result_tab, "Results Analysis")

            #**Configurations_Tab
        self.configuration_tab = Configuration_tab(self)
        self.windows.addTab(self.configuration_tab, "Configuration")
            #** Help_Tab
        self.help_tab = Help(self)
        self.windows.addTab(self.help_tab, "Info")

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.setStyleSheet("background-color: #CDCDCD;border-radius: 15px")
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

         #### detect hover mouse event
        self.timer12 = QtCore.QTimer(self)
        self.timer12.start(10)
        self.timer12.timeout.connect(self.Hover)
        ####end

        ####exit button
        self.exit = QtGui.QPushButton(self)
        self.exit.setGeometry(QtCore.QRect(860, 10, 31, 23))
        self.exit.setObjectName("exit")
        self.exit.setIconSize(QtCore.QSize(15,15))

        #####minimize button
        self.minimize = QtGui.QPushButton(self)
        self.minimize.setGeometry(QtCore.QRect(835, 10, 31, 23))
        self.minimize.setObjectName("minimize")
        self.minimize.setIconSize(QtCore.QSize(15, 15))

            #Windows position
        screen = QtGui.QDesktopWidget().screenGeometry()
        mysize = self.geometry()
        self.hpos = (screen.width() - mysize.width()) / 2
        self.vpos = 5
        self.setGeometry(QtCore.QRect(self.hpos, self.vpos, 900, 680))

        self.windows.setCurrentIndex(0)
        self.windows.setTabEnabled(1, False)
        self.windows.setTabEnabled(2, False)
        QtCore.QMetaObject.connectSlotsByName(self)

            #### Connections
            #*** exit and minimize
        self.exit.clicked.connect(self.close)
        self.minimize.clicked.connect(self.showMinimized)

        self.statusbar.showMessage("Version: %s" % __version__)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?",
                                           QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            try:self.program_body.worker.__del__()
            except:pass
            try:self.result_tab.bestw.__del__()
            except: pass
            try:self.result_tab.bestwB.__del__()
            except: pass
            try:self.result_tab.allw.__del__()
            except: pass
            try:self.result_tab.allwB.__del__()
            except: pass
            try:self.program_body.b_pymol.__del__()
            except:pass
            try:self.program_body.b_pymolB.__del__()
            except:pass
            try:self.program_body.complexw.__del__()
            except:pass
            event.accept()
        else:
            event.ignore()
    def Hover(self):
        ''' change propety of object'''
        ###effect for exit and minimize button
        if self.exit.underMouse() == True:
            self.exit.setIcon(QtGui.QIcon(QtGui.QPixmap(self.objects.close_icon_hover)))
            self.exit.setStyleSheet("background-color: rgb(192, 0, 0)")
        else:
            self.exit.setIcon(QtGui.QIcon(QtGui.QPixmap(self.objects.close_icon)))
            self.exit.setStyleSheet("background-color: #CDCDCD")
        if self.minimize.underMouse() == True:
            self.minimize.setIcon(QtGui.QIcon(QtGui.QPixmap(self.objects.minimize_icon_hover)))
            self.minimize.setStyleSheet("background-color: rgb(46, 117, 182)")
        else:
            self.minimize.setIcon(QtGui.QIcon(QtGui.QPixmap(self.objects.minimize_icon)))
            self.minimize.setStyleSheet("background-color: #CDCDCD")
        ###effect for vina_dock button
        if self.windows.dock_vina_button.underMouse():
            self.windows.comment_vina_dock.show()
        else:
            self.windows.comment_vina_dock.hide()
        ### effect for adock button
        if self.windows.adock_button.underMouse():
            self.windows.comment_adock.show()
        else:
            self.windows.comment_adock.hide()
        ###effect for adock_button button
        if self.windows.adockZn_button.underMouse():
            self.windows.comment_adockZn.show()
        else:
            self.windows.comment_adockZn.hide()
        ###effect for vina_result
        if self.windows.results_button.underMouse():
            self.windows.comment_results.show()
        else:
            self.windows.comment_results.hide()
    ###rounded corner
    def hex2QColor(self,c):
        """Convert Hex color to QColor"""
        r = int(c[0:2], 16)
        g = int(c[2:4], 16)
        b = int(c[4:6], 16)
        return QtGui.QColor(r, g, b)
    def paintEvent(self, event):
        # get current window size
        s = self.size()
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        #qp.setPen(self.foregroundColor)
        qp.setBrush(self.backgroundColor)
        qp.drawRoundedRect(0, 0, s.width(), s.height(), self.borderRadius, self.borderRadius)
        qp.end()

        ###mouse events
    def mousePressEvent(self, event):
        if self.draggable and event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()  # global
            self.__mouseMovePos = event.globalPos() - self.pos()  # local
        super(AMDock, self).mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if self.draggable and event.buttons() & QtCore.Qt.LeftButton:
            globalPos = event.globalPos()
            moved = globalPos - self.__mousePressPos
            if moved.manhattanLength() > self.dragging_threshould:
                # move when user drag window more than dragging_threshould
                diff = globalPos - self.__mouseMovePos
                self.move(diff)
                self.__mouseMovePos = globalPos - self.pos()
        super(AMDock, self).mouseMoveEvent(event)
