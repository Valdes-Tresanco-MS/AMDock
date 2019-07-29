from PyQt4 import QtGui, QtCore
import os, Queue
from command_runner import Worker
from warning import reset_warning
from variables import Variables
from rfile_show import Result_File

__version__ = "1.1.0 For main_window and Linux"


class Results(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Results, self).__init__(parent)
        self.parent = parent
        self.setObjectName("result_tab")

        self.rfile_show = Result_File(self)
        self.only_one = 0

        self.import_box = QtGui.QGroupBox(self)
        self.import_box.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.import_box.setObjectName("import_box")
        self.import_box.setTitle("Import")

        self.load_button = QtGui.QPushButton(self.import_box)
        self.load_button.setObjectName("load_button")
        self.load_button.setText("Load Data")

        self.import_text = QtGui.QLineEdit(self.import_box)
        self.import_text.setReadOnly(True)
        self.import_text.setObjectName("import_text")
        self.import_text.setPlaceholderText('*.amdock')

        self.show_rfile = QtGui.QPushButton(self.import_box)
        self.show_rfile.setObjectName("show_rfile")
        self.show_rfile.setText("Results File")

        self.import_help = QtGui.QPushButton(self.import_box)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.import_help.setFont(font)
        self.import_help.setObjectName("import_help")
        self.import_help.setText("?")
        self.import_help.setToolTip(self.parent.tt.result_tt)

        self.import_layout = QtGui.QHBoxLayout(self.import_box)
        self.import_layout.addWidget(self.load_button)
        self.import_layout.addWidget(self.import_text, 1)
        self.import_layout.addWidget(self.show_rfile)
        self.import_layout.addWidget(self.import_help)

        self.data_box = QtGui.QGroupBox(self)
        self.data_box.setAlignment(QtCore.Qt.AlignCenter)
        self.data_box.setObjectName("data_box")
        self.data_box.setTitle("Data Result")
        self.prot_label = QtGui.QLabel('Target: ', self.data_box)
        self.prot_labelB = QtGui.QLabel('Off-Target', self.data_box)
        self.prot_labelB.hide()
        self.prot_label_sel = QtGui.QLabel(self)
        self.prot_label_sel.setAlignment(QtCore.Qt.AlignCenter)
        self.prot_label_sel.hide()

        self.prot_label_selB = QtGui.QLabel(self)
        self.prot_label_selB.setAlignment(QtCore.Qt.AlignCenter)
        self.prot_label_selB.hide()

        self.minus = QtGui.QLabel(self)
        self.minus.setText('-')
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.minus.setFont(font)
        self.minus.hide()

        self.equal = QtGui.QLabel(self)
        self.equal.setText('=')
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.equal.setFont(font)
        self.equal.hide()

        self.selectivity = QtGui.QLabel(self)
        self.selectivity.setText('Selectivity: ')
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.selectivity.setFont(font)
        self.selectivity.hide()

        self.selectivity_value_text = QtGui.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.selectivity_value_text.setFont(font)
        self.selectivity_value_text.hide()

        self.sele1 = QtGui.QSpinBox(self)
        self.sele1.setRange(1, 10)
        self.sele1.setObjectName('sele1')
        self.sele1.hide()

        self.sele2 = QtGui.QSpinBox(self)
        self.sele2.setRange(1, 10)
        self.sele2.setObjectName('sele2')
        self.sele2.hide()

        self.sele1.valueChanged.connect(lambda: self.select_row(self.sele1))
        self.sele2.valueChanged.connect(lambda: self.select_row(self.sele2))

        self.result_table = QtGui.QTableWidget(self.data_box)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.result_table.setFont(font)
        self.result_table.setObjectName("result_table")
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(
            QtCore.QString("Pose;Binding Energy(kcal/mol);Estimated Ki;Ki Units;Ligand Efficiency").split(";"))
        self.result_table.horizontalHeader().setDefaultSectionSize(174)
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.verticalHeader().setDefaultSectionSize(19)
        self.result_table.sortItems(0, QtCore.Qt.AscendingOrder)

        self.result_tableB = QtGui.QTableWidget(self.data_box)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.result_tableB.setFont(font)
        self.result_tableB.setObjectName("result_tableB")
        self.result_tableB.setColumnCount(5)
        self.result_tableB.setHorizontalHeaderLabels(
            QtCore.QString("Pose;Binding Energy(kcal/mol);Estimated Ki;Ki Units;Ligand Efficiency").split(";"))
        self.result_tableB.horizontalHeader().setDefaultSectionSize(174)
        self.result_tableB.horizontalHeader().setStretchLastSection(True)
        self.result_tableB.verticalHeader().setVisible(False)
        self.result_tableB.verticalHeader().setDefaultSectionSize(19)
        self.result_tableB.sortItems(0, QtCore.Qt.AscendingOrder)
        self.result_tableB.hide()

        self.best_button = QtGui.QPushButton(self)
        self.best_button.setObjectName("best_button")
        self.best_button.setText("Show Best Pose")
        self.best_button.setFont(font)
        self.best_button.setEnabled(False)

        self.best_buttonB = QtGui.QPushButton(self)
        self.best_buttonB.setObjectName("best_buttonB")
        self.best_buttonB.setText("Best Pose + Off-Target")
        self.best_buttonB.setFont(font)
        self.best_buttonB.hide()

        self.all_button = QtGui.QPushButton(self)
        self.all_button.setObjectName("all_button")
        self.all_button.setText("Show All Poses")
        self.all_button.setFont(font)
        self.all_button.setEnabled(False)

        self.all_buttonB = QtGui.QPushButton(self)
        self.all_buttonB.setObjectName("all_buttonB")
        self.all_buttonB.setText("All Poses + Off-Target")
        self.all_buttonB.setFont(font)
        self.all_buttonB.hide()

        self.show_complex = QtGui.QPushButton(self)
        self.show_complex.setObjectName("show_complex")
        self.show_complex.setText("Show Complex")
        self.show_complex.setFont(font)
        self.show_complex.hide()

        self.new_button = QtGui.QPushButton(self)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.new_button.setFont(font)
        self.new_button.setObjectName("new_button")
        self.new_button.setText("New Project")
        self.new_button.setIcon(QtGui.QIcon(QtGui.QPixmap(self.parent.objects.new_icon)))

        self.current_pose = self.sele1.value()
        self.current_poseB = self.sele2.value()

        self.data_box_layout = QtGui.QVBoxLayout(self.data_box)
        self.data_box_layout.addWidget(self.prot_label)
        self.data_box_layout.addWidget(self.result_table)
        self.data_box_layout.addWidget(self.prot_labelB)
        self.data_box_layout.addWidget(self.result_tableB)

        self.spacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.rest_layout = QtGui.QGridLayout()

        self.rest_layout.addWidget(self.prot_label_sel, 0, 1)
        self.rest_layout.addWidget(self.prot_label_selB, 0, 3)
        self.rest_layout.addWidget(self.selectivity, 1, 0)
        self.rest_layout.addWidget(self.sele1, 1, 1)
        self.rest_layout.addWidget(self.minus, 1, 2, QtCore.Qt.AlignCenter)
        self.rest_layout.addWidget(self.sele2, 1, 3)
        self.rest_layout.addWidget(self.equal, 1, 4, QtCore.Qt.AlignCenter)
        self.rest_layout.addWidget(self.selectivity_value_text, 1, 5, QtCore.Qt.AlignCenter)
        self.rest_layout.setColumnStretch(0, 1)
        self.rest_layout.setColumnStretch(1, 1)
        self.rest_layout.setColumnStretch(2, 1)
        self.rest_layout.setColumnStretch(3, 1)
        self.rest_layout.setColumnStretch(4, 1)
        self.rest_layout.setColumnStretch(5, 1)
        self.rest_layout.setColumnStretch(6, 5)

        self.buttons_layout = QtGui.QHBoxLayout()
        self.buttons_layout.addWidget(self.show_complex)
        self.buttons_layout.addWidget(self.best_button)
        self.buttons_layout.addWidget(self.all_button)
        self.buttons_layout.addStretch(1)
        self.buttons_layout.addWidget(self.best_buttonB)
        self.buttons_layout.addWidget(self.all_buttonB)
        self.buttons_layout.addStretch(10)
        self.buttons_layout.addWidget(self.new_button)

        self.tab_layout = QtGui.QVBoxLayout(self)
        self.tab_layout.addWidget(self.import_box)
        self.tab_layout.addWidget(self.data_box)
        self.tab_layout.addStretch()
        self.tab_layout.addLayout(self.rest_layout)
        self.tab_layout.addLayout(self.buttons_layout)

        self.new_button.clicked.connect(lambda: self.new_project(self.new_button))
        self.load_button.clicked.connect(lambda: self.parent.program_body.load_file(self.load_button))
        self.best_button.clicked.connect(lambda: self.show_best(self.best_button))
        self.all_button.clicked.connect(lambda: self.show_all(self.all_button))
        self.best_buttonB.clicked.connect(lambda: self.show_best(self.best_buttonB))
        self.all_buttonB.clicked.connect(lambda: self.show_all(self.all_buttonB))
        self.show_complex.clicked.connect(self._show_complex)
        self.show_rfile.clicked.connect(self.show_result_file)

    def show_result_file(self):
        if self.parent.v.amdock_file is not None:
            if self.only_one == 0:
                self.rfile_show.show()
                self.only_one = 1
                self.rfile_show.lineEdit.setText(self.parent.v.project_name)
                self.rfile_show.lineEdit_2.setText(os.path.normpath(self.parent.v.WDIR))
                self.rfile_show.lineEdit_3.setText(self.parent.v.docking_program)
                self.rfile_show.lineEdit_4.setText(self.parent.v.ligand_name)
                self.rfile_show.lineEdit_5.setText(self.parent.v.protein_name)
                self.rfile_show.lineEdit_6.setText(str(self.parent.v.ligands))
                self.rfile_show.lineEdit_7.setText(str(self.parent.v.metals))
                self.rfile_show.lineEdit_8.setText(self.parent.v.result_file)
                self.rfile_show.lineEdit_9.setText(self.parent.v.best_result_file)
                self.rfile_show.mode_label.setText(self.parent.v.program_mode)
                if self.parent.v.analog_protein_name != 'protein B':
                    self.rfile_show.lineEdit_10.setText(str(self.parent.v.analog_protein_name))
                    self.rfile_show.lineEdit_11.setText(str(self.parent.v.analog_ligands))
                    self.rfile_show.lineEdit_12.setText(str(self.parent.v.analog_metals))
                    self.rfile_show.lineEdit_13.setText(str(self.parent.v.analog_result_file))
                    self.rfile_show.lineEdit_14.setText(str(self.parent.v.best_analog_result_file))
        else:
            QtGui.QMessageBox.information(self, 'Information',
                                          'The amdock file is not defined yet. Please define amdock file.',
                                          QtGui.QMessageBox.Ok)

    def new_project(self, r):
        reset_opt = reset_warning(self)
        if reset_opt == QtGui.QMessageBox.Yes:
            self.parent.statusbar.showMessage("Version: %s" % __version__)
            self.parent.main_window.setTabEnabled(0, True)
            self.parent.main_window.setCurrentIndex(0)
            self.parent.main_window.setTabEnabled(2, False)
            self.parent.program_body.project_text.setEnabled(True)
            self.parent.program_body.wdir_button.setEnabled(True)
            self.parent.program_body.project_text.clear()
            self.parent.program_body.project_box.setEnabled(True)
            self.parent.program_body.wdir_text.clear()
            self.parent.program_body.input_box.setEnabled(False)
            self.parent.program_body.protein_text.clear()
            self.parent.program_body.protein_label.clear()
            self.parent.program_body.protein_textB.clear()
            self.parent.program_body.protein_labelB.clear()
            self.parent.program_body.ligand_text.clear()
            self.parent.program_body.ligand_label.clear()
            self.parent.program_body.grid_box.setEnabled(False)
            self.parent.program_body.btnA_auto.setChecked(True)
            self.parent.program_body.btnB_auto.setChecked(True)
            self.parent.program_body.progressBar.setValue(0)
            self.parent.program_body.run_button.setEnabled(False)
            self.parent.program_body.stop_button.setEnabled(False)
            self.parent.program_body.reset_button.setEnabled(True)
            self.parent.program_body.bind_site_button.setEnabled(True)
            self.prot_label.setText('Target: ')
            self.parent.program_body.simple_docking.setChecked(True)
            self.parent.program_body.run_scoring.hide()
            self.parent.program_body.non_button.hide()
            self.all_button.show()
            self.best_button.show()
            self.show_complex.hide()
            try:
                self.parent.output2file.conclude()
            except:
                pass
            try:
                os.chdir(self.parent.v.loc_project)
            except:
                pass

            self.parent.v = Variables()
            self.parent.configuration_tab.initial_config()
            self.clear_result_tab()
            try:
                self.bestw.__del__()
            except:
                pass
            try:
                self.bestwB.__del__()
            except:
                pass
            try:
                self.allw.__del__()
            except:
                pass
            try:
                self.allwB.__del__()
            except:
                pass
            try:
                self.complexw.__del__()
            except:
                pass

            self.parent.program_body.grid_icon.hide()
            self.parent.program_body.grid_iconB.hide()
            self.parent.program_body.grid_icon_ok.hide()
            self.parent.program_body.grid_icon_okB.hide()
            self.parent.program_body.checker_icon.hide()
            self.parent.program_body.checker_iconB.hide()
            self.parent.program_body.checker_icon_ok.hide()
            self.parent.program_body.checker_icon_okB.hide()
            self.parent.program_body.lig_list.clear()
            self.parent.program_body.lig_list.hide()
            self.parent.program_body.lig_listB.clear()
            self.parent.program_body.lig_listB.hide()

    def clear_result_tab(self):
        self.import_text.clear()
        self.result_table.clear()
        self.result_table.setRowCount(0)
        self.result_tableB.clear()
        self.result_tableB.hide()
        self.selectivity.hide()
        self.sele1.hide()
        self.sele2.hide()
        self.minus.hide()
        self.equal.hide()
        self.import_text.clear()
        self.load_button.setEnabled(True)
        self.selectivity_value_text.hide()
        self.prot_label_sel.hide()
        self.prot_label_selB.hide()
        self.prot_labelB.hide()
        self.best_button.setText('Show Best Pose')
        self.all_button.setText('Show All Poses')
        self.best_buttonB.hide()
        self.all_buttonB.hide()
        self.best_button.setEnabled(False)
        self.all_button.setEnabled(False)
        self.show_complex.hide()
        self.best_button.show()
        self.all_button.show()
        self.result_table.setHorizontalHeaderLabels(
            QtCore.QString("Pose;Binding Energy(kcal/mol);Estimated Ki;Ki Units;Ligand Efficiency").split(";"))
        self.result_tableB.setHorizontalHeaderLabels(
            QtCore.QString("Pose;Binding Energy(kcal/mol);Estimated Ki;Ki Units;Ligand Efficiency").split(";"))

    def show_best(self, b):
        if b.objectName() == 'best_button':
            if self.parent.v.docking_program == 'AutoDock Vina':
                visual_arg = [os.path.join(self.parent.v.result_dir, 'best_pose_target_ADV_result.pdb'),
                              self.parent.ws.lig_site_pymol]
            else:
                visual_arg = [os.path.join(self.parent.v.result_dir, 'best_pose_target_AD4_result.pdb'),
                              self.parent.ws.lig_site_pymol]
            self.best_pymol = {'Pymol': [self.parent.ws.pymol, visual_arg]}
            self.bestw = Worker()
            self.bestw.readyReadStandardOutput.connect(self.parent.program_body.readStdOutput)
            self.bestw.readyReadStandardError.connect(self.parent.program_body.readStdError)
            self.bestw.prog_started.connect(self.parent.program_body.prog_show)
            self.bestw.queue_finished.connect(self.parent.program_body.check_queue)
            self.bestq = Queue.Queue()
            self.bestq.put(self.best_pymol)
            self.bestw.init(self.bestq, 'Visualization')
            self.bestw.start_process()

        else:
            if self.parent.v.docking_program == 'AutoDock Vina':
                visual_arg = [os.path.join(self.parent.v.result_dir, 'best_pose_off-target_ADV_result.pdb'),
                              self.parent.ws.lig_site_pymol]
            else:
                visual_arg = [os.path.join(self.parent.v.result_dir, 'best_pose_off-target_AD4_result.pdb'),
                              self.parent.ws.lig_site_pymol]
            self.best_pymolB = {'Pymol': [self.parent.ws.pymol, visual_arg]}
            self.bestwB = Worker()
            self.bestwB.readyReadStandardOutput.connect(self.parent.program_body.readStdOutput)
            self.bestwB.readyReadStandardError.connect(self.parent.program_body.readStdError)
            self.bestwB.prog_started.connect(self.parent.program_body.prog_show)
            self.bestwB.queue_finished.connect(self.parent.program_body.check_queue)
            self.bestqB = Queue.Queue()
            self.bestqB.put(self.best_pymolB)
            self.bestwB.init(self.bestqB, 'Visualization')
            self.bestwB.start_process()

    def show_all(self, b):
        if b.objectName() == 'all_button':
            if self.parent.v.docking_program == 'AutoDock Vina':
                visual_arg = [os.path.join(self.parent.v.input_dir, self.parent.v.protein_pdbqt),
                              os.path.join(self.parent.v.result_dir, 'all_poses_target_ADV_result.pdb'),
                              self.parent.ws.protein_cartoon_pymol]
            else:
                visual_arg = [os.path.join(self.parent.v.input_dir, self.parent.v.protein_pdbqt),
                              os.path.join(self.parent.v.result_dir, 'all_poses_target_AD4_result.pdb'),
                              self.parent.ws.protein_cartoon_pymol]
            self.all_pymol = {'Pymol': [self.parent.ws.pymol, visual_arg]}
            self.allw = Worker()
            self.allw.readyReadStandardOutput.connect(self.parent.program_body.readStdOutput)
            self.allw.readyReadStandardError.connect(self.parent.program_body.readStdError)
            self.allw.prog_started.connect(self.parent.program_body.prog_show)
            self.allw.queue_finished.connect(self.parent.program_body.check_queue)
            self.allq = Queue.Queue()
            self.allq.put(self.all_pymol)
            self.allw.init(self.allq, 'Visualization')
            self.allw.start_process()
        else:
            if self.parent.v.docking_program == 'AutoDock Vina':
                visual_arg = [os.path.join(self.parent.v.input_dir, self.parent.v.analog_protein_pdbqt),
                              os.path.join(self.parent.v.result_dir, 'all_poses_off-target_ADV_result.pdb'),
                              self.parent.ws.protein_cartoon_pymol]
            else:
                visual_arg = [os.path.join(self.parent.v.input_dir, self.parent.v.analog_protein_pdbqt),
                              os.path.join(self.parent.v.result_dir, 'all_poses_off-target_AD4_result.pdb'),
                              self.parent.ws.protein_cartoon_pymol]
            self.all_pymolB = {'Pymol': [self.parent.ws.pymol, visual_arg]}
            self.allwB = Worker()
            self.allwB.readyReadStandardOutput.connect(self.parent.program_body.readStdOutput)
            self.allwB.readyReadStandardError.connect(self.parent.program_body.readStdError)
            self.allwB.prog_started.connect(self.parent.program_body.prog_show)
            self.allwB.queue_finished.connect(self.parent.program_body.check_queue)
            self.allqB = Queue.Queue()
            self.allqB.put(self.all_pymolB)
            self.allwB.init(self.allqB, 'Visualization')
            self.allwB.start_process()

    def _show_complex(self):
        visual_arg = [os.path.join(self.parent.v.input_dir, self.parent.v.protein_pdbqt),
                      os.path.join(self.parent.v.input_dir, self.parent.v.ligand_pdbqt),
                      self.parent.ws.protein_cartoon_pymol]
        self.complex_pymol = {'Pymol': [self.parent.ws.pymol, visual_arg]}
        self.complexw = Worker()
        self.complexw.readyReadStandardOutput.connect(self.parent.program_body.readStdOutput)
        self.complexw.readyReadStandardError.connect(self.parent.program_body.readStdError)
        self.complexw.prog_started.connect(self.parent.program_body.prog_show)
        self.complexw.queue_finished.connect(self.parent.program_body.check_queue)
        self.complexq = Queue.Queue()
        self.complexq.put(self.complex_pymol)
        self.complexw.init(self.complexq, 'Visualization')
        self.complexw.start_process()

    def select_row(self, sele):
        if sele.objectName() == 'sele1':
            self.result_table.item(self.current_pose - 1, 1).setBackgroundColor(QtGui.QColor('white'))
            self.current_pose = sele.value()
            self.result_table.item(self.current_pose - 1, 1).setBackgroundColor(QtGui.QColor('darkGray'))
            self.value1 = float(self.result_table.item(self.current_pose - 1, 1).text())
        else:
            self.result_tableB.item(self.current_poseB - 1, 1).setBackgroundColor(QtGui.QColor('white'))
            self.current_poseB = sele.value()
            self.result_tableB.item(self.current_poseB - 1, 1).setBackgroundColor(QtGui.QColor('darkGray'))
            self.value2 = float(self.result_tableB.item(self.current_poseB - 1, 1).text())
        self.selectivity_value = self.value1 - self.value2
        self.selectivity_value_text.setText('%s kcal/mol' % self.selectivity_value)
