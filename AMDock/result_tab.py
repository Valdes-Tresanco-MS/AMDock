import os
from queue import Queue
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from AMDock.command_runner import PROCESS
from AMDock.rfile_show import Result_File
from AMDock.tools import FormatedText as Ft
from AMDock.variables import Variables
from AMDock.warning import amdock_file_warning
import math


class Results(QWidget):
    def __init__(self, parent=None):
        super(Results, self).__init__(parent)
        self.AMDock = parent
        self.setObjectName("result_tab")

        self.rfile_show = Result_File(self.AMDock)
        self.rfile_show.close()

        self.import_box = QGroupBox(self)
        self.import_box.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.import_box.setObjectName("import_box")
        self.import_box.setTitle("Import")
        self.import_box.setToolTip(self.AMDock.result_tt)

        self.load_button = QPushButton(self.import_box)
        self.load_button.setObjectName("load_button")
        self.load_button.setText("Load Data")

        self.import_text = QLineEdit(self.import_box)
        self.import_text.setReadOnly(True)
        self.import_text.setObjectName("import_text")
        self.import_text.setPlaceholderText('*.amdock')

        self.show_rfile = QPushButton(self.import_box)
        self.show_rfile.setObjectName("show_rfile")
        self.show_rfile.setText("Results File")

        self.import_layout = QHBoxLayout(self.import_box)
        self.import_layout.addWidget(self.load_button)
        self.import_layout.addWidget(self.import_text, 1)
        self.import_layout.addWidget(self.show_rfile)

        self.data_box = QGroupBox(self)
        self.data_box.setAlignment(Qt.AlignCenter)
        self.data_box.setObjectName("data_box")
        self.data_box.setTitle("Data Result")
        self.prot_label = QLabel('Target: ', self.data_box)
        self.prot_labelB = QLabel('Off-Target: ', self.data_box)
        self.prot_labelB.hide()
        self.prot_label_sel = QLabel(self)
        self.prot_label_sel.setAlignment(Qt.AlignCenter)
        self.prot_label_sel.hide()

        self.prot_label_selB = QLabel(self)
        self.prot_label_selB.setAlignment(Qt.AlignCenter)
        self.prot_label_selB.hide()

        self.div = QLabel(self)
        self.div.setText(':')
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.div.setFont(font)
        self.div.hide()

        self.equal = QLabel(self)
        self.equal.setText('=')
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.equal.setFont(font)
        self.equal.hide()

        self.selectivity = QLabel(self)
        self.selectivity.setText('Selectivity: ')
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.selectivity.setFont(font)
        self.selectivity.hide()

        self.selectivity_value_text = QLabel(self)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.selectivity_value_text.setFont(font)
        self.selectivity_value_text.hide()

        self.sele1 = QSpinBox(self)
        self.sele1.setRange(1, 10)
        self.sele1.setObjectName('sele1')
        self.sele1.hide()

        self.sele2 = QSpinBox(self)
        self.sele2.setRange(1, 10)
        self.sele2.setObjectName('sele2')
        self.sele2.hide()

        self.sele1.valueChanged.connect(lambda: self.select_row(self.sele1))
        self.sele2.valueChanged.connect(lambda: self.select_row(self.sele2))

        self.result_table = QTableWidget(self.data_box)
        self.result_table.setObjectName("result_table")
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels(
            str("Pose;Affinity(kcal/mol);Estimated Ki;Ki Units;Ligand Efficiency").split(";"))
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_table.verticalHeader().setVisible(False)
        self.result_table.sortItems(0, Qt.AscendingOrder)

        self.result_tableB = QTableWidget(self.data_box)
        self.result_tableB.setObjectName("result_tableB")
        self.result_tableB.setColumnCount(5)
        self.result_tableB.setHorizontalHeaderLabels(
            str("Pose;Affinity(kcal/mol);Estimated Ki;Ki Units;Ligand Efficiency").split(";"))
        self.result_tableB.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result_tableB.verticalHeader().setVisible(False)
        self.result_tableB.sortItems(0, Qt.AscendingOrder)
        self.result_tableB.hide()

        self.showinpymol = QPushButton(self)
        self.showinpymol.setObjectName("showinpymol")
        self.showinpymol.setText("Show in PyMol")

        self.new_button = QPushButton(self)
        self.new_button.setObjectName("new_button")
        self.new_button.setText("New Project")
        self.new_button.setIcon(QIcon(self.AMDock.new_icon))

        self.current_pose = self.sele1.value()
        self.current_poseB = self.sele2.value()

        self.data_box_layout = QVBoxLayout(self.data_box)
        self.data_box_layout.addWidget(self.prot_label)
        self.data_box_layout.addWidget(self.result_table)
        self.data_box_layout.addWidget(self.prot_labelB)
        self.data_box_layout.addWidget(self.result_tableB)

        self.spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.rest_layout = QGridLayout()

        self.rest_layout.addWidget(self.prot_label_sel, 0, 1)
        self.rest_layout.addWidget(self.prot_label_selB, 0, 3)
        self.rest_layout.addWidget(self.selectivity, 1, 0)
        self.rest_layout.addWidget(self.sele1, 1, 1)
        self.rest_layout.addWidget(self.div, 1, 2, Qt.AlignCenter)
        self.rest_layout.addWidget(self.sele2, 1, 3)
        self.rest_layout.addWidget(self.equal, 1, 4, Qt.AlignCenter)
        self.rest_layout.addWidget(self.selectivity_value_text, 1, 5, Qt.AlignCenter)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addWidget(self.showinpymol)
        self.buttons_layout.addStretch(10)
        self.buttons_layout.addWidget(self.new_button)

        self.tab_layout = QVBoxLayout(self)
        self.tab_layout.addWidget(self.import_box)
        self.tab_layout.addWidget(self.data_box, 4)
        self.tab_layout.addLayout(self.rest_layout)
        self.tab_layout.addLayout(self.buttons_layout, 1)

        self.new_button.clicked.connect(self.new_project)
        self.load_button.clicked.connect(self.load_file)
        self.showinpymol.clicked.connect(self.show_inPyMol)
        self.show_rfile.clicked.connect(self.show_result_file)

    def load_file(self):
        if self.AMDock.project.output:
            self.prot_opt = amdock_file_warning(self)
            if self.prot_opt == QMessageBox.Yes:
                self.clear_result_tab()
            else:
                return
        self.amdock_load()
        self.AMDock.statusbar.showMessage(" Loading amdock file...", 2000)

    def amdock_load(self):
        elements = {0: 'Working Directory', 1: 'Input Directory', 2: 'Results Directory', 3: 'PDBQT of Target Protein',
                    4: 'All Poses File of Target Result', 5: 'Best Pose File of Target Result',
                    6: 'PDBQT of Off-Target Protein', 7: 'All Poses File of Off-Target Result',
                    8: 'Best Pose File of Off-Target Result'}
        elements_score = {0: 'Working Directory', 1: 'Input Directory', 2: 'Results Directory',
                          3: 'PDBQT of Target Protein', 4: 'PDBQT of Ligand'}
        self.AMDock.statusbar.showMessage(" Loading .amdock file...", 2000)
        # if self.
        self.data = self.AMDock.loader.load_amdock_file()
        if self.data:
            if self.AMDock.project.mode == 1:
                self.table1 = self.data[0]
                self.complete = self.data[1]
                self.table2 = self.data[2]
            else:
                self.table1 = self.data[0]
                self.complete = self.data[1]
            errlist = ''
            errlist2 = []
            if self.AMDock.project.mode != 2:
                for index in range(0, len(self.complete)):
                    if self.complete[index] == '1':
                        errlist += '\n-%s' % elements[index]
                if len(errlist) != 0:
                    QMessageBox.critical(self, 'Error', 'Some files defined in .amdock file were not found or '
                                                              'they are inaccessible.\nMissing elements:%s' % errlist)
                    self.import_text.clear()
                    Variables.__init__(self.AMDock)
                else:
                    os.chdir(self.AMDock.project.results)
                    self.prot_label.setText('Target: %s' % self.AMDock.target.name)
                    self.prot_label_sel.setText('%s' % self.AMDock.target.name)

                    self.result_table.setRowCount(len(self.table1))
                    self.sele1.setRange(1, len(self.table1))
                    f = 0
                    for x in self.table1:
                        c = 0
                        for item in x:
                            item = str(item)
                            self.result_table.setItem(f, c, QTableWidgetItem(item))
                            self.result_table.item(f, c).setTextAlignment(
                                Qt.AlignHCenter | Qt.AlignVCenter)
                            if c == 4:
                                item_v = float(item)
                                if item_v <= -0.3:
                                    self.result_table.item(f, c).setBackground(
                                        QColor(0, 255, 128, 200))
                            c += 1
                        f += 1
                    self.value1 = float(self.result_table.item(0, 1).text())
                    self.result_table.item(0, 1).setBackground(QColor('darkGray'))
                    selection_model = self.result_table.selectionModel()
                    selection_model.select(self.result_table.model().index(0, 0),
                                           QItemSelectionModel.ClearAndSelect)
                    if self.AMDock.project.bsd_mode_target == 0:
                        self.result_table.setHorizontalHeaderLabels(
                            str(
                                "Binding Site;Affinity(kcal/mol);Estimated Ki;Ki Units;Ligand Efficiency").split(";"))
                    else:
                        self.result_table.setHorizontalHeaderLabels(
                            str(
                                "Pose;Affinity(kcal/mol);Estimated Ki;Ki Units;Ligand Efficiency").split(";"))

                    if self.AMDock.project.mode == 1:
                        self.prot_labelB.setText('Off-Target: %s' % self.AMDock.offtarget.name)
                        self.prot_label_selB.setText('%s' % self.AMDock.offtarget.name)
                        self.result_tableB.show()
                        self.selectivity_value_text.show()
                        self.selectivity.show()
                        self.sele1.show()
                        self.sele2.show()
                        self.prot_label_sel.show()
                        self.prot_label_selB.show()
                        self.div.show()
                        self.equal.show()
                        self.prot_labelB.show()

                        self.result_tableB.setRowCount(len(self.table2))
                        self.sele2.setRange(1, len(self.table2))
                        f = 0
                        for x in self.table2:
                            c = 0
                            for item in x:
                                item = str(item)
                                self.result_tableB.setItem(f, c, QTableWidgetItem(item))
                                self.result_tableB.item(f, c).setTextAlignment(
                                    Qt.AlignHCenter | Qt.AlignVCenter)
                                if c == 4:
                                    item_v = float(item)
                                    if item_v <= -0.3:
                                        self.result_tableB.item(f, c).setBackground(
                                            QColor(0, 255, 128, 200))
                                c += 1
                            f += 1
                            self.value2 = float(
                                self.result_tableB.item(0, 1).text())
                        self.result_tableB.item(0, 1).setBackground(QColor('darkGray'))
                        selection_model = self.result_tableB.selectionModel()
                        selection_model.select(self.result_tableB.model().index(0, 0),
                                               QItemSelectionModel.ClearAndSelect)
                        if self.AMDock.project.bsd_mode_offtarget == 0:
                            self.result_tableB.setHorizontalHeaderLabels(
                                str(
                                    "Binding Site;Affinity(kcal/mol);Estimated Ki;Ki Units;Ligand Efficiency").split(
                                    ";"))
                        else:
                            self.result_tableB.setHorizontalHeaderLabels(
                                str(
                                    "Pose;Affinity(kcal/mol);Estimated Ki;Ki Units;Ligand Efficiency").split(
                                    ";"))
                        self.selectivity_value = math.exp((self.value2 - self.value1)/(0.001987207 * 298))
                        self.selectivity_value_text.setText(
                            '%.01f' % self.selectivity_value)
            else:
                for index in range(0, len(self.complete)):
                    if self.complete[index] == '1':
                        errlist += '\n-%s' % elements_score[index]
                        errlist2.append(index)
                if len(errlist) != 0:
                    QMessageBox.critical(self, 'Error', 'Some files defined in .amdock file were not found or '
                                                              'they are inaccessible.\nMissing elements:%s' % errlist)
                    self.import_text.clear()
                    Variables.__init__(self.AMDock)
                else:
                    os.chdir(self.AMDock.project.results)
                    self.prot_label.setText('Target: %s' % self.AMDock.target.name)

                    self.result_table.setRowCount(len(self.table1))
                    self.sele1.setRange(1, len(self.table1))
                    f = 0
                    for x in self.table1:
                        c = 0
                        for item in x:
                            item = str(item)
                            self.result_table.setItem(f, c, QTableWidgetItem(item))
                            self.result_table.item(f, c).setTextAlignment(
                                Qt.AlignHCenter | Qt.AlignVCenter)
                            if c == 4:
                                item_v = float(item)
                                if item_v <= -0.3:
                                    self.result_table.item(f, c).setBackground(
                                        QColor(0, 255, 128, 200))
                            c += 1
                        f += 1
                    self.result_table.item(0, 1).setBackground(QColor('darkGray'))
                    selection_model = self.result_table.selectionModel()
                    selection_model.select(self.result_table.model().index(0, 0),
                                           QItemSelectionModel.ClearAndSelect)
            # open log if exit
            if os.path.exists(os.path.join(self.AMDock.project.WDIR, self.AMDock.project.name + '.log')):
                self.AMDock.project.log = os.path.join(self.AMDock.project.WDIR, self.AMDock.project.name + '.log')
            if not self.AMDock.project.log:
                return
            if os.path.exists(self.AMDock.project.log):
                msg = QMessageBox.information(self.AMDock, 'Information', 'This project has a log file.'
                                                ' Do you want to open it?', QMessageBox.Yes |
                                                    QMessageBox.No)
                if msg == QMessageBox.Yes:
                    self.AMDock.log_widget.textedit.append(Ft('Opening AMDock Log File...').process())
                    ofile = open(self.AMDock.project.log)
                    for line in ofile:
                        line = line.strip('\n')
                        self.AMDock.log_widget.textedit.append(line)
                    ofile.close()
                    self.AMDock.log_widget.textedit.append(Ft('Opening AMDock Log File... Done.').process())

    def show_result_file(self):
        if self.AMDock.project.output:
            self.rfile_show.textedit.moveCursor(QTextCursor.Start)
            self.rfile_show.textedit.ensureCursorVisible()
            self.rfile_show.show()

    def new_project(self):
        if self.AMDock.state:
            msg = QMessageBox.warning(self.AMDock, 'Warning',
                                            'There are processes in the background. Do you want to close them?',
                                            QMessageBox.Yes | QMessageBox.No)
            if msg == QMessageBox.No:
                return
            elif msg == QMessageBox.Yes:
                try:
                    self.pymol.force_finished()
                except:
                    pass
        if self.AMDock.program_body.reset_function():
            Variables.__init__(self.AMDock)
            self.prot_label.setText('Target: ')
            self.prot_labelB.setText('Off-Target: ')
            # try:
            #     self.AMDock.output2file.conclude()
            # except:
            #     pass
            try:
                os.chdir(self.AMDock.loc_project)
            except:
                pass

            self.clear_result_tab()
            self.AMDock.log_widget.textedit.append(80 * '#')
            self.AMDock.log_widget.textedit.append(Ft('NEW PROJECT...\n\n').resetting())

    def clear_result_tab(self):
        self.import_text.clear()
        self.result_table.clearContents()
        self.result_tableB.clearContents()
        self.result_tableB.hide()
        self.selectivity.hide()
        self.sele1.hide()
        self.sele2.hide()
        self.div.hide()
        self.equal.hide()
        self.import_text.clear()
        self.selectivity_value_text.hide()
        self.prot_label_sel.hide()
        self.prot_label_selB.hide()
        self.prot_labelB.hide()

    def show_inPyMol(self):
        # check if exit any structure
        if self.AMDock.target.pdb:
            # check if exist items
            poses = {'target': [], 'offtarget': []}
            for titem in self.result_table.selectedItems():
                if not titem.row() + 1 in poses['target']:
                    poses['target'].append([int(self.result_table.item(titem.row(), 0).text()),
                                            float(self.result_table.item(titem.row(), 1).text())])

            for oitem in self.result_tableB.selectedItems():
                if not oitem.row() + 1 in poses['offtarget']:
                    poses['offtarget'].append([int(self.result_tableB.item(oitem.row(), 0).text()),
                                               float(self.result_tableB.item(oitem.row(), 1).text())])
            # makes at least one selected item always exist
            if not len(self.result_table.selectedItems() + self.result_tableB.selectedItems()):
                poses['target'] = [self.result_table.item(0, 0)]
                selection_model = self.result_table.selectionModel()
                selection_model.select(self.result_table.model().index(0, 0), QItemSelectionModel.ClearAndSelect)

            visual_arg = [self.AMDock.pymol, self.AMDock.lig_site_pymol, '--']

            if poses['target']:
                # order by affinity
                poses['target'].sort(key=lambda x: x[1])
                target_arg = '%s,Target,' % os.path.join(self.AMDock.project.input,self.AMDock.target.pdb)
                ligands = ''
                c = 1
                for num in poses['target']:
                    if self.AMDock.project.mode == 2:
                        ligands += '%s' % self.AMDock.ligand.input
                    else:
                        ligands += os.path.join(self.AMDock.project.results, '%s_%s_out%02d.pdb' % (
                            self.AMDock.ligand.name, self.AMDock.target.name, num[0]))
                    if c < len(poses['target']):
                        ligands += ','
                        c += 1
                target_arg += ligands
                visual_arg.append(target_arg)

            if poses['offtarget']:
                # order by affinity
                poses['offtarget'].sort(key=lambda x: x[1])
                offtarget_arg = '%s,Off-Target,'% os.path.join(self.AMDock.project.input,self.AMDock.offtarget.pdb)
                ligands = ''
                c = 1
                for num in poses['offtarget']:
                    ligands += os.path.join(self.AMDock.project.results, '%s_%s_out%02d.pdb' %
                                            (self.AMDock.ligand.name, self.AMDock.offtarget.name, num[0]))
                    if c < len(poses['offtarget']):
                        ligands += ','
                        c += 1
                offtarget_arg += ligands
                visual_arg.append(offtarget_arg)

            pymol_command = {'PyMol': [self.AMDock.this_python, visual_arg]}
            self.pymol = PROCESS()
            self.pymol.state.connect(self.AMDock.program_body.check_state)
            self.pymol.process.readyReadStandardOutput.connect(self.pymol_output)
            self.pymol.process.readyReadStandardError.connect(self.AMDock.program_body.readStdError)
            pymolq = Queue()
            pymolq.name = -3
            pymolq.put(pymol_command)
            self.pymol.set_queue(pymolq)
            self.pymol.start_process()

    def pymol_output(self):
        pymol_output = None
        if hasattr(self, 'pymol'):
            pymol_output = str(self.pymol.process.readAllStandardOutput())
        if pymol_output:
            self.pymol_out = str(pymol_output)
        else:
            return
        print(self.pymol_out)

    def select_row(self, sele):
        if sele.objectName() == 'sele1':
            self.result_table.item(self.current_pose - 1, 1).setBackground(QColor('white'))
            self.current_pose = sele.value()
            self.result_table.item(self.current_pose - 1, 1).setBackground(QColor('darkGray'))
            self.value1 = float(self.result_table.item(self.current_pose - 1, 1).text())
        else:
            self.result_tableB.item(self.current_poseB - 1, 1).setBackground(QColor('white'))
            self.current_poseB = sele.value()
            self.result_tableB.item(self.current_poseB - 1, 1).setBackground(QColor('darkGray'))
            self.value2 = float(self.result_tableB.item(self.current_poseB - 1, 1).text())
        self.selectivity_value = math.exp((self.value2 - self.value1)/(0.001987207 * 298))
        self.selectivity_value_text.setText('%.01f' % self.selectivity_value)
