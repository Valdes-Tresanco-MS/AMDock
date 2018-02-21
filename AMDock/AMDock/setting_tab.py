import multiprocessing, os, time, re
from PyQt4 import QtGui, QtCore
from some_slots import values
from log_window import LogWindow

class Configuration_tab(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Configuration_tab, self).__init__(parent)
        self.setObjectName("configuration_tab")
        self.parent = parent

        font1 = QtGui.QFont()
        font1.setPointSize(9)

        path = os.path.split(__file__)[0]
        self.config = os.path.join(path, 'configuration.ini')

        self.initial_config()

        self.log_view = QtGui.QCheckBox(self)
        self.log_view.setGeometry(QtCore.QRect(380, 10, 140, 20))
        self.log_view.setChecked(False)
        self.log_view.setObjectName("log_view")
        self.log_view.setText("View Log Window")

        self.save = QtGui.QPushButton(self)
        self.save.setGeometry(QtCore.QRect(740,5,150,30))
        self.save.setText('Save Configuration in File')
        self.save.setFont(font1)

        self.reset = QtGui.QPushButton(self)
        self.reset.setGeometry(QtCore.QRect(10, 5, 150, 30))
        self.reset.setText('Set Default Configuration')
        self.reset.setFont(font1)

        self.pdb2pqr_box = QtGui.QGroupBox(self)
        self.pdb2pqr_box.setGeometry(QtCore.QRect(10, 45, 880, 50))
        self.pdb2pqr_box.setTitle('PDB2PQR Configuration')

        self.ff_label = QtGui.QLabel(self.pdb2pqr_box)
        self.ff_label.setGeometry(QtCore.QRect(15,20,65,22))
        self.ff_label.setText('Force Field: ')
        self.ff_label.setFont(font1)

        self.amber = QtGui.QRadioButton(self.pdb2pqr_box)
        self.amber.setGeometry(QtCore.QRect(100,20,70,22))
        self.amber.setText('AMBER')
        self.amber.setFont(font1)

        self.charmm = QtGui.QRadioButton(self.pdb2pqr_box)
        self.charmm.setGeometry(QtCore.QRect(180, 20, 80, 22))
        self.charmm.setText('CHARMM')
        self.charmm.setFont(font1)

        self.parse = QtGui.QRadioButton(self.pdb2pqr_box)
        self.parse.setGeometry(QtCore.QRect(270, 20, 65, 22))
        self.parse.setText('PARSE')
        self.parse.setFont(font1)

        self.tyl06 = QtGui.QRadioButton(self.pdb2pqr_box)
        self.tyl06.setGeometry(QtCore.QRect(350, 20, 60, 22))
        self.tyl06.setText('TYL06')
        self.tyl06.setFont(font1)

        self.peoepb = QtGui.QRadioButton(self.pdb2pqr_box)
        self.peoepb.setGeometry(QtCore.QRect(430, 20, 70, 22))
        self.peoepb.setText('PEOEPB')
        self.peoepb.setFont(font1)

        self.swanson = QtGui.QRadioButton(self.pdb2pqr_box)
        self.swanson.setGeometry(QtCore.QRect(520, 20, 83, 22))
        self.swanson.setText('SWANSON')
        self.swanson.setFont(font1)

        self.ff = QtGui.QButtonGroup (self.pdb2pqr_box)
        self.ff.addButton(self.amber, 1)
        self.ff.addButton(self.charmm, 2)
        self.ff.addButton(self.parse, 3)
        self.ff.addButton(self.tyl06, 4)
        self.ff.addButton(self.peoepb, 5)
        self.ff.addButton(self.swanson, 6)

        # self.pdb2pqr_config_help = QtGui.QPushButton(self.pdb2pqr_box)
        # self.pdb2pqr_config_help.setGeometry(QtCore.QRect(855, 18, 22, 22))
        # font = QtGui.QFont()
        # font.setPointSize(10)
        # self.pdb2pqr_config_help.setFont(font)
        # self.pdb2pqr_config_help.setObjectName("pdb2pqr_config_help")
        # self.pdb2pqr_config_help.setText("?")

        self.ff.buttonClicked[QtGui.QAbstractButton].connect(self.ff_sel)

        self.vina_config_box = QtGui.QGroupBox(self)
        self.vina_config_box.setGeometry(QtCore.QRect(10, 105, 880, 71))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.vina_config_box.setFont(font)
        self.vina_config_box.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.vina_config_box.setObjectName("vina_config_box")
        self.vina_config_box.setTitle("Vina Configuration")

        self.cpu_perf = QtGui.QLabel(self.vina_config_box)
        self.cpu_perf.setGeometry(QtCore.QRect(10, 25, 100, 22))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(True)
        self.cpu_perf.setFont(font)
        self.cpu_perf.setObjectName("cpu_perf")
        self.cpu_perf.setText("CPU Performance")
        self.number_cpu = multiprocessing.cpu_count()

        self.horizontalSlider = QtGui.QSlider(self.vina_config_box)
        self.horizontalSlider.setGeometry(QtCore.QRect(120, 22, 141, 22))
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setMaximum(self.number_cpu)
        self.horizontalSlider.setValue(self.cpu)

        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setTickInterval(5)
        self.horizontalSlider.setObjectName("horizontalSlider")

        self.cpu_label = QtGui.QLabel(self.vina_config_box)
        self.cpu_label.setGeometry(QtCore.QRect(10, 50, 300, 22))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.cpu_label.setFont(font)
        self.cpu_label.setObjectName("cpu_label")
        self.cpu_label.setText("%s" % self.horizontalSlider.value() + " CPU in use of %s" % self.number_cpu)

        self.low_perf = QtGui.QLabel(self.vina_config_box)
        self.low_perf.setGeometry(QtCore.QRect(120, 35, 31, 22))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.low_perf.setFont(font)
        self.low_perf.setObjectName("low_perf")
        self.low_perf.setText("Low")

        self.high_perf = QtGui.QLabel(self.vina_config_box)
        self.high_perf.setGeometry(QtCore.QRect(243, 35, 31, 22))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.high_perf.setFont(font)
        self.high_perf.setObjectName("high_perf")
        self.high_perf.setText("High")

        self.exh = QtGui.QLabel(self.vina_config_box)
        self.exh.setGeometry(QtCore.QRect(300, 30, 100, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.exh.setFont(font)
        self.exh.setObjectName("exh")
        self.exh.setText("Exhaustiveness")

        self.exh_value = QtGui.QSpinBox(self.vina_config_box)
        self.exh_value.setGeometry(QtCore.QRect(410, 30, 51, 22))
        self.exh_value.setObjectName("exh_value")
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.exh_value.setFont(font)
        self.exh_value.setAlignment(QtCore.Qt.AlignCenter)
        self.exh_value.setMinimum(8)
        self.exh_value.setMaximum(56)
        self.exh_value.setSingleStep(8)

        self.nposes = QtGui.QLabel(self.vina_config_box)
        self.nposes.setGeometry(QtCore.QRect(505, 30, 100, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.nposes.setFont(font)
        self.nposes.setObjectName("nposes")
        self.nposes.setText("Number of Poses")

        self.nposes_value = QtGui.QSpinBox(self.vina_config_box)
        self.nposes_value.setGeometry(QtCore.QRect(610, 30, 51, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        self.nposes_value.setFont(font)
        self.nposes_value.setAlignment(QtCore.Qt.AlignCenter)
        self.nposes_value.setMinimum(1.0)
        self.nposes_value.setMaximum(20.0)
        self.nposes_value.setSingleStep(1.0)
        self.nposes_value.setObjectName("nposes_value")

        # self.vina_config_help = QtGui.QPushButton(self.vina_config_box)
        # self.vina_config_help.setGeometry(QtCore.QRect(855, 30, 22, 22))
        # font = QtGui.QFont()
        # font.setPointSize(10)
        # self.vina_config_help.setFont(font)
        # self.vina_config_help.setObjectName("vina_config_help")
        # self.vina_config_help.setText("?")

        self.AD4_config_box = QtGui.QGroupBox(self)
        self.AD4_config_box.setGeometry(QtCore.QRect(10, 185, 880, 71))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.AD4_config_box.setFont(font)
        self.AD4_config_box.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.AD4_config_box.setObjectName("AD4_config_box")
        self.AD4_config_box.setTitle("AutoDock4 Configuration")

        self.neval = QtGui.QLabel(self.AD4_config_box)
        self.neval.setGeometry(QtCore.QRect(10, 30, 130, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        # font.setBold(True)
        self.neval.setFont(font)
        self.neval.setObjectName("neval")
        self.neval.setText("Energy Evaluations")

        self.neval_value = QtGui.QSpinBox(self.AD4_config_box)
        self.neval_value.setGeometry(QtCore.QRect(150, 30, 90, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        self.neval_value.setFont(font)
        self.neval_value.setAlignment(QtCore.Qt.AlignCenter)
        self.neval_value.setMinimum(200000)
        self.neval_value.setMaximum(10000000)
        self.neval_value.setSingleStep(100000)
        self.neval_value.setObjectName("nposes_value")

        self.nruns = QtGui.QLabel(self.AD4_config_box)
        self.nruns.setGeometry(QtCore.QRect(300, 30, 100, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        # font.setBold(True)
        self.nruns.setFont(font)
        self.nruns.setObjectName("nruns")
        self.nruns.setText("Number of Runs")

        self.nruns_value = QtGui.QSpinBox(self.AD4_config_box)
        self.nruns_value.setGeometry(QtCore.QRect(405, 30, 50, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        self.nruns_value.setFont(font)
        self.nruns_value.setAlignment(QtCore.Qt.AlignCenter)
        self.nruns_value.setMinimum(1)
        self.nruns_value.setMaximum(1000)
        self.nruns_value.setSingleStep(1)
        self.nruns_value.setObjectName("nruns_value")

        self.rmstol_label = QtGui.QLabel(self.AD4_config_box)
        self.rmstol_label.setGeometry(QtCore.QRect(500, 30, 105, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        # font.setBold(True)
        self.rmstol_label.setFont(font)
        self.rmstol_label.setObjectName("rmstol")
        self.rmstol_label.setText("Cluster Tolerance")

        self.rmstol_value = QtGui.QDoubleSpinBox(self.AD4_config_box)
        self.rmstol_value.setGeometry(QtCore.QRect(610, 30, 51, 22))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        self.rmstol_value.setFont(font)
        self.rmstol_value.setAlignment(QtCore.Qt.AlignCenter)
        self.rmstol_value.setDecimals(1)
        self.rmstol_value.setMinimum(0.5)
        self.rmstol_value.setMaximum(3.0)
        self.rmstol_value.setSingleStep(0.5)
        self.rmstol_value.setObjectName("rmstol_value")

        # self.AD_config_help = QtGui.QPushButton(self.AD4_config_box)
        # self.AD_config_help.setGeometry(QtCore.QRect(855, 30, 22, 22))
        # font = QtGui.QFont()
        # font.setPointSize(10)
        # self.AD_config_help.setFont(font)
        # self.AD_config_help.setObjectName("AD4_config_help")
        # self.AD_config_help.setText("?")

        self.conf_from_file()

        self.log_wdw = LogWindow(self)

        self.horizontalSlider.valueChanged.connect(lambda: self.values(self.horizontalSlider))
        self.nposes_value.valueChanged.connect(lambda: self.values(self.nposes_value))
        self.exh_value.valueChanged.connect(lambda: self.values(self.exh_value))
        self.neval_value.valueChanged.connect(lambda: self.values(self.neval_value))
        self.nruns_value.valueChanged.connect(lambda: self.values(self.nruns_value))
        self.rmstol_value.valueChanged.connect(lambda: self.values(self.rmstol_value))
        self.save.clicked.connect(self.configuration)
        self.reset.clicked.connect(self.set_default)

    def conf_from_file(self):
        for button in self.ff.buttons():
            if self.forcefield == button.text():
                button.setChecked(True)

        self.exh_value.setProperty('value', self.exhaustiveness)
        self.nposes_value.setProperty('value', self.NoPoses)
        self.neval_value.setProperty('value', self.ga_num_eval)
        self.nruns_value.setProperty('value', self.ga_run)
        self.rmstol_value.setProperty('value', self.rmstol)
        if self.log == 'False':
            self.log_view.setChecked(False)
        else:
            self.log_view.setChecked(True)
    def values(self, k):  # ok
        if k.objectName() == 'horizontalSlider':
            self.parent.v.ncpu = self.horizontalSlider.value()
            self.cpu_label.setText("%s" % self.parent.v.ncpu + " CPU in use of %s" % self.number_cpu)
        elif k.objectName() == 'nposes_value':
            self.parent.v.poses_vina = self.nposes_value.value()
        elif k.objectName() == "exh_value":
            self.parent.v.exhaustiveness = self.exh_value.value()
        elif k.objectName() == 'neval':
            self.parent.v.eval = self.neval_value.value()
        elif k.objectName() == 'nruns_value':
            self.parent.v.runs = self.nruns_value.value()
        elif k.objectName() == 'rmstol_value':
            self.parent.v.rmsd = self.rmstol_value.value()
    def ff_sel(self,btn):
        self.forcefield = btn.text()
    def data_view(self, cb):
        if cb.isChecked():
            self.log_wdw.show()
    def configuration(self):
        path = os.path.split(__file__)[0]
        config = os.path.join(path,'configuration.ini')
        msg =self.parent.statusbar.currentMessage()
        self.parent.statusbar.clearMessage()
        self.parent.statusbar.showMessage('Wrote configuration file',5000)
        config_file = open(config, 'w')
        config_file.write('################################################################################\n'
                          '#                           AMDOCK CONFIGURATION FILE                          #\n'
                          '################################################################################\n')
        config_file.write('[PDB2PQR]\n')
        config_file.write('ff %s\n' % self.forcefield)
        config_file.write('[VINA]\n')
        config_file.write('cpu %s\n' % self.horizontalSlider.value())
        config_file.write('exhaustiveness %s\n' % self.exh_value.value())
        config_file.write('NoPoses %s\n' % self.nposes_value.value())
        config_file.write('[AD4]\n')
        config_file.write('ga_num_eval %s\n' % self.neval_value.value())
        config_file.write('ga_run %s\n' % self.nruns_value.value())
        config_file.write('rmstol %s\n' % self.rmstol_value.value())
        config_file.write('[LOG]\n')
        config_file.write('log %s\n' % self.log_view.isChecked())
        config_file.close()
        time.sleep(3)
        self.parent.statusbar.showMessage(msg)
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
                    self.forcefield = line.split()[1]
                elif re.search('cpu', line):
                    self.cpu = int(line.split()[1])
                    self.parent.v.ncpu = self.cpu
                elif re.search('exhaustiveness', line):
                    self.exhaustiveness = int(line.split()[1])
                    self.parent.v.exhaustiveness = self.exhaustiveness
                elif re.search('NoPoses', line):
                    self.NoPoses = int(line.split()[1])
                    self.parent.v.poses_vina = self.NoPoses
                elif re.search('Vina_Spacing', line):
                    self.vina_spacing = float(line.split()[1])
                elif re.search('ga_num_eval', line):
                    self.ga_num_eval = int(line.split()[1])
                    self.parent.v.eval = self.ga_num_eval
                elif re.search('ga_run', line):
                    self.ga_run = int(line.split()[1])
                    self.parent.v.runs = self.ga_run
                elif re.search('rmstol', line):
                    self.rmstol = float(line.split()[1])
                    self.parent.v.rmsd = self.rmstol
                elif re.search('log', line):
                    self.log = line.split()[1]
        cfile.close()
