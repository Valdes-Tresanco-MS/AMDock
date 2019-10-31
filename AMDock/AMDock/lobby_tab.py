from PyQt4 import QtGui, QtCore
from variables import Objects


class FRAME(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent=parent)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(self.rect(), QtGui.QPixmap(Objects.presentation))
        QtGui.QFrame.paintEvent(self, event)


class Lobby(FRAME):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.parent = parent
        self.setObjectName("tab_lobby")
        self.dock_vina_button = QtGui.QPushButton(self)
        self.dock_vina_button.setObjectName("dock_vina_button")
        self.dock_vina_button.setMinimumSize(180, 70)
        self.dock_vina_button.setMaximumSize(180, 70)
        self.dock_vina_button.setText("Autodock Vina")
        self.dock_vina_button.clicked.connect(lambda: self.program_select(self.dock_vina_button))

        self.adock_button = QtGui.QPushButton(self)
        self.adock_button.setMinimumSize(180, 70)
        self.adock_button.setMaximumSize(180, 70)
        self.adock_button.setObjectName("adock_button")
        self.adock_button.setText("Autodock4")
        self.adock_button.clicked.connect(lambda: self.program_select(self.adock_button))
        self.adock_button.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.adockZn_button = QtGui.QPushButton(self)
        self.adockZn_button.setMinimumSize(180, 70)
        self.adockZn_button.setMaximumSize(180, 70)
        self.adockZn_button.setObjectName("adockZn_button")
        self.adockZn_button.setText("Autodock4Zn")
        self.adockZn_button.clicked.connect(lambda: self.program_select(self.adockZn_button))
        self.adockZn_button.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.results_button = QtGui.QPushButton(self)
        self.results_button.setMinimumSize(180, 70)
        self.results_button.setMaximumSize(180, 70)
        self.results_button.setObjectName("results_button")
        self.results_button.setText("Analize Results")
        self.results_button.clicked.connect(lambda: self.result_select(self.results_button))
        self.results_button.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.comment_vina_dock = QtGui.QLabel(self)
        self.comment_vina_dock.setMinimumSize(180, 60)
        self.comment_vina_dock.setMaximumSize(180, 60)
        self.comment_vina_dock.setLineWidth(10)
        self.comment_vina_dock.setScaledContents(True)
        self.comment_vina_dock.setWordWrap(True)
        self.comment_vina_dock.setMargin(2)
        self.comment_vina_dock.setIndent(5)
        self.comment_vina_dock.setObjectName("comment_vina_dock")
        self.comment_vina_dock.setText("1-Molecular Docking Simulation\n2-Cross Docking with \n     Autodock Vina.")

        self.comment_adock = QtGui.QLabel(self)
        self.comment_adock.setMinimumSize(180, 60)
        self.comment_adock.setMaximumSize(180, 60)
        self.comment_adock.setLineWidth(10)
        self.comment_adock.setScaledContents(True)
        self.comment_adock.setWordWrap(True)
        self.comment_adock.setMargin(2)
        self.comment_adock.setIndent(5)
        self.comment_adock.setObjectName("comment_adock")
        self.comment_adock.setText("1-Molecular Docking Simulation\n2-Cross Docking with\n     Autodock4.")

        self.comment_adockZn = QtGui.QLabel(self)
        self.comment_adockZn.setMinimumSize(180, 60)
        self.comment_adockZn.setMaximumSize(180, 60)
        self.comment_adockZn.setLineWidth(10)
        self.comment_adockZn.setScaledContents(True)
        self.comment_adockZn.setWordWrap(True)
        self.comment_adockZn.setMargin(2)
        self.comment_adockZn.setIndent(5)
        self.comment_adockZn.setObjectName("comment_adockZn")
        self.comment_adockZn.setText("1-Molecular Docking Simulation\n2-Cross Docking with\n     Autodock4Zn.")

        self.comment_results = QtGui.QLabel(self)
        self.comment_results.setMinimumSize(180, 60)
        self.comment_results.setMaximumSize(180, 60)
        self.comment_results.setLineWidth(10)
        self.comment_results.setScaledContents(True)
        self.comment_results.setWordWrap(True)
        self.comment_results.setMargin(2)
        self.comment_results.setIndent(5)
        self.comment_results.setObjectName("comment_results")
        self.comment_results.setText("Analyze Results")

        self.spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.buttons_layout = QtGui.QHBoxLayout()

        self.vina_layout = QtGui.QVBoxLayout()
        self.vina_layout.addWidget(self.dock_vina_button)
        self.vina_layout.addWidget(self.comment_vina_dock)
        self.vina_layout.setSpacing(0)

        self.adock_layout = QtGui.QVBoxLayout()
        self.adock_layout.addWidget(self.adock_button)
        self.adock_layout.addWidget(self.comment_adock)
        self.adock_layout.setSpacing(0)

        self.adockzn_layout = QtGui.QVBoxLayout()
        self.adockzn_layout.addWidget(self.adockZn_button)
        self.adockzn_layout.addWidget(self.comment_adockZn)
        self.adockzn_layout.setSpacing(0)

        self.result_layout = QtGui.QVBoxLayout()
        self.result_layout.addWidget(self.results_button)
        self.result_layout.addWidget(self.comment_results)
        self.result_layout.setSpacing(0)

        self.cont_layout = QtGui.QHBoxLayout()
        self.cont_layout.addStretch(2)
        self.cont_layout.addLayout(self.vina_layout, 1)
        self.cont_layout.addStretch(1)
        self.cont_layout.addLayout(self.adock_layout, 1)
        self.cont_layout.addStretch(1)
        self.cont_layout.addLayout(self.adockzn_layout, 1)
        self.cont_layout.addStretch(3)
        self.cont_layout.addLayout(self.result_layout, 1)
        self.cont_layout.addStretch(6)

        self.lobby_layout = QtGui.QVBoxLayout(self)
        self.lobby_layout.addStretch(2)
        self.lobby_layout.addLayout(self.cont_layout)
        self.lobby_layout.addStretch(10)

        self.timer12 = QtCore.QTimer(self)
        self.timer12.start(10)
        self.timer12.timeout.connect(self.Hover)

    def Hover(self):
        ''' change propety of object'''
        if self.dock_vina_button.underMouse():
            self.comment_vina_dock.show()
        else:
            self.comment_vina_dock.hide()
        if self.adock_button.underMouse():
            self.comment_adock.show()
        else:
            self.comment_adock.hide()
        if self.adockZn_button.underMouse():
            self.comment_adockZn.show()
        else:
            self.comment_adockZn.hide()
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
        self.parent.statusbar.addWidget(QtGui.QLabel("| " + self.parent.v.docking_program + " is selected"))
        self.parent.main_window.setCurrentIndex(1)
        self.parent.main_window.setTabEnabled(1, True)
        self.parent.main_window.setTabEnabled(0, False)

    def result_select(self, b):
        if b.objectName() == 'vina_result_button':
            self.parent.statusbar.showMessage(b.text() + " is selected")
        else:
            self.parent.statusbar.showMessage(b.text() + " is selected")
        self.parent.main_window.setCurrentIndex(2)
        self.parent.main_window.setTabEnabled(1, False)
        self.parent.main_window.setTabEnabled(0, False)
        self.parent.main_window.setTabEnabled(2, True)
