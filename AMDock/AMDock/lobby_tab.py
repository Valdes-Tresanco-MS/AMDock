from PyQt4 import QtGui, QtCore
import os
from variables import Objects
#
# class Label(QtGui.QWidget):
#     def __init__(self, parent=None):
#         QtGui.QWidget.__init__(self, parent=parent)
#         self.p = QtGui.QPixmap()
#
#     def setPixmap(self, p):
#         self.p = p
#         self.update()
#
#     def paintEvent(self, event):
#         if not self.p.isNull():
#             painter = QtGui.QPainter(self)
#             painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
#             painter.drawPixmap(self.rect(), self.p)

class Lobby(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent

        # with open(self.parent.objects.style_file) as f:
        #     self.setStyleSheet(f.read())

        # font = QtGui.QFont()
        # font.setFamily("Arial")
        # font.setPointSize(10)
        # font.setBold(True)
        # font.setWeight(75)
        # font.setKerning(True)


        # self.setGeometry(QtCore.QRect(0, 35, 900, 648))
        # self.setFont(font)
        # self.setMouseTracking(True)
        # self.setTabPosition(QtGui.QTabWidget.North)
        # self.setTabShape(QtGui.QTabWidget.Rounded)
        # self.setIconSize(QtCore.QSize(30, 22))
        self.setObjectName("tab_lobby")
        print self.parent.objects
    
        loc = os.path.join(os.path.dirname(__file__), 'images', 'presentation.png')
        style = '#tab_lobby {background-image: url(%s) 0 0 0 0 stretch stretch;}' % Objects().presentation
        # self.setStyleSheet('background-image: url(file://images/presentation.png); 0 0 0 0 stretch stretch;')
        # self.setStyleSheet('background-color: black;')

        # self.picture = Label(self)
        # self.picture.setPixmap(QtGui.QPixmap(loc))

        self.contentwidget = QtGui.QWidget()

        self.dock_vina_button = QtGui.QPushButton(self.contentwidget)
        self.dock_vina_button.setGeometry(QtCore.QRect(15, 35, 165, 70))
        self.dock_vina_button.setObjectName("dock_vina_button")
        self.dock_vina_button.setText("Autodock Vina")
        self.dock_vina_button.clicked.connect(lambda: self.program_select(self.dock_vina_button))

        self.adock_button = QtGui.QPushButton(self.contentwidget)
        self.adock_button.setGeometry(QtCore.QRect(195, 35, 165, 70))
        self.adock_button.setObjectName("adock_button")
        self.adock_button.setText("Autodock4")
        self.adock_button.clicked.connect(lambda: self.program_select(self.adock_button))

        self.adockZn_button = QtGui.QPushButton(self.contentwidget)
        self.adockZn_button.setGeometry(QtCore.QRect(375, 35, 165, 70))
        self.adockZn_button.setObjectName("adockZn_button")
        self.adockZn_button.setText("Autodock4Zn")
        self.adockZn_button.clicked.connect(lambda: self.program_select(self.adockZn_button))

        self.results_button = QtGui.QPushButton(self.contentwidget)
        self.results_button.setGeometry(QtCore.QRect(620, 35, 200, 70))
        self.results_button.setObjectName("results_button")
        self.results_button.setText("Analize Results")
        self.results_button.clicked.connect(lambda: self.result_select(self.results_button))

        self.comment_vina_dock = QtGui.QLabel(self.contentwidget)
        self.comment_vina_dock.setGeometry(QtCore.QRect(15, 103, 165, 60))
        self.comment_vina_dock.setLineWidth(10)
        self.comment_vina_dock.setScaledContents(True)
        self.comment_vina_dock.setWordWrap(True)
        self.comment_vina_dock.setMargin(2)
        self.comment_vina_dock.setIndent(5)
        self.comment_vina_dock.setObjectName("comment_vina_dock")
        self.comment_vina_dock.setText("1-Molecular Docking Simulation\n2-Cross Docking with \n     Autodock Vina.")

        self.comment_adock = QtGui.QLabel(self.contentwidget)
        self.comment_adock.setGeometry(QtCore.QRect(195, 103, 165, 60))
        self.comment_adock.setLineWidth(10)
        self.comment_adock.setScaledContents(True)
        self.comment_adock.setWordWrap(True)
        self.comment_adock.setMargin(2)
        self.comment_adock.setIndent(5)
        self.comment_adock.setObjectName("comment_adock")
        self.comment_adock.setText("1-Molecular Docking Simulation\n2-Cross Docking with\n     Autodock4.")

        self.comment_adockZn = QtGui.QLabel(self.contentwidget)
        self.comment_adockZn.setGeometry(QtCore.QRect(375, 103, 165, 60))
        self.comment_adockZn.setLineWidth(10)
        self.comment_adockZn.setScaledContents(True)
        self.comment_adockZn.setWordWrap(True)
        self.comment_adockZn.setMargin(2)
        self.comment_adockZn.setIndent(5)
        self.comment_adockZn.setObjectName("comment_adockZn")
        self.comment_adockZn.setText("1-Molecular Docking Simulation\n2-Cross Docking with\n     Autodock4Zn.")

        self.comment_results = QtGui.QLabel(self.contentwidget)
        self.comment_results.setGeometry(QtCore.QRect(620, 103, 200, 60))
        self.comment_results.setLineWidth(10)
        self.comment_results.setScaledContents(True)
        self.comment_results.setWordWrap(True)
        self.comment_results.setMargin(2)
        self.comment_results.setIndent(5)
        self.comment_results.setObjectName("comment_results")
        self.comment_results.setText("Analyze Results")

        self.spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.lobby_layout = QtGui.QGridLayout(self)
        # self.lobby_layout.addItem(self.spacer, 0, 0, 0, -1)
        self.lobby_layout.addWidget(self.contentwidget, 1, 1)
        # self.lobby_layout.addItem(self.spacer, 0, 2, 0, -1)
        # self



        # self.addTab(self, self.icon, '')

        #### detect hover mouse event
        self.timer12 = QtCore.QTimer(self)
        self.timer12.start(10)
        self.timer12.timeout.connect(self.Hover)

    def Hover(self):
        ''' change propety of object'''
        ###effect for vina_dock button
        if self.dock_vina_button.underMouse():
            self.comment_vina_dock.show()
        else:
            self.comment_vina_dock.hide()
        ### effect for adock button
        if self.adock_button.underMouse():
            self.comment_adock.show()
        else:
            self.comment_adock.hide()
        ###effect for adock_button button
        if self.adockZn_button.underMouse():
            self.comment_adockZn.show()
        else:
            self.comment_adockZn.hide()
        ###effect for vina_result
        if self.results_button.underMouse():
            self.comment_results.show()
        else:
            self.comment_results.hide()
        

    def program_select(self, b):
        if b.objectName() == 'adock_button':
            self.parent.v.docking_program = 'AutoDock4'
        elif b.objectName() == 'adockZn_button':
            self.parent.v.docking_program = 'AutoDockZn'
        elif b.objectName() == 'dock_vina_button':
            self.parent.v.docking_program = 'AutoDock Vina'
        self.parent.statusbar.showMessage(self.parent.v.docking_program + " is selected")
        self.parent.windows.setCurrentIndex(1)
        self.parent.windows.setTabEnabled(1, True)
        self.parent.windows.setTabEnabled(0, False)

    def result_select(self, b):
        if b.objectName() == 'vina_result_button':
            self.parent.statusbar.showMessage(b.text() + " is selected")
        else:
            self.parent.statusbar.showMessage(b.text() + " is selected")
        self.parent.windows.setCurrentIndex(2)
        self.parent.windows.setTabEnabled(1, False)
        self.parent.windows.setTabEnabled(0, False)
        self.parent.windows.setTabEnabled(2, True)
