import multiprocessing, os, time, re
from PyQt4 import QtGui, QtCore
from log_window import LogWindow


class Configuration_tab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Configuration_tab, self).__init__(parent)
        self.setObjectName("configuration_tab")
        self.parent = parent

        path = os.path.split(__file__)[0]
        self.config = os.path.join(path, 'configuration.ini')

        self.initial_config()

        self.check_timer = QtCore.QTimer()
        self.check_timer.timeout.connect(self.check_changes)
        self.check_timer.start(15)

        self.log_view = QtGui.QCheckBox(self)
        self.log_view.setObjectName("log_view")
        self.log_view.setText("View Log Window")
        self.log_view.setFixedWidth(200)

        self.save = QtGui.QPushButton(self)
        self.save.setText('Save Configuration in File')

        self.reset = QtGui.QPushButton(self)
        self.reset.setText('Set Default Configuration')

        self.pdb2pqr_box = QtGui.QGroupBox(self)
        self.pdb2pqr_box.setTitle('PDB2PQR Configuration')

        self.ff_label = QtGui.QLabel(self.pdb2pqr_box)
        self.ff_label.setText('Force Field: ')

        self.amber = QtGui.QRadioButton(self.pdb2pqr_box)
        self.amber.setText('AMBER')

        self.charmm = QtGui.QRadioButton(self.pdb2pqr_box)
        self.charmm.setText('CHARMM')

        self.parse = QtGui.QRadioButton(self.pdb2pqr_box)
        self.parse.setText('PARSE')

        self.tyl06 = QtGui.QRadioButton(self.pdb2pqr_box)
        self.tyl06.setText('TYL06')

        self.peoepb = QtGui.QRadioButton(self.pdb2pqr_box)
        self.peoepb.setText('PEOEPB')

        self.swanson = QtGui.QRadioButton(self.pdb2pqr_box)
        self.swanson.setText('SWANSON')

        self.ff = QtGui.QButtonGroup(self.pdb2pqr_box)
        self.ff.addButton(self.amber, 1)
        self.ff.addButton(self.charmm, 2)
        self.ff.addButton(self.parse, 3)
        self.ff.addButton(self.tyl06, 4)
        self.ff.addButton(self.peoepb, 5)
        self.ff.addButton(self.swanson, 6)

        self.ff.buttonClicked[QtGui.QAbstractButton].connect(self.ff_sel)

        self.vina_config_box = QtGui.QGroupBox(self)
        self.vina_config_box.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.vina_config_box.setObjectName("vina_config_box")
        self.vina_config_box.setTitle("Vina Configuration")

        self.cpu_perf = QtGui.QLabel(self.vina_config_box)
        self.cpu_perf.setObjectName("cpu_perf")
        self.cpu_perf.setText("CPU Performance")
        self.number_cpu = multiprocessing.cpu_count()

        self.horizontalSlider = QtGui.QSlider(self.vina_config_box)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setMaximum(self.number_cpu)
        self.horizontalSlider.setValue(self.parent.v.ncpu)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setTickInterval(5)
        self.horizontalSlider.setObjectName("horizontalSlider")

        self.cpu_label = QtGui.QLabel(self.vina_config_box)
        self.cpu_label.setObjectName("cpu_label")
        self.cpu_label.setText("%s" % self.parent.v.ncpu + " CPU in use of %s" % self.number_cpu)

        self.low_perf = QtGui.QLabel(self.vina_config_box)
        self.low_perf.setObjectName("low_perf")
        self.low_perf.setText("Low")

        self.high_perf = QtGui.QLabel(self.vina_config_box)
        self.high_perf.setObjectName("high_perf")
        self.high_perf.setText("High")

        self.exh = QtGui.QLabel(self.vina_config_box)
        self.exh.setObjectName("exh")
        self.exh.setText("Exhaustiveness")

        self.exh_value = QtGui.QSpinBox(self.vina_config_box)
        self.exh_value.setObjectName("exh_value")
        self.exh_value.setAlignment(QtCore.Qt.AlignCenter)
        self.exh_value.setMinimum(8)
        self.exh_value.setMaximum(56)
        self.exh_value.setSingleStep(8)

        self.nposes = QtGui.QLabel(self.vina_config_box)
        self.nposes.setObjectName("nposes")
        self.nposes.setText("Number of Poses")

        self.nposes_value = QtGui.QSpinBox(self.vina_config_box)
        self.nposes_value.setAlignment(QtCore.Qt.AlignCenter)
        self.nposes_value.setMinimum(1.0)
        self.nposes_value.setMaximum(20.0)
        self.nposes_value.setSingleStep(1.0)
        self.nposes_value.setObjectName("nposes_value")

        self.AD4_config_box = QtGui.QGroupBox(self)
        self.AD4_config_box.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.AD4_config_box.setObjectName("AD4_config_box")
        self.AD4_config_box.setTitle("AutoDock4 Configuration")

        self.neval = QtGui.QLabel(self.AD4_config_box)
        self.neval.setObjectName("neval")
        self.neval.setText("Energy Evaluations")

        self.neval_value = QtGui.QSpinBox(self.AD4_config_box)
        self.neval_value.setAlignment(QtCore.Qt.AlignCenter)
        self.neval_value.setMinimum(200000)
        self.neval_value.setMaximum(10000000)
        self.neval_value.setSingleStep(100000)
        self.neval_value.setObjectName("nposes_value")

        self.nruns = QtGui.QLabel(self.AD4_config_box)
        self.nruns.setObjectName("nruns")
        self.nruns.setText("Number of Runs")

        self.nruns_value = QtGui.QSpinBox(self.AD4_config_box)
        self.nruns_value.setAlignment(QtCore.Qt.AlignCenter)
        self.nruns_value.setMinimum(1)
        self.nruns_value.setMaximum(1000)
        self.nruns_value.setSingleStep(1)
        self.nruns_value.setObjectName("nruns_value")

        self.rmstol_label = QtGui.QLabel(self.AD4_config_box)
        self.rmstol_label.setObjectName("rmstol")
        self.rmstol_label.setText("Cluster Tolerance")

        self.rmstol_value = QtGui.QDoubleSpinBox(self.AD4_config_box)
        self.rmstol_value.setAlignment(QtCore.Qt.AlignCenter)
        self.rmstol_value.setDecimals(1)
        self.rmstol_value.setMinimum(0.5)
        self.rmstol_value.setMaximum(3.0)
        self.rmstol_value.setSingleStep(0.5)
        self.rmstol_value.setObjectName("rmstol_value")

        self.misc_box = QtGui.QGroupBox(self)
        self.misc_box.setTitle('Miscellaneous Configuration')

        self.align = QtGui.QCheckBox(self.misc_box)
        self.align.setChecked(True)
        self.align.setObjectName("align")
        self.align.setText("Proteins superposition in off-target docking")

        self.unsaved_config = QtGui.QLabel(self)
        self.unsaved_config.setText('Some parameters were modified!!!\nTo take effect, please save this configuration '
                                    'options.')
        font10 = QtGui.QFont()
        font10.setPointSize(20)
        font10.setWeight(100)
        self.unsaved_config.setFont(font10)
        self.unsaved_config.setStyleSheet('background-color : white; color : red; ')
        self.unsaved_config.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        self.unsaved_config.hide()

        self.conf_from_file()

        self.cpu = self.horizontalSlider.value()
        self.NoPoses = self.nposes_value.value()
        self.exhaustiveness = self.exh_value.value()
        self.ga_num_eval = self.neval_value.value()
        self.ga_run = self.nruns_value.value()
        self.rmstol = self.rmstol_value.value()
        self.forcefield = self.ff.checkedButton().text()
        self.alignment = self.align.isChecked()

        self.log_wdw = LogWindow(self)

        self.init_button_layout = QtGui.QHBoxLayout()
        self.init_button_layout.addWidget(self.save)
        self.init_button_layout.addStretch(1)
        self.init_button_layout.addWidget(self.log_view, QtCore.Qt.AlignCenter)
        self.init_button_layout.addStretch(1)
        self.init_button_layout.addWidget(self.reset)

        self.pdb2pqr_box_layout = QtGui.QHBoxLayout(self.pdb2pqr_box)
        self.pdb2pqr_box_layout.addWidget(self.ff_label)
        self.pdb2pqr_box_layout.addWidget(self.amber)
        self.pdb2pqr_box_layout.addWidget(self.charmm)
        self.pdb2pqr_box_layout.addWidget(self.parse)
        self.pdb2pqr_box_layout.addWidget(self.tyl06)
        self.pdb2pqr_box_layout.addWidget(self.peoepb)
        self.pdb2pqr_box_layout.addWidget(self.swanson)

        self.vina_slide_layout = QtGui.QHBoxLayout()
        self.vina_slide_layout.addWidget(self.low_perf)
        self.vina_slide_layout.addWidget(self.horizontalSlider)
        self.vina_slide_layout.addWidget(self.high_perf)

        self.vina_proc_layout = QtGui.QVBoxLayout()
        self.vina_proc_layout.addLayout(self.vina_slide_layout)
        self.vina_proc_layout.addWidget(self.cpu_label)

        self.vina_config_box_layout = QtGui.QHBoxLayout(self.vina_config_box)
        self.vina_config_box_layout.addWidget(self.cpu_perf)
        self.vina_config_box_layout.addLayout(self.vina_proc_layout)
        self.vina_config_box_layout.addStretch(1)
        self.vina_config_box_layout.addWidget(self.exh)
        self.vina_config_box_layout.addWidget(self.exh_value)
        self.vina_config_box_layout.addStretch(1)
        self.vina_config_box_layout.addWidget(self.nposes)
        self.vina_config_box_layout.addWidget(self.nposes_value)

        self.ad4_layout = QtGui.QHBoxLayout(self.AD4_config_box)
        self.ad4_layout.addWidget(self.neval)
        self.ad4_layout.addWidget(self.neval_value)
        self.ad4_layout.addStretch(1)
        self.ad4_layout.addWidget(self.nruns)
        self.ad4_layout.addWidget(self.nruns_value)
        self.ad4_layout.addStretch(1)
        self.ad4_layout.addWidget(self.rmstol_label)
        self.ad4_layout.addWidget(self.rmstol_value)

        self.misc_box_layout = QtGui.QHBoxLayout(self.misc_box)
        self.misc_box_layout.addWidget(self.align)

        self.conf_tab_layout = QtGui.QVBoxLayout(self)
        self.conf_tab_layout.addLayout(self.init_button_layout)
        self.conf_tab_layout.addWidget(self.pdb2pqr_box)
        self.conf_tab_layout.addWidget(self.vina_config_box)
        self.conf_tab_layout.addWidget(self.AD4_config_box)
        self.conf_tab_layout.addWidget(self.misc_box)
        self.conf_tab_layout.addStretch(1)
        self.conf_tab_layout.addWidget(self.unsaved_config)
        self.conf_tab_layout.addStretch(1)

        self.horizontalSlider.valueChanged.connect(lambda: self.values(self.horizontalSlider))
        self.nposes_value.valueChanged.connect(lambda: self.values(self.nposes_value))
        self.exh_value.valueChanged.connect(lambda: self.values(self.exh_value))
        self.neval_value.valueChanged.connect(lambda: self.values(self.neval_value))
        self.nruns_value.valueChanged.connect(lambda: self.values(self.nruns_value))
        self.rmstol_value.valueChanged.connect(lambda: self.values(self.rmstol_value))
        self.align.clicked.connect(self._align)
        self.save.clicked.connect(self.configuration)
        self.reset.clicked.connect(self.set_default)

    def conf_from_file(self):
        for button in self.ff.buttons():
            if self.parent.v.forcefield == button.text():
                button.setChecked(True)

        self.exh_value.setProperty('value', self.parent.v.exhaustiveness)
        self.nposes_value.setProperty('value', self.parent.v.poses_vina)
        self.neval_value.setProperty('value', self.parent.v.eval)
        self.nruns_value.setProperty('value', self.parent.v.runs)
        self.rmstol_value.setProperty('value', self.parent.v.rmsd)
        self.horizontalSlider.setProperty('value', self.parent.v.ncpu)
        self.log_view.setChecked(self.parent.v.log)
        self.align.setChecked(self.parent.v.prot_align)

    def values(self, k):  # ok
        if k.objectName() == 'horizontalSlider':
            self.cpu = self.horizontalSlider.value()
            self.cpu_label.setText("%s" % self.cpu + " CPU in use of %s" % self.number_cpu)
        elif k.objectName() == 'nposes_value':
            self.NoPoses = self.nposes_value.value()
        elif k.objectName() == "exh_value":
            self.exhaustiveness = self.exh_value.value()
        elif k.objectName() == 'neval':
            self.ga_num_eval = self.neval_value.value()
        elif k.objectName() == 'nruns_value':
            self.ga_run = self.nruns_value.value()
        elif k.objectName() == 'rmstol_value':
            self.rmstol = self.rmstol_value.value()

    def _align(self):
        self.alignment = self.align.isChecked()

    def ff_sel(self, btn):
        self.forcefield = btn.text()

    def data_view(self, cb):
        if cb.isChecked():
            self.log_wdw.show()

    def configuration(self):
        path = os.path.split(__file__)[0]
        config = os.path.join(path, 'configuration.ini')
        msg = self.parent.statusbar.currentMessage()
        self.parent.statusbar.clearMessage()
        self.parent.statusbar.showMessage('Wrote configuration file', 5000)
        config_file = open(config, 'w')
        config_file.write('################################################################################\n'
                          '#                           AMDOCK CONFIGURATION FILE                          #\n'
                          '################################################################################\n')
        config_file.write('[PDB2PQR]\n')
        config_file.write('ff %s\n' % self.forcefield)
        config_file.write('[VINA]\n')
        config_file.write('cpu %s\n' % self.cpu)
        config_file.write('exhaustiveness %s\n' % self.exhaustiveness)
        config_file.write('NoPoses %s\n' % self.NoPoses)
        config_file.write('[AD4]\n')
        config_file.write('ga_num_eval %s\n' % self.ga_num_eval)
        config_file.write('ga_run %s\n' % self.ga_run)
        config_file.write('rmstol %s\n' % self.rmstol)
        config_file.write('[LOG]\n')
        config_file.write('log %s\n' % self.log_view.isChecked())
        config_file.write('[MISC]\n')
        config_file.write('prot_align %s\n' % self.align.isChecked())
        config_file.close()
        time.sleep(3)
        self.parent.statusbar.showMessage(msg)
        self.initial_config()

    def set_default(self):
        self.default()
        self.initial_config()
        self.conf_from_file()

    def default(self):
        config_file = open(self.config, 'w')
        config_file.write('################################################################################\n'
                          '#                           AMDOCK CONFIGURATION FILE                          #\n'
                          '################################################################################\n')
        config_file.write('[PDB2PQR]\n')
        config_file.write('ff AMBER\n')
        config_file.write('[VINA]\n')
        config_file.write('cpu 1\n')
        config_file.write('exhaustiveness 8\n')
        config_file.write('NoPoses 10\n')
        config_file.write('[AD4]\n')
        config_file.write('ga_num_eval 2500000\n')
        config_file.write('ga_run 10\n')
        config_file.write('rmstol 2.0\n')
        config_file.write('[LOG]\n')
        config_file.write('log False\n')
        config_file.write('[MISC]\n')
        config_file.write('prot_align True')
        config_file.close()

    def initial_config(self):
        if not os.path.exists(self.config):
            self.default()
        cfile = open(self.config, 'r')
        for line in cfile:
            line = line.strip('\n')
            if re.search('#', line) or re.search('\[', line):
                continue
            else:
                if re.search('ff', line):
                    self.parent.v.forcefield = line.split()[1]
                elif re.search('cpu', line):
                    self.parent.v.ncpu = int(line.split()[1])
                elif re.search('exhaustiveness', line):
                    self.parent.v.exhaustiveness = int(line.split()[1])
                elif re.search('NoPoses', line):
                    self.parent.v.poses_vina = int(line.split()[1])
                elif re.search('ga_num_eval', line):
                    self.parent.v.eval = int(line.split()[1])
                elif re.search('ga_run', line):
                    self.parent.v.runs = int(line.split()[1])
                elif re.search('rmstol', line):
                    self.parent.v.rmsd = float(line.split()[1])
                elif re.search('log', line):
                    if line.split()[1] == 'False':
                        self.parent.v.log = False
                    else:
                        self.parent.v.log = True
                elif re.search('prot_align', line):
                    if line.split()[1] == 'False':
                        self.parent.v.prot_align = False
                    else:
                        self.parent.v.prot_align = True
                try:
                    self.align.setChecked(self.parent.v.prot_align)
                except:
                    pass
        cfile.close()

    def check_changes(self):
        '''check if you saved the configuration '''
        if self.cpu != self.parent.v.ncpu or self.exhaustiveness != self.parent.v.exhaustiveness or self.NoPoses != \
                self.parent.v.poses_vina or self.forcefield != self.parent.v.forcefield or self.ga_run != self.parent.v.runs \
                or self.ga_num_eval != self.parent.v.eval or self.rmstol != self.parent.v.rmsd or self.alignment != self.parent.v.prot_align:
            self.unsaved_config.show()
        else:
            self.unsaved_config.hide()
