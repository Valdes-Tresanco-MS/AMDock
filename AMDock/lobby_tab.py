from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from AMDock.tools import FormatedText as Ft

class Lobby(QFrame):
    def __init__(self, parent=None):
        super(Lobby, self).__init__(parent)
        self.AMDock = parent
        self.setObjectName("tab_lobby")
        self.dock_vina_button = QPushButton(self)
        self.dock_vina_button.setObjectName("dock_vina_button")
        self.dock_vina_button.setMinimumSize(180, 70)
        self.dock_vina_button.setMaximumSize(180, 70)
        self.dock_vina_button.setText("Autodock Vina")
        self.dock_vina_button.clicked.connect(lambda: self.program_select(self.dock_vina_button))

        self.adock_button = QPushButton(self)
        self.adock_button.setMinimumSize(180, 70)
        self.adock_button.setMaximumSize(180, 70)
        self.adock_button.setObjectName("adock_button")
        self.adock_button.setText("Autodock4")
        self.adock_button.clicked.connect(lambda: self.program_select(self.adock_button))
        self.adock_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.adockZn_button = QPushButton(self)
        self.adockZn_button.setMinimumSize(180, 70)
        self.adockZn_button.setMaximumSize(180, 70)
        self.adockZn_button.setObjectName("adockZn_button")
        self.adockZn_button.setText("Autodock4Zn")
        self.adockZn_button.clicked.connect(lambda: self.program_select(self.adockZn_button))
        self.adockZn_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.results_button = QPushButton(self)
        self.results_button.setMinimumSize(180, 70)
        self.results_button.setMaximumSize(180, 70)
        self.results_button.setObjectName("results_button")
        self.results_button.setText("Analize Results")
        self.results_button.clicked.connect(self.result_select)
        self.results_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.comment_vina_dock = QLabel(self)
        self.comment_vina_dock.setMinimumSize(180, 60)
        # self.comment_vina_dock.setMaximumSize(180, 60)
        self.comment_vina_dock.setLineWidth(10)
        # self.comment_vina_dock.setScaledContents(True)
        # self.comment_vina_dock.setWordWrap(True)
        self.comment_vina_dock.setMargin(5)
        self.comment_vina_dock.setIndent(5)
        self.comment_vina_dock.setObjectName("comment_vina_dock")
        self.comment_vina_dock.setText("1-Molecular Docking\n2-Off-Target Docking with \n     AutoDock "
                                       "Vina.\n3-Scoring")

        self.comment_adock = QLabel(self)
        self.comment_adock.setMinimumSize(180, 60)
        # self.comment_adock.setMaximumSize(180, 60)
        self.comment_adock.setLineWidth(10)
        # self.comment_adock.setScaledContents(True)
        # self.comment_adock.setWordWrap(True)
        self.comment_adock.setMargin(5)
        self.comment_adock.setIndent(5)
        self.comment_adock.setObjectName("comment_adock")
        self.comment_adock.setText("1-Molecular Docking\n2-Off-Target Docking with\n     AutoDock4.\n3-Scoring")

        self.comment_adockZn = QLabel(self)
        self.comment_adockZn.setMinimumSize(180, 60)
        # self.comment_adockZn.setMaximumSize(180, 60)
        self.comment_adockZn.setLineWidth(10)
        # self.comment_adockZn.setScaledContents(True)
        # self.comment_adockZn.setWordWrap(True)
        self.comment_adockZn.setMargin(5)
        self.comment_adockZn.setIndent(5)
        self.comment_adockZn.setObjectName("comment_adockZn")
        self.comment_adockZn.setText("1-Molecular Docking\n2-Off-Target Docking with\n     AutoDock4Zn.\n3-Scoring")

        self.comment_results = QLabel(self)
        self.comment_results.setMinimumSize(180, 60)
        # self.comment_results.setMaximumSize(180, 60)
        self.comment_results.setLineWidth(10)
        self.comment_results.setScaledContents(True)
        self.comment_results.setWordWrap(True)
        self.comment_results.setMargin(2)
        self.comment_results.setIndent(5)
        self.comment_results.setObjectName("comment_results")
        self.comment_results.setText("Analyze Results")

        self.spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.buttons_layout = QHBoxLayout()

        self.vina_layout = QVBoxLayout()
        self.vina_layout.addWidget(self.dock_vina_button)
        self.vina_layout.addWidget(self.comment_vina_dock)
        self.vina_layout.setSpacing(0)

        self.adock_layout = QVBoxLayout()
        self.adock_layout.addWidget(self.adock_button)
        self.adock_layout.addWidget(self.comment_adock)
        self.adock_layout.setSpacing(0)

        self.adockzn_layout = QVBoxLayout()
        self.adockzn_layout.addWidget(self.adockZn_button)
        self.adockzn_layout.addWidget(self.comment_adockZn)
        self.adockzn_layout.setSpacing(0)

        self.result_layout = QVBoxLayout()
        self.result_layout.addWidget(self.results_button)
        self.result_layout.addWidget(self.comment_results)
        self.result_layout.setSpacing(0)

        self.cont_layout = QHBoxLayout()
        self.cont_layout.addStretch(2)
        self.cont_layout.addLayout(self.vina_layout, 1)
        self.cont_layout.addStretch(1)
        self.cont_layout.addLayout(self.adock_layout, 1)
        self.cont_layout.addStretch(1)
        self.cont_layout.addLayout(self.adockzn_layout, 1)
        self.cont_layout.addStretch(3)
        self.cont_layout.addLayout(self.result_layout, 1)
        self.cont_layout.addStretch(6)

        self.lobby_layout = QVBoxLayout(self)
        self.lobby_layout.addStretch(1)
        self.lobby_layout.addLayout(self.cont_layout)
        self.lobby_layout.addStretch(10)

        self.timer12 = QTimer(self)
        self.timer12.start(10)
        self.timer12.timeout.connect(self.hover)

    def hover(self):
        """ change propety of object"""
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
            self.AMDock.docking_program = 'AutoDock4'
            self.AMDock.program_body.new_para_btn.show()
            self.AMDock.program_body.new_para_text.show()
        elif b.objectName() == 'adockZn_button':
            self.AMDock.docking_program = 'AutoDockZn'
            self.AMDock.program_body.new_para_btn.show()
            self.AMDock.program_body.new_para_text.show()
        elif b.objectName() == 'dock_vina_button':
            self.AMDock.docking_program = 'AutoDock Vina'
            self.AMDock.program_body.new_para_btn.hide()
            self.AMDock.program_body.new_para_text.hide()
        self.AMDock.mess = QLabel(self.AMDock.docking_program + " is selected")
        self.AMDock.statusbar.addWidget(self.AMDock.mess)
        self.AMDock.log_widget.textedit.append(Ft('Defining Initial Parameters...').section())
        self.AMDock.log_widget.textedit.append(Ft('DOCKING_PROGRAM: %s' % self.AMDock.docking_program).definitions())
        self.AMDock.main_window.setCurrentIndex(1)
        self.AMDock.main_window.setTabEnabled(1, True)
        self.AMDock.main_window.setTabEnabled(0, False)

    def result_select(self):
        self.AMDock.statusbar.showMessage("Analyze Results is selected")
        self.AMDock.main_window.setCurrentIndex(2)
        self.AMDock.main_window.setTabEnabled(1, False)
        self.AMDock.main_window.setTabEnabled(0, False)
        self.AMDock.main_window.setTabEnabled(2, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), QPixmap(self.AMDock.presentation))
        QFrame.paintEvent(self, event)