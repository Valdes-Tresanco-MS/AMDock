from PyQt4 import QtGui, QtCore


class LogWindow(QtGui.QDockWidget):
    def __init__(self, parent=None):
        QtGui.QDockWidget.__init__(self, parent)
        self.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.AMDock = parent
        self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.list_view = QtGui.QTreeWidget()
        self.list_view.setColumnCount(2)
        self.list_view.header().setResizeMode(QtGui.QHeaderView.Stretch)
        # self.list_view.setHeaderLabels(['Step', 'State'])
        self.list_view.setHeaderHidden(True)

        # items list
        self.dp = QtGui.QTreeWidgetItem(self.list_view, ['Docking Program'])

        self.pf = QtGui.QTreeWidgetItem(self.list_view, ['Project'])

        self.inp = QtGui.QTreeWidgetItem(self.list_view, ['Input Files'])
        self.target = QtGui.QTreeWidgetItem(self.inp, ['Target'])
        # self.tpdb2pqr = QtGui.QTreeWidgetItem(self.target, ['PDB2PQR'])
        # self.tfix = QtGui.QTreeWidgetItem(self.target, ['Fix PDB'])
        # self.tprepare = QtGui.QTreeWidgetItem(self.target, ['Prepare Receptor'])

        self.offtarget = QtGui.QTreeWidgetItem(self.inp, ['Off-Target'])
        # self.opdb2pqr = QtGui.QTreeWidgetItem(self.offtarget, ['PDB2PQR'])
        # self.ofix = QtGui.QTreeWidgetItem(self.offtarget, ['Fix PDB'])
        # self.oprepare = QtGui.QTreeWidgetItem(self.offtarget, ['Prepare Receptor'])

        self.ligand = QtGui.QTreeWidgetItem(self.inp, ['Ligand'])
        # self.lpdb2pqr = QtGui.QTreeWidgetItem(self.ligand, ['Obabel'])
        # self.lprepare = QtGui.QTreeWidgetItem(self.ligand, ['Prepare Ligand'])

        self.ss = QtGui.QTreeWidgetItem(self.list_view, ['Search Space'])
        self.target = QtGui.QTreeWidgetItem(self.ss, ['Target'])
        # self.tgpf = QtGui.QTreeWidgetItem(self.target, ['Prepare GPF'])
        # self.tfix = QtGui.QTreeWidgetItem(self.target, ['Fix PDB'])
        # self.tprepare = QtGui.QTreeWidgetItem(self.target, ['Prepare Receptor'])

        self.offtarget = QtGui.QTreeWidgetItem(self.ss, ['Off-Target'])
        # self.opdb2pqr = QtGui.QTreeWidgetItem(self.offtarget, ['PDB2PQR'])
        # self.ofix = QtGui.QTreeWidgetItem(self.offtarget, ['Fix PDB'])
        # self.oprepare = QtGui.QTreeWidgetItem(self.offtarget, ['Prepare Receptor'])
        self.md = QtGui.QTreeWidgetItem(self.list_view, ['Docking'])
        self.target = QtGui.QTreeWidgetItem(self.md, ['Target'])
        self.offtarget = QtGui.QTreeWidgetItem(self.md, ['Off-Target'])

        # for x in range(self.list_view.topLevelItemCount()):
        #     print self.list_view.itemAt(x)

        font = QtGui.QFont('Courier New')
        # font.setPointSize(10)
        font.setKerning(False)
        self.textedit = QtGui.QTextEdit(self)
        self.textedit.setMinimumWidth(500)
        self.textedit.ensureCursorVisible()
        self.textedit.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.textedit.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.textedit.setFont(font)
        self.textedit.setReadOnly(True)
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
        self.save = QtGui.QPushButton('Save')
        self.save.clicked.connect(self.file_save)
        self.clear = QtGui.QPushButton('Clear')
        self.clear.clicked.connect(self.clear_log)
        self.btn_layout = QtGui.QHBoxLayout()
        self.btn_layout.addStretch(1)
        self.btn_layout.addWidget(self.save)
        self.btn_layout.addWidget(self.clear)
        self.btn_layout.addStretch(1)

        self.container = QtGui.QWidget()
        self.container_layout = QtGui.QVBoxLayout(self.container)
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
            name = QtGui.QFileDialog.getSaveFileName(self.AMDock, 'Save File', '.', "Log *.log")
            if name:
                file = open(name, 'w')
                text = self.textEdit.toPlainText()
                file.write(text)
                file.close()

    def clear_log(self):
        msg = QtGui.QMessageBox.warning(self.AMDock, 'Warning', 'This Log contains important information. Do you '
                                                                'really want to delete it?', QtGui.QMessageBox.Yes |
                                        QtGui.QMessageBox.No)
        if msg == QtGui.QMessageBox.Yes:
            self.textedit.clear()
            self.textedit.append('Welcome to AMDock\nVersion %s\n' % self.AMDock.version)

    def jump(self):
        self.textedit.verticalScrollBar().setValue(self.textedit.verticalScrollBar().maximum())

    def ch_state(self, st):
        if st.isChecked() is False:
            self.close()
        else:
            self.show()
