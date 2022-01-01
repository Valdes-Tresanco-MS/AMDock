from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class LogWindow(QDockWidget):
    def __init__(self, parent=None):
        QDockWidget.__init__(self, parent)
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.AMDock = parent
        self.splitter = QSplitter(Qt.Vertical)
        self.list_view = QTreeWidget()
        self.list_view.setColumnCount(2)
        self.list_view.header().setSectionResizeMode(QHeaderView.Stretch)
        # self.list_view.setHeaderLabels(['Step', 'State'])
        self.list_view.setHeaderHidden(True)

        # items list
        self.dp = QTreeWidgetItem(self.list_view, ['Docking Program'])

        self.pf = QTreeWidgetItem(self.list_view, ['Project'])

        self.inp = QTreeWidgetItem(self.list_view, ['Input Files'])
        self.target = QTreeWidgetItem(self.inp, ['Target'])
        # self.tpdb2pqr = QTreeWidgetItem(self.target, ['PDB2PQR'])
        # self.tfix = QTreeWidgetItem(self.target, ['Fix PDB'])
        # self.tprepare = QTreeWidgetItem(self.target, ['Prepare Receptor'])

        self.offtarget = QTreeWidgetItem(self.inp, ['Off-Target'])
        # self.opdb2pqr = QTreeWidgetItem(self.offtarget, ['PDB2PQR'])
        # self.ofix = QTreeWidgetItem(self.offtarget, ['Fix PDB'])
        # self.oprepare = QTreeWidgetItem(self.offtarget, ['Prepare Receptor'])

        self.ligand = QTreeWidgetItem(self.inp, ['Ligand'])
        # self.lpdb2pqr = QTreeWidgetItem(self.ligand, ['Obabel'])
        # self.lprepare = QTreeWidgetItem(self.ligand, ['Prepare Ligand'])

        self.ss = QTreeWidgetItem(self.list_view, ['Search Space'])
        self.target = QTreeWidgetItem(self.ss, ['Target'])
        # self.tgpf = QTreeWidgetItem(self.target, ['Prepare GPF'])
        # self.tfix = QTreeWidgetItem(self.target, ['Fix PDB'])
        # self.tprepare = QTreeWidgetItem(self.target, ['Prepare Receptor'])

        self.offtarget = QTreeWidgetItem(self.ss, ['Off-Target'])
        # self.opdb2pqr = QTreeWidgetItem(self.offtarget, ['PDB2PQR'])
        # self.ofix = QTreeWidgetItem(self.offtarget, ['Fix PDB'])
        # self.oprepare = QTreeWidgetItem(self.offtarget, ['Prepare Receptor'])
        self.md = QTreeWidgetItem(self.list_view, ['Docking'])
        self.target = QTreeWidgetItem(self.md, ['Target'])
        self.offtarget = QTreeWidgetItem(self.md, ['Off-Target'])

        # for x in range(self.list_view.topLevelItemCount()):
        #     print self.list_view.itemAt(x)

        font = QFont('Courier New')
        # font.setPointSize(10)
        font.setKerning(False)
        self.textedit = QTextEdit(self)
        self.textedit.setMinimumWidth(500)
        self.textedit.setReadOnly(True)
        self.textedit.setLineWrapMode(QTextEdit.NoWrap)
        self.textedit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.textedit.setFont(font)
        self.textedit.ensureCursorVisible()
        self.textedit.append('Welcome to AMDock\nVersion %s\n' % self.AMDock.version)
        self.textedit.textChanged.connect(self.jump)
        # layout.addWidget(self.textedit)
        # self.parent.log_view.stateChanged.connect(lambda: self.ch_state(self.parent.log_view))
        # self.finished.connect(self.closed)
        # if self.parent.log_view.isChecked():
        #     self.show()

        # self.setLayout(layout)
        # self.splitter.addWidget(self.list_view)
        # self.splitter.addWidget(self.textedit)
        # self.splitter.setStretchFactor(1, 10)
        self.save = QPushButton('Save')
        self.save.clicked.connect(self.file_save)
        self.clear = QPushButton('Clear')
        self.clear.clicked.connect(self.clear_log)
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addStretch(1)
        self.btn_layout.addWidget(self.save)
        self.btn_layout.addWidget(self.clear)
        self.btn_layout.addStretch(1)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.addWidget(self.textedit, 1)
        self.container_layout.addLayout(self.btn_layout)

        # self.setWidget(self.splitter)
        # self.setWidget(self.textedit)
        self.setWidget(self.container)

    def file_save(self):
        if self.AMDock.project.log:
            wfile = open(self.AMDock.project.log, 'w')
            text = self.textedit.toPlainText()
            wfile.write(text)
            wfile.close()
        else:
            name = QFileDialog.getSaveFileName(self.AMDock, 'Save File', '.', "Log *.log")
            if name:
                file = open(name, 'w')
                text = self.textedit.toPlainText()
                file.write(text)
                file.close()

    def clear_log(self):
        msg = QMessageBox.warning(self.AMDock, 'Warning', 'This Log contains important information. Do you '
                                                                'really want to delete it?', QMessageBox.Yes |
                                        QMessageBox.No)
        if msg == QMessageBox.Yes:
            self.textedit.clear()
            self.textedit.append('Welcome to AMDock\nVersion %s\n' % self.AMDock.version)

    def jump(self):
        self.textedit.verticalScrollBar().setValue(self.textedit.verticalScrollBar().maximum())

    def ch_state(self, st):
        if st.isChecked() is False:
            self.close()
        else:
            self.show()
