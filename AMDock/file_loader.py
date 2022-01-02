import os
import re
import shutil
import time
from PyQt5.QtWidgets import *
from AMDock.tools import FormatedText as Ft
from AMDock.warning import wdir_warning, same_protein, wdir3_warning


class Loader:
    def __init__(self, parent=None):
        self.AMDock = parent

    def copy_target(self):
        try:
            shutil.copy('%s' % self.AMDock.target.path, self.t_input)
            self.AMDock.target.input = self.t_input
        except:
            nowdir = QMessageBox.critical(self.AMDock, 'Error', 'The working directory was not found or '
                                                                      'it does not have permission for writing.'
                                                                      '\nPlease reset the program.',
                                                QMessageBox.Retry | QMessageBox.Cancel)
            if nowdir == QMessageBox.Retry:
                self.copy_target()
            else:
                return False
        return True

    def copy_offtarget(self):
        try:
            shutil.copy('%s' % self.AMDock.offtarget.path, self.o_input)
            self.AMDock.offtarget.input = self.o_input
        except:
            nowdir = QMessageBox.critical(self.AMDock, 'Error', 'The working directory was not found or '
                                                                      'it does not have permission for writing.'
                                                                      '\nPlease reset the program.',
                                                QMessageBox.Retry | QMessageBox.Cancel)
            if nowdir == QMessageBox.Retry:
                self.copy_offtarget()
            else:
                return False
        return True

    def copy_ligand(self):
        try:
            shutil.copy('%s' % self.AMDock.ligand.path, self.l_input)
            self.AMDock.ligand.input = self.l_input
        except:
            nowdir = QMessageBox.critical(self.AMDock, 'Error', 'The working directory was not found or '
                                                                      'it does not have permission for writing.'
                                                                      '\nPlease reset the program.',
                                                QMessageBox.Retry | QMessageBox.Cancel)
            if nowdir == QMessageBox.Retry:
                self.copy_ligand()
            else:
                return False
        return True

    def create_project_function(self):
        self.AMDock.project.get_info(self.AMDock.program_body.project_text.text())
        try:
            os.chdir(self.AMDock.project.location)
        except:
            wdir_warning(self.AMDock)
            return
        if os.path.exists(self.AMDock.project.name):
            rt = wdir3_warning(self.AMDock)
            if rt == QMessageBox.Yes:
                try:
                    new_name = self.AMDock.project.name + '_old_{:04d}{:02d}{:02d}_{:02d}{:02d}{:02d}'.format(
                        *time.localtime(os.path.getmtime(self.AMDock.project.name))[0:6])
                    os.rename(self.AMDock.project.name, new_name)
                    if os.path.exists(os.path.join(new_name, self.AMDock.project.name + '.amdock')):
                        old_file = open(os.path.join(new_name, self.AMDock.project.name + '.amdock')).readlines()

                        new_file = open(os.path.join(new_name, self.AMDock.project.name + '.amdock'), 'w')
                        for line in old_file:
                            if line[:19] == 'AMDOCK: WORKING_DIR':
                                new_file.write('AMDOCK: WORKING_DIR'.ljust(24) + '%s\n' % os.path.abspath(new_name))
                            else:
                                new_file.write(line)
                        new_file.close()
                except:
                    msg = QMessageBox.critical(self.AMDock, 'Error',
                                                     'The directory could not be renamed. Please check that you have '
                                                     'writing rights.', QMessageBox.Ok)
                    return
            else:
                return
        try:
            os.mkdir(self.AMDock.project.name)
            os.chdir(self.AMDock.project.WDIR)
            os.mkdir('input')
            os.mkdir('results')
            self.AMDock.statusbar.showMessage("Create project: %s" % self.AMDock.project.WDIR, 3000)

            return True
        except:
            wdir_warning(self.AMDock)
            return

    def project_location(self):
        data_file = QFileDialog()
        data_file.setFileMode(QFileDialog.DirectoryOnly)
        if data_file.exec_():
            filenames = data_file.selectedFiles()
            return filenames

    def load_parameters(self):
        data_file = QFileDialog()
        data_file.setFileMode(QFileDialog.AnyFile)
        data_file.setNameFilter("AD4 parameter file (*.dat)")
        if data_file.exec_():
            openfile = data_file.selectedFiles()[0]
            print(str(openfile))
            filename = os.path.split(str(openfile))[1]
            try:
                shutil.copy(str(openfile), self.AMDock.project.input)
                self.AMDock.para_file = filename
            except IOError as e:
                nowdir = QMessageBox.critical(self.AMDock, 'Error', 'Error: %s' % e,
                                                    QMessageBox.Ok)
                return False
            return True
        return

    def load_protein(self):
        data_file = QFileDialog()
        data_file.setFileMode(QFileDialog.AnyFile)
        data_file.setNameFilter("Protein Data Bank (*.pdb *.ent *.pdbqt)")
        if data_file.exec_():
            filenames = data_file.selectedFiles()
            self.AMDock.target.get_data(filenames)
            if self.AMDock.target.name == self.AMDock.offtarget.name:
                self.AMDock.program_body.reset_target()
                self.same = same_protein(self, 'Target Protein', self.AMDock.target.name, 'Off-Target Protein')
                if self.same == QMessageBox.Ok:
                    self.load_protein()
            elif self.AMDock.target.name == self.AMDock.ligand.name:
                self.AMDock.program_body.reset_target()
                self.same = same_protein(self, 'Target Protein', self.AMDock.target.name, 'Ligand')
                if self.same == QMessageBox.Ok:
                    self.load_protein()
            else:
                self.AMDock.program_body.target_label.setText(
                    'Loaded Target Protein from: %s' % self.AMDock.target.path)
                self.AMDock.program_body.target_text.setText(os.path.basename(self.AMDock.target.path))

                self.t_input = os.path.join(self.AMDock.project.input, self.AMDock.target.name + '.' +
                                            self.AMDock.target.ext)

                if not self.copy_target():
                    self.AMDock.program_body.reset_target()
                    self.load_protein()
                else:
                    return self.AMDock.target

    def load_proteinB(self):
        data_file = QFileDialog()
        data_file.setFileMode(QFileDialog.AnyFile)
        data_file.setNameFilter("Protein Data Bank (*.pdb *.ent *.pdbqt)")
        if data_file.exec_():
            filenames = data_file.selectedFiles()
            self.AMDock.offtarget.get_data(filenames)

            if self.AMDock.offtarget.name == self.AMDock.target.name:
                self.AMDock.program_body.reset_offtarget()
                self.same = same_protein(self, 'Off-Target Protein', self.AMDock.offtarget.name, 'Target Protein')
                if self.same == QMessageBox.Ok:
                    self.load_proteinB()
            elif self.AMDock.offtarget.name == self.AMDock.ligand.name:
                self.AMDock.program_body.reset_offtarget()
                self.same = same_protein(self, 'Off-Target Protein', self.AMDock.offtarget.name, 'Ligand')
                if self.same == QMessageBox.Ok:
                    self.load_proteinB()
            else:
                self.AMDock.program_body.offtarget_label.setText('Loaded Off-Target from: %s' %
                                                                 self.AMDock.offtarget.path)
                self.AMDock.program_body.offtarget_text.setText(os.path.basename(self.AMDock.offtarget.path))

                self.o_input = os.path.join(self.AMDock.project.input, self.AMDock.offtarget.name + '.' +
                                            self.AMDock.offtarget.ext)

                if not self.copy_offtarget():
                    self.AMDock.program_body.reset_offtarget()
                    self.load_proteinB()

    def load_ligand(self):
        data_file = QFileDialog()
        data_file.setFileMode(QFileDialog.AnyFile)
        data_file.setNameFilter("Ligand (*.pdb *.mol2 *.pdbqt)")

        if data_file.exec_():
            filenames = data_file.selectedFiles()
            self.AMDock.ligand.get_data(filenames)

            if self.AMDock.ligand.name == self.AMDock.target.name:
                self.AMDock.program_body.reset_ligand()
                self.same = same_protein(self, 'Ligand', self.AMDock.ligand.name, 'Target Protein', 'ligand')
                if self.same == QMessageBox.Ok:
                    self.load_ligand()
            elif self.AMDock.ligand.name == self.AMDock.offtarget.name:
                self.AMDock.program_body.reset_ligand()
                self.same = same_protein(self, 'Ligand', self.AMDock.ligand.name, 'Off-Target Protein', 'ligand')
                if self.same == QMessageBox.Ok:
                    self.load_ligand()
            else:
                self.AMDock.program_body.ligand_label.setText("Loaded Ligand from: %s" % self.AMDock.ligand.path)
                self.AMDock.program_body.ligand_text.setText(os.path.basename(self.AMDock.ligand.path))

                self.l_input = os.path.join(self.AMDock.project.input, self.AMDock.ligand.name + '.' +
                                            self.AMDock.ligand.ext)

                if not self.copy_ligand():
                    self.AMDock.program_body.reset_ligand()
                    self.load_ligand()

    def load_amdock_file(self):
        data_file = QFileDialog()
        data_file.setFileMode(QFileDialog.AnyFile)
        data_file.setNameFilter("AMDock File (*.amdock)")
        if data_file.exec_():
            filenames = data_file.selectedFiles()
            self.AMDock.project.output = str(filenames[0])
            self.AMDock.result_tab.import_text.setText(self.AMDock.project.output)
            self.AMDock.section = 3 # for reset
            amdock_file = open(self.AMDock.project.output)
            self.AMDock.log_widget.textedit.append(Ft('Opening AMDock File (*.amdock)...').process())
            alltable = []
            for line in amdock_file:
                line = line.strip('\n')
                self.AMDock.log_widget.textedit.append(line)
                self.AMDock.result_tab.rfile_show.textedit.append(line)
                if line.startswith('|'):
                    alltable.append(line)
                if not re.search('AMDOCK:', line):
                    continue
                if line[:23] == 'AMDOCK: DOCKING_PROGRAM':
                    self.AMDock.docking_program = (line[24:]).strip()
                    self.AMDock.mess = QLabel(self.AMDock.docking_program + " is selected")
                    self.AMDock.statusbar.addWidget(self.AMDock.mess)
                if line[:20] == 'AMDOCK: PROJECT_NAME':
                    self.AMDock.project.name = (line.split()[2]).strip()
                elif line[:19] == 'AMDOCK: WORKING_DIR':
                    self.AMDock.project.WDIR = (line.split()[2]).strip()
                elif line[:12] == 'AMDOCK: MODE':
                    if (line.split()[2]).strip() == 'SIMPLE':
                        self.AMDock.project.mode = 0
                    elif (line.split()[2]).strip() == 'OFF-TARGET':
                        self.AMDock.project.mode = 1
                    else:
                        self.AMDock.project.mode = 2
                elif line[:15] == 'AMDOCK: TARGET ':
                    self.AMDock.target.name = (line.split()[2]).strip()
                elif line[:19] == 'AMDOCK: OFF-TARGET ':
                    self.AMDock.offtarget.name = (line.split()[2]).strip()
                elif line[:15] == 'AMDOCK: LIGAND ':
                    self.AMDock.ligand.name = (line.split()[2]).strip()
                elif line[:18] == 'AMDOCK: T_BOX_MODE':
                    if (line.split()[2]).strip() == 'AUTOMATIC':
                        self.AMDock.project.bsd_mode_target = 0
                elif line[:18] == 'AMDOCK: O_BOX_MODE':
                    if (line.split()[2]).strip() == 'AUTOMATIC':
                        self.AMDock.project.bsd_mode_offtarget = 0
            amdock_file.close()
            self.AMDock.log_widget.textedit.append(Ft('Opening AMDock File (*.amdock)... Done.').process())
            complete = ''
            # 0 WDIR
            if os.path.exists(self.AMDock.project.WDIR):
                complete += '0'
            else:
                complete += '1'
            # 1 Input folder
            if os.path.exists(os.path.join(self.AMDock.project.WDIR, 'input')):
                complete += '0'
                self.AMDock.project.input = os.path.join(self.AMDock.project.WDIR, 'input')
            else:
                complete += '1'
            # 2 Results folder
            if os.path.exists(os.path.join(self.AMDock.project.WDIR, 'results')):
                complete += '0'
                self.AMDock.project.results = os.path.join(self.AMDock.project.WDIR, 'results')
            else:
                complete += '1'
            # 3 target pdbqt
            if os.path.exists(os.path.join(self.AMDock.project.input, self.AMDock.target.name + '_h.pdb')):
                complete += '0'
                self.AMDock.target.pdb = os.path.join(os.path.join(self.AMDock.project.input,
                                                                   self.AMDock.target.name + '_h.pdb'))
            else:
                complete += '1'

            if self.AMDock.project.mode != 2:
                if self.AMDock.project.mode == 1:
                    # 6
                    if os.path.exists(os.path.join(self.AMDock.project.input, self.AMDock.offtarget.name +
                                                                              '_h.pdb')):
                        complete += '0'
                        self.AMDock.offtarget.pdb = os.path.join(os.path.join(self.AMDock.project.input,
                                                                              self.AMDock.offtarget.name + '_h.pdb'))
                    else:
                        complete += '1'
                    # 7
            else:
                # 9
                if os.path.exists(os.path.join(self.AMDock.project.input, self.AMDock.ligand.name + '_h.pdbqt')):
                    complete += '0'
                    self.AMDock.ligand.pdbqt = os.path.join(self.AMDock.project.input, self.AMDock.ligand.name +
                                                            '_h.pdbqt')
                elif os.path.exists(os.path.join(self.AMDock.project.input, self.AMDock.ligand.name + '.pdbqt')):
                    complete += '0'
                    self.AMDock.ligand.pdbqt = os.path.join(self.AMDock.project.input, self.AMDock.ligand.name +
                                                            '.pdbqt')
                else:
                    complete += '1'
            d = 0
            mode1 = 0
            mode2 = 0
            for x in alltable:
                if x.startswith('|'):
                    if 'POSES' in x:
                        if mode1 == 0:
                            mode1 = d
                        else:
                            mode2 = d
                d += 1
            f = 0
            table1 = []
            for c in alltable:
                if mode1 and f > mode1 + 2:
                    if '__' in c:
                        break
                    else:
                        table1.append(c.split()[1::2])
                f += 1
            if self.AMDock.project.mode == 1:
                ff = 0
                table2 = []
                for c in alltable:
                    if mode2 and ff > mode2 + 2:
                        if '__' in c:
                            break
                        else:
                            table2.append(c.split()[1::2])
                    ff += 1
                return table1, complete, table2
            else:
                return table1, complete
