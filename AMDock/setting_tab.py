import multiprocessing
import os
import re
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Configuration_tab(QWidget):
    def __init__(self, parent=None):
        super(Configuration_tab, self).__init__(parent)
        self.setObjectName("configuration_tab")
        self.AMDock = parent

        self.config = self.AMDock.config_file

        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_changes)
        self.check_timer.start(500)

        self.pdb2pqr_box = QGroupBox(self)
        self.pdb2pqr_box.setTitle('PDB2PQR Configuration')

        self.ff_label = QLabel(self.pdb2pqr_box)
        self.ff_label.setText('Force Field: ')

        self.amber = QRadioButton(self.pdb2pqr_box)
        self.amber.setText('AMBER')

        self.charmm = QRadioButton(self.pdb2pqr_box)
        self.charmm.setText('CHARMM')

        self.parse = QRadioButton(self.pdb2pqr_box)
        self.parse.setText('PARSE')

        self.tyl06 = QRadioButton(self.pdb2pqr_box)
        self.tyl06.setText('TYL06')

        self.peoepb = QRadioButton(self.pdb2pqr_box)
        self.peoepb.setText('PEOEPB')

        self.swanson = QRadioButton(self.pdb2pqr_box)
        self.swanson.setText('SWANSON')

        self.ff = QButtonGroup(self.pdb2pqr_box)
        self.ff.addButton(self.amber, 1)
        self.ff.addButton(self.charmm, 2)
        self.ff.addButton(self.parse, 3)
        self.ff.addButton(self.tyl06, 4)
        self.ff.addButton(self.peoepb, 5)
        self.ff.addButton(self.swanson, 6)

        self.ff.buttonClicked[QAbstractButton].connect(self.ff_sel)

        self.save = QPushButton(self)
        self.save.setText('Save Configuration in File')

        self.reset = QPushButton(self)
        self.reset.setText('Set Default Configuration')

        self.vina_config_box = QGroupBox(self)
        self.vina_config_box.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.vina_config_box.setObjectName("vina_config_box")
        self.vina_config_box.setTitle("Vina Configuration")

        self.cpu_perf = QLabel(self.vina_config_box)
        self.cpu_perf.setObjectName("cpu_perf")
        self.cpu_perf.setText("CPU Performance")
        self.number_cpu = multiprocessing.cpu_count()

        self.horizontalSlider = QSlider(self.vina_config_box)
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setMaximum(self.number_cpu)
        self.horizontalSlider.setOrientation(Qt.Horizontal)
        self.horizontalSlider.setTickInterval(5)
        self.horizontalSlider.setObjectName("horizontalSlider")

        self.cpu_label = QLabel(self.vina_config_box)
        self.cpu_label.setObjectName("cpu_label")

        self.low_perf = QLabel(self.vina_config_box)
        self.low_perf.setObjectName("low_perf")
        self.low_perf.setText("Low")

        self.high_perf = QLabel(self.vina_config_box)
        self.high_perf.setObjectName("high_perf")
        self.high_perf.setText("High")

        self.exh = QLabel(self.vina_config_box)
        self.exh.setObjectName("exh")
        self.exh.setText("Exhaustiveness")

        self.exh_value = QSpinBox(self.vina_config_box)
        self.exh_value.setObjectName("exh_value")
        self.exh_value.setAlignment(Qt.AlignCenter)
        self.exh_value.setMinimum(8)
        self.exh_value.setMaximum(56)
        self.exh_value.setSingleStep(8)

        self.nposes = QLabel(self.vina_config_box)
        self.nposes.setObjectName("nposes")
        self.nposes.setText("Number of Poses")

        self.nposes_value = QSpinBox(self.vina_config_box)
        self.nposes_value.setAlignment(Qt.AlignCenter)
        self.nposes_value.setMinimum(1.0)
        self.nposes_value.setMaximum(20.0)
        self.nposes_value.setSingleStep(1.0)
        self.nposes_value.setObjectName("nposes_value")

        self.AD4_config_box = QGroupBox(self)
        self.AD4_config_box.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.AD4_config_box.setObjectName("AD4_config_box")
        self.AD4_config_box.setTitle("AutoDock4 Configuration")

        self.neval = QLabel(self.AD4_config_box)
        self.neval.setObjectName("neval")
        self.neval.setText("Energy Evaluations")

        self.neval_value = QSpinBox(self.AD4_config_box)
        self.neval_value.setAlignment(Qt.AlignCenter)
        self.neval_value.setMinimum(200000)
        self.neval_value.setMaximum(10000000)
        self.neval_value.setSingleStep(100000)
        self.neval_value.setObjectName("neval_value")

        self.nruns = QLabel(self.AD4_config_box)
        self.nruns.setObjectName("nruns")
        self.nruns.setText("Number of Runs")

        self.nruns_value = QSpinBox(self.AD4_config_box)
        self.nruns_value.setAlignment(Qt.AlignCenter)
        self.nruns_value.setMinimum(1)
        self.nruns_value.setMaximum(1000)
        self.nruns_value.setSingleStep(1)
        self.nruns_value.setObjectName("nruns_value")

        self.rmstol_label = QLabel(self.AD4_config_box)
        self.rmstol_label.setObjectName("rmstol")
        self.rmstol_label.setText("Cluster Tolerance")

        self.rmstol_value = QDoubleSpinBox(self.AD4_config_box)
        self.rmstol_value.setAlignment(Qt.AlignCenter)
        self.rmstol_value.setDecimals(1)
        self.rmstol_value.setMinimum(0.5)
        self.rmstol_value.setMaximum(3.0)
        self.rmstol_value.setSingleStep(0.5)
        self.rmstol_value.setObjectName("rmstol_value")

        self.log_config = QGroupBox('Log')

        self.log_view = QCheckBox(self)
        self.log_view.setObjectName("log_view")
        self.log_view.setText("View Log Window")
        self.log_view.setFixedWidth(200)

        self.log_min = QRadioButton('Only actions')
        self.log_max = QRadioButton('All output')
        self.log_max.setChecked(True)
        self.log_output_group = QGroupBox('Output')

        self.log_group = QButtonGroup()
        self.log_group.addButton(self.log_min, 1)
        self.log_group.addButton(self.log_max, 2)
        self.log_group.buttonClicked.connect(self.log_level_sel)
        self.log_output_layout = QHBoxLayout(self.log_output_group)
        self.log_output_layout.addWidget(self.log_min)
        self.log_output_layout.addWidget(self.log_max)

        self.log_layout = QHBoxLayout(self.log_config)
        self.log_layout.addWidget(self.log_view)
        self.log_layout.addWidget(self.log_output_group)

        self.protonation_config = QGroupBox('Protonation')

        self.protonation_view = QCheckBox(self)
        self.protonation_view.setObjectName("protonation")
        self.protonation_view.setText("Ligand Protonation")
        self.protonation_view.setFixedWidth(200)

        self.openbabel = QRadioButton('OpenBabel')
        self.openbabel.setChecked(True)
        self.adtools = QRadioButton('AutoDockTools')
        self.program_group = QGroupBox('Program')

        self.prog_group = QButtonGroup()
        self.prog_group.addButton(self.openbabel, 1)
        self.prog_group.addButton(self.adtools, 2)
        self.prog_group.buttonClicked.connect(self.prot_prog_sel)
        self.prot_prog_layout = QHBoxLayout(self.program_group)
        self.prot_prog_layout.addWidget(self.openbabel)
        self.prot_prog_layout.addWidget(self.adtools)

        self.prto_layout = QHBoxLayout(self.protonation_config)
        self.prto_layout.addWidget(self.protonation_view)
        self.prto_layout.addWidget(self.program_group)

        self.unsaved_config = QLabel(self)
        self.unsaved_config.setText('Some parameters were modified!\n'
                                    'If you want you can save these settings permanently.')
        font10 = QFont()
        font10.setPointSize(16)
        font10.setWeight(200)
        self.unsaved_config.setFont(font10)
        self.unsaved_config.setStyleSheet('background-color : white; color : red; ')
        self.unsaved_config.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.unsaved_config.hide()

        self.init_button_layout = QHBoxLayout()
        self.init_button_layout.addWidget(self.save)
        self.init_button_layout.addStretch(1)
        self.init_button_layout.addWidget(self.reset)

        self.pdb2pqr_box_layout = QHBoxLayout(self.pdb2pqr_box)
        self.pdb2pqr_box_layout.addWidget(self.ff_label)
        self.pdb2pqr_box_layout.addWidget(self.amber)
        self.pdb2pqr_box_layout.addWidget(self.charmm)
        self.pdb2pqr_box_layout.addWidget(self.parse)
        self.pdb2pqr_box_layout.addWidget(self.tyl06)
        self.pdb2pqr_box_layout.addWidget(self.peoepb)
        self.pdb2pqr_box_layout.addWidget(self.swanson)

        self.vina_slide_layout = QHBoxLayout()
        self.vina_slide_layout.addWidget(self.low_perf)
        self.vina_slide_layout.addWidget(self.horizontalSlider)
        self.vina_slide_layout.addWidget(self.high_perf)

        self.vina_proc_layout = QVBoxLayout()
        self.vina_proc_layout.addLayout(self.vina_slide_layout)
        self.vina_proc_layout.addWidget(self.cpu_label)

        self.vina_config_box_layout = QHBoxLayout(self.vina_config_box)
        self.vina_config_box_layout.addWidget(self.cpu_perf)
        self.vina_config_box_layout.addLayout(self.vina_proc_layout)
        self.vina_config_box_layout.addStretch(1)
        self.vina_config_box_layout.addWidget(self.exh)
        self.vina_config_box_layout.addWidget(self.exh_value)
        self.vina_config_box_layout.addStretch(1)
        self.vina_config_box_layout.addWidget(self.nposes)
        self.vina_config_box_layout.addWidget(self.nposes_value)

        self.ad4_layout = QHBoxLayout(self.AD4_config_box)
        self.ad4_layout.addWidget(self.neval)
        self.ad4_layout.addWidget(self.neval_value)
        self.ad4_layout.addStretch(1)
        self.ad4_layout.addWidget(self.nruns)
        self.ad4_layout.addWidget(self.nruns_value)
        self.ad4_layout.addStretch(1)
        self.ad4_layout.addWidget(self.rmstol_label)
        self.ad4_layout.addWidget(self.rmstol_value)

        self.conf_tab_layout = QVBoxLayout(self)
        self.conf_tab_layout.addLayout(self.init_button_layout)
        self.conf_tab_layout.addWidget(self.pdb2pqr_box)
        self.conf_tab_layout.addWidget(self.vina_config_box)
        self.conf_tab_layout.addWidget(self.AD4_config_box)
        self.conf_tab_layout.addWidget(self.log_config)
        self.conf_tab_layout.addWidget(self.protonation_config)
        self.conf_tab_layout.addStretch(1)
        self.conf_tab_layout.addWidget(self.unsaved_config)
        self.conf_tab_layout.addStretch(1)

        self.initial_config()
        self.conf_from_file()

        self.horizontalSlider.valueChanged.connect(lambda: self.values(self.horizontalSlider))
        self.nposes_value.valueChanged.connect(lambda: self.values(self.nposes_value))
        self.exh_value.valueChanged.connect(lambda: self.values(self.exh_value))
        self.neval_value.valueChanged.connect(lambda: self.values(self.neval_value))
        self.nruns_value.valueChanged.connect(lambda: self.values(self.nruns_value))
        self.rmstol_value.valueChanged.connect(lambda: self.values(self.rmstol_value))
        self.log_view.stateChanged.connect(self.log_control)
        self.save.clicked.connect(self.configuration)
        self.reset.clicked.connect(self.set_default)

    def ff_sel(self, btn):
        self.AMDock.forcefield = btn.text()

    def log_control(self, state):
        if state:
            self.AMDock.log = True
            self.AMDock.log_widget.show()
        else:
            self.AMDock.log = False
            self.AMDock.log_widget.close()

    def conf_from_file(self):
        for button in self.ff.buttons():
            if self.AMDock.forcefield == button.text():
                button.setChecked(True)
        self.cpu_label.setText("%s" % self.AMDock.ncpu + " CPU in use of %s" % self.number_cpu)
        self.horizontalSlider.setValue(self.AMDock.ncpu)
        self.exh_value.setValue(self.AMDock.exhaustiveness)
        self.nposes_value.setValue(self.AMDock.poses_vina)
        self.neval_value.setValue(self.AMDock.ga_num_eval)
        self.nruns_value.setValue(self.AMDock.ga_run)
        self.rmstol_value.setValue(self.AMDock.rmsdtol)
        self.horizontalSlider.setValue(self.AMDock.ncpu)
        self.log_view.setChecked(self.AMDock.log)
        self.log_group.button(self.AMDock.log_level).setChecked(True)
        self.protonation_view.setChecked(self.AMDock.protonation)
        if self.AMDock.protonation_program == 'obabel':
            self.prog_group.button(1).setChecked(True)
        else:
            self.prog_group.button(2).setChecked(True)

    def values(self, k):  # ok
        if k.objectName() == 'horizontalSlider':
            self.AMDock.ncpu = self.horizontalSlider.value()
            self.cpu_label.setText("%s" % self.AMDock.ncpu + " CPU in use of %s" % self.number_cpu)
        elif k.objectName() == 'nposes_value':
            self.AMDock.poses_vina = self.nposes_value.value()
        elif k.objectName() == "exh_value":
            self.AMDock.exhaustiveness = self.exh_value.value()
        elif k.objectName() == 'neval_value':
            self.AMDock.ga_num_eval = self.neval_value.value()
        elif k.objectName() == 'nruns_value':
            self.AMDock.ga_run = self.nruns_value.value()
        elif k.objectName() == 'rmstol_value':
            self.AMDock.rmsdtol = self.rmstol_value.value()

    def log_level_sel(self, btn):
        self.AMDock.log_level = self.log_group.id(btn)

    def prot_prog_sel(self, btn):
        self.AMDock.prot_prog = self.prog_group.id(btn)

    def data_view(self, cb):
        if cb.isChecked():
            self.AMDock.log_widget.show()

    def configuration(self):
        config = self.AMDock.config_file
        msg = self.AMDock.statusbar.currentMessage()
        self.AMDock.statusbar.clearMessage()
        self.AMDock.statusbar.showMessage('Wrote configuration file', 3000)
        config_file = open(config, 'w')
        config_file.write('################################################################################\n'
                          '#                           AMDOCK CONFIGURATION FILE                          #\n'
                          '################################################################################\n')
        config_file.write('[PDB2PQR]\n')
        config_file.write('ff %s\n' % self.AMDock.forcefield)
        config_file.write('[VINA]\n')
        config_file.write('cpu %s\n' % self.AMDock.ncpu)
        config_file.write('exhaustiveness %s\n' % self.AMDock.exhaustiveness)
        config_file.write('NoPoses %s\n' % self.AMDock.poses_vina)
        config_file.write('[AD4]\n')
        config_file.write('ga_num_eval %s\n' % self.AMDock.ga_num_eval)
        config_file.write('ga_run %s\n' % self.AMDock.ga_run)
        config_file.write('rmstol %s\n' % self.AMDock.rmsdtol)
        config_file.write('[LOG]\n')
        config_file.write('log %s\n' % self.AMDock.log)
        config_file.write('log_level %s\n' % self.AMDock.log_level)
        config_file.write('[PROTONATION]\n')
        config_file.write('protonation %s\n' % self.AMDock.protonation)
        config_file.write('protonation_program %s\n' % self.AMDock.protonation_program)
        config_file.close()
        # time.sleep(3)
        self.AMDock.statusbar.showMessage(msg)
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
        config_file.write('log True\n')
        config_file.write('log_level 2\n')
        config_file.write('[PROTONATION]\n')
        config_file.write('protonation False\n')
        config_file.write('protonation_program obabel\n')

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
                    self.forcefield = self.AMDock.forcefield = line.split()[1]
                elif re.search('cpu', line):
                    self.ncpu = self.AMDock.ncpu = int(line.split()[1])
                elif re.search('exhaustiveness', line):
                    self.exhaustiveness = self.AMDock.exhaustiveness = int(line.split()[1])
                elif re.search('NoPoses', line):
                    self.poses_vina = self.AMDock.poses_vina = int(line.split()[1])
                elif re.search('ga_num_eval', line):
                    self.ga_num_eval = self.AMDock.ga_num_eval = int(line.split()[1])
                elif re.search('ga_run', line):
                    self.ga_run = self.AMDock.ga_run = int(line.split()[1])
                elif re.search('rmstol', line):
                    self.rmsdtol = self.AMDock.rmsdtol = float(line.split()[1])
                elif line.split()[0] == 'log':
                    if line.split()[1] == 'False':
                        self.log = self.AMDock.log = False
                    else:
                        self.log = self.AMDock.log = True
                elif line.split()[0] == 'log_level':
                    self.log_level = self.AMDock.log_level = int(line.split()[1])
                elif line.split()[0] == 'protonation':
                    if line.split()[1] == 'False':
                        self.protonation = self.AMDock.protonation = False
                    else:
                        self.protonation = self.AMDock.protonation = True
                elif line.split()[0] == 'protonation_program':
                    self.protonation_program = self.AMDock.protonation_program = line.split()[1].strip()
        cfile.close()

    def check_changes(self):
        """check if you saved the configuration """
        if (self.ncpu != self.AMDock.ncpu or self.exhaustiveness != self.AMDock.exhaustiveness or
                self.poses_vina != self.AMDock.poses_vina or self.ga_run != self.AMDock.ga_run or
                self.ga_num_eval != self.AMDock.ga_num_eval or self.rmsdtol != self.AMDock.rmsdtol or
                self.log != self.AMDock.log or self.log_level != self.AMDock.log_level or
                self.forcefield != self.AMDock.forcefield):
            self.unsaved_config.show()
        else:
            self.unsaved_config.hide()
