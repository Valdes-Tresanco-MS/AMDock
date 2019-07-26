import os, time, shutil, math,Queue,re
from PyQt4 import QtGui,QtCore
from warning import wdir_warning, empty_file_warning, same_protein,not_find_warning
from tools import Fix_PQR,PDBMap,HeavyAtoms,Gyrate,GridDefinition,Converter, ClearAndFix
import subprocess
# from default_variables import default_setting
from some_slots import progress
from command_runner import Worker

class Loader(QtGui.QMainWindow):
    def __init__(self, parent = None):
        QtGui.QMainWindow.__init__(parent)
        self.parent = parent
    def project_location(self):
        data_file = QtGui.QFileDialog()
        data_file.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        if data_file.exec_():
            self.parent.program_body.project_text.setDisabled(True)
            #### when pressed location button, it is create a folder tree
            filenames = data_file.selectedFiles()
            self.parent.v.loc_project = str(filenames[0])
            try: os.chdir(self.parent.v.loc_project)
            except: wdir_warning(self.parent)
            if self.parent.program_body.project_text.text() != '':
                self.parent.v.project_name = str(self.parent.program_body.project_text.text())
            try:
                if os.path.exists(self.parent.v.project_name):
                    os.rename(self.parent.v.project_name, self.parent.v.project_name + '_old_' + "%s-%s-%s-%s-%s-%s" %
                    time.localtime(os.path.getmtime(self.parent.v.project_name))[0:6])
                    os.mkdir(self.parent.v.project_name)
                else:
                    os.mkdir(self.parent.v.project_name)
                self.parent.v.WDIR = os.path.join(self.parent.v.loc_project, self.parent.v.project_name)
                os.chdir(self.parent.v.WDIR)
                os.mkdir('input')
                os.mkdir('results')
                self.parent.program_body.input_box.setEnabled(True)
                progress(self.parent.program_body,0,1,2, finish=True,mess='Working Directory Definition...')
                self.parent.program_body.wdir_text.setText(filenames[0])
                self.parent.v.input_dir = os.path.join(self.parent.v.WDIR, 'input')
                self.parent.v.result_dir = os.path.join(self.parent.v.WDIR, 'results')
                self.parent.output2file.file_header(os.path.join(self.parent.v.WDIR, self.parent.v.project_name + '.amdock'))
                self.parent.output2file.out2file('>> PROJECT_NAME: %s\n' % self.parent.v.project_name)
                self.parent.output2file.out2file('>> WORKING_DIRECTORY: %s\n' % os.path.normpath(self.parent.v.WDIR))
            except:
                wdir_warning(self.parent)
                self.parent.v.loc_project = None
                self.parent.program_body.project_text.setDisabled(False)
        return self.parent.v.WDIR

    def load_protein(self):
        data_file = QtGui.QFileDialog()
        data_file.setFileMode(QtGui.QFileDialog.AnyFile)
        data_file.setFilter("Protein Data Bank (*.pdb *.ent *.pdbqt)")
        if data_file.exec_():
            filenames = data_file.selectedFiles()
            self.target_path = str(filenames[0])
            self.target_ext = str(os.path.basename(self.target_path).split('.')[1])
            self.target_name = str(os.path.basename(self.target_path).split('.')[0]).replace(' ', '_')

            self.parent.v.protein_name = self.target_name
            if self.parent.v.analog_protein_name == self.parent.v.protein_name:
                self.same = same_protein(self, 'Target Protein', self.parent.v.protein_name, 'Off-Target Protein')
                if self.same == QtGui.QMessageBox.Ok:
                    self.parent.v.protein_file = None
                    self.parent.v.protein_pdbqt = None
                    self.parent.program_body.protein_text.clear()
                    # self.parent.program_body.non_ligand.hide()
                    self.parent.program_body.btnA_lig.show()
                    self.parent.v.metals = None
                    self.parent.v.ligands = None
                    self.parent.program_body.protein_label.clear()
                    self.load_protein()
            elif self.parent.v.protein_name == self.parent.v.ligand_name:
                self.same = same_protein(self, 'Target Protein', self.parent.v.protein_name, 'Ligand')
                if self.same == QtGui.QMessageBox.Ok:
                    self.parent.v.protein_file = None
                    self.parent.v.protein_pdbqt = None
                    self.parent.program_body.protein_text.clear()
                    # self.parent.program_body.non_ligand.hide()
                    self.parent.program_body.btnA_lig.show()
                    self.parent.v.metals = None
                    self.parent.v.ligands = None
                    self.parent.program_body.protein_label.clear()
                    self.load_protein()
            else:
                if self.parent.v.cr:
                    self.parent.program_body.protein_label.setText('Loaded Target Protein from: %s' % self.target_path)
                else:
                    self.parent.program_body.protein_label.setText('Loaded protein from: %s' % self.target_path)
                self.parent.program_body.protein_text.setText(os.path.basename(self.target_path))
                if self.target_ext == 'pdbqt':
                    self.parent.v.target_prepare = False
                    self.parent.v.protein_pdbqt = str(os.path.basename(self.target_path)).replace(' ', '_')
                else:
                    self.parent.v.protein_file = str(os.path.basename(self.target_path)).replace(' ', '_')

                self.parent.v.input_target = os.path.join(self.parent.v.input_dir,self.target_name.replace(' ','_')+'.'+self.target_ext)

                try:
                    shutil.copy('%s' % self.target_path, self.parent.v.input_target)
                except:
                    nowdir = QtGui.QMessageBox.critical(self.parent, 'Error',
                                                     'The working directory was not found or it does not have permission for writing.\nPlease reset the program.',
                                                     QtGui.QMessageBox.Ok)


                # if self.parent.v.protein_pdbqt is None:
                os.chdir(self.parent.v.input_dir)
                # self.parent.v.input_target = os.path.join(self.parent.v.input_dir, self.parent.v.protein_file)
                self.parent.v.protein = PDBMap(self.target_path)
                try:
                    self.parent.v.ligands = self.parent.v.protein.count_molecules()['ligands']

                    if self.target_ext == 'pdbqt':
                        elim_lig = QtGui.QMessageBox.warning(self.parent,'Warning','The pdbqt file selected have a ligand.\n Do you wish to eliminate it?',QtGui.QMessageBox.Yes| QtGui.QMessageBox.No)
                        if elim_lig == QtGui.QMessageBox.Yes:
                            ClearAndFix(self.parent.v.input_target).write()
                            self.parent.v.ligands = None

                except:
                    pass
                try:
                    self.parent.v.metals = self.parent.v.protein.count_molecules()['metals']
                except:
                    pass
                os.chdir(self.parent.v.loc_project)
                ###lista de ligandos
                if self.parent.v.ligands != None:
                    # self.parent.program_body.non_ligand.hide()
                    for x in self.parent.v.ligands:
                        self.parent.program_body.lig_list.addItem('%s:%s:%s' % x)
                    self.parent.selected_ligand = self.parent.program_body.lig_list.currentText()
                    if self.parent.v.cr:
                        self.parent.program_body.btnA_lig.show()
                        self.parent.program_body.grid_by_lig_cr.setEnabled(True)
                        self.parent.program_body.lig_list.hide()
                    else:
                        self.parent.program_body.lig_list.show()
                        # self.parent.program_body.grid_by_lig.setEnabled(True)
                else:
                    # self.parent.program_body.non_ligand.setText(`self.parent.v.ligands`)
                    if self.parent.v.cr:
                        if self.parent.v.analog_ligands == None:
                            self.parent.program_body.btnA_lig.hide()
                            self.parent.program_body.btnB_lig.hide()
                            self.parent.program_body.grid_by_lig_cr.setEnabled(False)
                            # self.parent.program_body.non_ligand.show()
                        else:
                            self.parent.program_body.grid_by_lig_cr.setEnabled(True)
                            self.parent.program_body.btnA_lig.hide()
                    # else:
                        # self.parent.program_body.grid_by_lig.setEnabled(False)
                        # self.parent.program_body.non_ligand.show()

                if self.parent.v.cr:
                    if self.parent.v.input_lig is None and self.parent.v.input_control is None:
                        progress(self.parent.program_body, 0, 0, 5, finish=True, mess='Target Definition...')
                        self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                        self.parent.program_body.wdir_button.setEnabled(True)
                    elif self.parent.v.input_lig is None and self.parent.v.input_control is not None:
                        progress(self.parent.program_body, 0, 0, 8, finish=True, mess='Target Definition...')
                        self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                        self.parent.program_body.wdir_button.setEnabled(True)
                    elif self.parent.v.input_lig is not None and self.parent.v.input_control is None:
                        progress(self.parent.program_body, 0, 0, 7, finish=True, mess='Target Definition...')
                        self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                        self.parent.program_body.wdir_button.setEnabled(True)
                    else:
                        progress(self.parent.program_body, 0, 0, 10, finish=True, mess='Target Definition...')
                        self.parent.program_body.prep_rec_lig_button.setEnabled(True)
                        self.parent.program_body.wdir_button.setEnabled(False)
                else:
                    if self.parent.v.input_lig is not None:
                        progress(self.parent.program_body, 0, 0, 10, finish=True, mess='Protein Definition...')
                        self.parent.program_body.prep_rec_lig_button.setEnabled(True)
                        self.parent.program_body.wdir_button.setEnabled(False)
                    else:
                        progress(self.parent.program_body, 0, 0, 6, finish=True, mess='Protein Definition...')
                        self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                        self.parent.program_body.wdir_button.setEnabled(True)
                # return self.parent.v.protein_file
            try:
                if self.parent.v.prot_align and self.target_ext in ['pdb','ent'] and self.control_ext in ['pdb','ent']:
                    aln = subprocess.Popen([self.parent.ws.pymol, '-c', self.parent.ws.aln_pymol, '--', '-t', self.target_name+'.'+self.target_ext, '-o', self.control_name+'.'+self.control_ext],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                    aln.wait()
            except: pass

    def load_proteinB(self):
        data_file = QtGui.QFileDialog()
        data_file.setFileMode(QtGui.QFileDialog.AnyFile)
        data_file.setFilter("Protein Data Bank (*.pdb *.ent *.pdbqt)")
        if data_file.exec_():
            filenames = data_file.selectedFiles()

            self.control_path = str(filenames[0])
            self.control_ext = str(os.path.basename(self.control_path).split('.')[1])
            self.control_name = str(os.path.basename(self.control_path).split('.')[0]).replace(' ', '_')

            self.parent.v.analog_protein_name = self.control_name
            if self.parent.v.analog_protein_name == self.parent.v.protein_name:
                self.same = same_protein(self, 'Off-Target Protein', self.parent.v.analog_protein_name, 'Target Protein')
                if self.same == QtGui.QMessageBox.Ok:
                    self.parent.v.analog_protein_file = None
                    self.parent.program_body.protein_textB.clear()
                    self.parent.program_body.non_ligandB.hide()
                    self.parent.program_body.btnB_lig.show()
                    self.parent.v.analog_metals = None
                    self.parent.v.analog_ligands = None
                    self.parent.program_body.protein_labelB.clear()
                    self.load_proteinB()
            elif self.parent.v.analog_protein_name == self.parent.v.ligand_name:
                self.same = same_protein(self, 'Off-Target Protein', self.parent.v.protein_name, 'Ligand')
                if self.same == QtGui.QMessageBox.Ok:
                    self.parent.v.analog_protein_file = None
                    self.parent.v.analog_protein_pdbqt =None
                    self.parent.program_body.protein_textB.clear()
                    self.parent.program_body.non_ligandB.hide()
                    self.parent.program_body.btnB_lig.show()
                    self.parent.v.analog_metals = None
                    self.parent.v.analog_ligands = None
                    self.parent.program_body.protein_labelB.clear()
                    self.load_proteinB()
            else:
                self.parent.program_body.protein_labelB.setText('Loaded Off-Target from: %s' % self.control_path)
                self.parent.program_body.protein_textB.setText(os.path.basename(self.control_path))

                if self.control_ext == 'pdbqt':
                    self.parent.v.control_prepare = False
                    self.parent.v.analog_protein_pdbqt = str(os.path.basename(self.control_path)).replace(' ', '_')
                else:
                    self.parent.v.analog_protein_file = str(os.path.basename(self.control_path)).replace(' ', '_')
                self.parent.v.input_control = os.path.join(self.parent.v.input_dir,self.control_name.replace(' ','_')+'.'+self.control_ext)
                try:
                    shutil.copy('%s' % self.control_path,self.parent.v.input_control)
                except:
                    nowdir = QtGui.QMessageBox.critical(self.parent, 'Error',
                                                        'The working directory was not found or it does not have permission for writing.\nPlease reset the program.',
                                                        QtGui.QMessageBox.Ok)

                os.chdir(self.parent.v.input_dir)
                self.parent.v.analog_protein = PDBMap(self.control_path)
                try:
                    self.parent.v.analog_ligands = self.parent.v.analog_protein.count_molecules()['ligands']
                    if self.control_ext == 'pdbqt':
                        elim_lig = QtGui.QMessageBox.warning(self.parent, 'Warning','The pdbqt file selected have a ligand.\n'
                                            ' Do you wish to eliminate it?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                        if elim_lig == QtGui.QMessageBox.Yes:
                            ClearAndFix(self.parent.v.input_control).write()
                            self.parent.v.analog_ligands = None
                except:
                    pass
                try:
                    self.parent.v.analog_metals = self.parent.v.analog_protein.count_molecules()['metals']
                except:
                    pass
                os.chdir(self.parent.v.loc_project)
                ###lista de ligandos
                if self.parent.v.analog_ligands != None:
                    self.parent.program_body.non_ligandB.hide()
                    for x in self.parent.v.analog_ligands:
                        self.parent.program_body.lig_listB.addItem('%s:%s:%s' % x)
                    self.parent.analog_selected_ligand = self.parent.program_body.lig_listB.currentText()
                    self.parent.program_body.btnB_lig.show()
                    self.parent.program_body.grid_by_lig_cr.setEnabled(True)
                    self.parent.program_body.lig_listB.hide()
                else:
                    self.parent.program_body.non_ligandB.setText(`self.parent.v.analog_ligands`)
                    if self.parent.v.ligands == None:
                        self.parent.program_body.btnA_lig.hide()
                        self.parent.program_body.btnB_lig.hide()
                        self.parent.program_body.grid_by_lig_cr.setEnabled(False)
                        self.parent.program_body.non_ligandB.show()
                    else:
                        self.parent.program_body.grid_by_lig_cr.setEnabled(True)
                        self.parent.program_body.btnB_lig.hide()
                        self.parent.program_body.non_ligandB.show()

                if self.parent.v.input_lig is None and self.parent.v.input_target is None:
                    progress(self.parent.program_body, 0, 0, 5, finish=True, mess='Control Definition...')
                    self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                    self.parent.program_body.wdir_button.setEnabled(True)
                elif self.parent.v.ligand_path == '' and self.parent.v.input_target is not None:
                    progress(self.parent.program_body, 0, 0, 8, finish=True, mess='Control Definition...')
                    self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                    self.parent.program_body.wdir_button.setEnabled(True)
                elif self.parent.v.ligand_path != '' and self.parent.v.input_target is None:
                    progress(self.parent.program_body, 0, 0, 7, finish=True, mess='Control Definition...')
                    self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                    self.parent.program_body.wdir_button.setEnabled(True)
                else:
                    progress(self.parent.program_body, 0, 0, 10, finish=True, mess='Control Definition...')
                    self.parent.program_body.prep_rec_lig_button.setEnabled(True)
                    self.parent.program_body.wdir_button.setEnabled(False)
            try:
                if self.parent.v.prot_align and self.target_ext in ['pdb','ent'] and self.control_ext in ['pdb','ent']:
                    aln = subprocess.Popen([self.parent.ws.pymol, '-c', self.parent.ws.aln_pymol, '--', '-t', self.target_name+'.'+self.target_ext, '-o', self.control_name+'.'+self.control_ext],stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                    aln.wait()
            except:
                pass


    def load_ligand(self):
        data_file = QtGui.QFileDialog()
        data_file.setFileMode(QtGui.QFileDialog.AnyFile)
        data_file.setFilter("Ligand (*.pdb *.mol2 *.pdbqt)")
        if data_file.exec_():
            filenames = data_file.selectedFiles()

            self.input_ligand_path = str(filenames[0])
            self.input_ligand_ext = str(os.path.basename(self.input_ligand_path).split('.')[-1])
            self.input_ligand_name = str(os.path.basename(self.input_ligand_path).split('.')[0]).replace(' ', '_')

            self.parent.v.ligand_name = self.input_ligand_name
            if self.parent.v.ligand_name == self.parent.v.protein_name:
                self.same = same_protein(self, 'Ligand', self.parent.v.ligand_name, 'Target Protein', 'ligand')
                if self.same == QtGui.QMessageBox.Ok:
                    self.parent.v.ligand_file = None
                    self.parent.program_body.ligand_text.clear()
                    self.parent.program_body.ligand_label.clear()
                    self.load_ligand()
            elif self.parent.v.ligand_name == self.parent.v.analog_protein_name:
                self.same = same_protein(self, 'Ligand', self.parent.v.protein_name, 'Control Protein','ligand')
                if self.same == QtGui.QMessageBox.Ok:
                    self.parent.v.ligand_file = None
                    self.parent.program_body.ligand_text.clear()
                    self.parent.program_body.ligand_label.clear()
                    self.load_ligand()

            else:
                self.parent.program_body.ligand_text.setText(os.path.basename(self.input_ligand_path))
                self.parent.program_body.ligand_label.setText("Loaded Ligand from: %s" % self.input_ligand_path)

                if self.input_ligand_ext == 'pdbqt':
                    self.parent.v.ligand_prepare = False
                    self.parent.v.ligand_pdbqt = str(os.path.basename(self.input_ligand_path)).replace(' ', '_')
                else:
                    self.parent.v.ligand_file = str(os.path.basename(self.input_ligand_path)).replace(' ', '_')
                    self.parent.v.ligand_pdb = self.input_ligand_name+'.pdb'

                self.parent.v.input_lig = os.path.join(self.parent.v.input_dir,self.input_ligand_name.replace(' ', '_') +'.'+ self.input_ligand_ext)

                try:
                    shutil.copy('%s' % self.input_ligand_path, self.parent.v.input_lig)
                except:
                    nowdir = QtGui.QMessageBox.critical(self.parent, 'Error',
                                                        'The working directory was not found or it does not have permission for writing.\nPlease reset the program.',
                                                        QtGui.QMessageBox.Ok)

                if self.parent.v.ligand_pdbqt is None:
                    os.chdir(self.parent.v.input_dir)
                    # try:
                    # mol = pybel.readfile(self.parent.v.ligand_file.split('.')[-1],self.parent.v.ligand_file).next()
                    # mol.removeh()
                    if HeavyAtoms(self.parent.v.ligand_file).imp() > 100:
                        self.wlig = QtGui.QMessageBox.warning(self.parent,'Warning','The selected ligand has more of 100 heavy atoms.\nDoes he wish to continue?',QtGui.QMessageBox.Yes| QtGui.QMessageBox.No)
                        if self.wlig == QtGui.QMessageBox.Yes:
                            cmol = Converter(self.parent.ws.openbabel,self.parent.v.ligand_file.split('.')[-1], self.parent.v.ligand_file, self.parent.v.ligand_pdb).format2pdb()
                            if cmol:
                                QtGui.QMessageBox.critical(self.parent, 'Error', 'The ligand can not be converted with '
                                                                                 'OpenBabel.\nPlease check this.',
                                                           QtGui.QMessageBox.Ok)
                            self.parent.v.heavy_atoms = HeavyAtoms(self.parent.v.ligand_file).imp()
                            self.parent.v.rg = int(math.ceil(Gyrate(self.parent.v.ligand_pdb).gyrate()))
                            os.chdir(self.parent.v.loc_project)

                            if self.parent.v.cr:
                                if self.parent.v.input_target == None and self.parent.v.input_control == None:
                                    progress(self.parent.program_body, 0, 0, 4, finish=True, mess='Ligand Definition...')
                                    self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                                    self.parent.program_body.wdir_button.setEnabled(True)
                                elif self.parent.v.input_target == None and self.parent.v.input_control != None:
                                    progress(self.parent.program_body, 0, 0, 7, finish=True, mess='Ligand Definition...')
                                    self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                                    self.parent.program_body.wdir_button.setEnabled(True)
                                elif self.parent.v.input_target != None and self.parent.v.input_control == None:
                                    progress(self.parent.program_body, 0, 0, 7, finish=True, mess='Ligand Definition...')
                                    self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                                    self.parent.program_body.wdir_button.setEnabled(True)
                                else:
                                    progress(self.parent.program_body, 0, 0, 10, finish=True, mess='Ligand Definition...')
                                    self.parent.program_body.prep_rec_lig_button.setEnabled(True)
                                    self.parent.program_body.wdir_button.setEnabled(False)
                            else:
                                if self.parent.v.input_target is not None:
                                    progress(self.parent.program_body, 0, 0, 10, finish=True, mess='Ligand Definition...')
                                    self.parent.program_body.prep_rec_lig_button.setEnabled(True)
                                    self.parent.program_body.wdir_button.setEnabled(False)
                                else:
                                    progress(self.parent.program_body, 0, 0, 6, finish=True, mess='Ligand Definition...')
                                    self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                                    self.parent.program_body.wdir_button.setEnabled(True)
                        else:
                            self.parent.v.ligand_file = None
                            self.parent.program_body.ligand_text.clear()
                            self.parent.program_body.ligand_label.clear()
                            self.load_ligand()

                    else:
                        cmol = Converter(self.parent.ws.openbabel,self.parent.v.ligand_file.split('.')[-1], self.parent.v.ligand_file, self.parent.v.ligand_pdb).format2pdb()
                        if cmol:
                            QtGui.QMessageBox.critical(self.parent, 'Error', 'The ligand can not be converted with '
                                                                             'OpenBabel.\nPlease check this.',
                                                       QtGui.QMessageBox.Ok)
                        self.parent.v.heavy_atoms = HeavyAtoms(self.parent.v.ligand_file).imp()
                        self.parent.v.rg = int(math.ceil(Gyrate(self.parent.v.ligand_pdb).gyrate()))
                        os.chdir(self.parent.v.loc_project)

                        if self.parent.v.cr:
                            if self.parent.v.input_target == None and self.parent.v.input_control is None:
                                progress(self.parent.program_body, 0, 0, 4, finish=True, mess='Ligand Definition...')
                            elif self.parent.v.input_target == None and self.parent.v.input_control is not None:
                                progress(self.parent.program_body, 0, 0, 7, finish=True, mess='Ligand Definition...')
                            elif self.parent.v.input_target != None and self.parent.v.input_control is None:
                                progress(self.parent.program_body, 0, 0, 7, finish=True, mess='Ligand Definition...')
                            else:
                                progress(self.parent.program_body, 0, 0, 10, finish=True, mess='Ligand Definition...')
                                self.parent.program_body.prep_rec_lig_button.setEnabled(True)
                                self.parent.program_body.wdir_button.setEnabled(False)
                        else:
                            if self.parent.v.input_target is not None:
                                progress(self.parent.program_body, 0, 0, 10, finish=True, mess='Ligand Definition...')
                                self.parent.program_body.prep_rec_lig_button.setEnabled(True)
                                self.parent.program_body.wdir_button.setEnabled(False)
                            else:
                                progress(self.parent.program_body, 0, 0, 6, finish=True, mess='Ligand Definition...')

                else:
                    self.parent.v.heavy_atoms = HeavyAtoms(self.input_ligand_path).imp()
                    self.parent.v.rg = int(math.ceil(Gyrate(self.input_ligand_path).gyrate()))
                    if self.parent.v.cr:
                        if self.parent.v.input_target == None and self.parent.v.input_control is None:
                            progress(self.parent.program_body, 0, 0, 4, finish=True, mess='Ligand Definition...')
                            self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                            self.parent.program_body.wdir_button.setEnabled(True)
                        elif self.parent.v.input_target == None and self.parent.v.input_control is not None:
                            progress(self.parent.program_body, 0, 0, 7, finish=True, mess='Ligand Definition...')
                            self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                            self.parent.program_body.wdir_button.setEnabled(True)
                        elif self.parent.v.input_target != None and self.parent.v.input_control is None:
                            progress(self.parent.program_body, 0, 0, 7, finish=True, mess='Ligand Definition...')
                            self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                            self.parent.program_body.wdir_button.setEnabled(True)
                        else:
                            progress(self.parent.program_body, 0, 0, 10, finish=True, mess='Ligand Definition...')
                            self.parent.program_body.prep_rec_lig_button.setEnabled(True)
                            self.parent.program_body.wdir_button.setEnabled(False)
                    else:
                        if self.parent.v.input_target != None:
                            progress(self.parent.program_body, 0, 0, 10, finish=True, mess='Ligand Definition...')
                            self.parent.program_body.prep_rec_lig_button.setEnabled(True)
                            self.parent.program_body.wdir_button.setEnabled(False)
                        else:
                            progress(self.parent.program_body, 0, 0, 6, finish=True, mess='Ligand Definition...')
                            self.parent.program_body.prep_rec_lig_button.setEnabled(False)
                            self.parent.program_body.wdir_button.setEnabled(True)
    def load_amdock_file(self):
        data_file = QtGui.QFileDialog(caption='Open AMDock File')
        data_file.setFileMode(QtGui.QFileDialog.AnyFile)
        data_file.setFilter("AMDock File (*.amdock)")
        if data_file.exec_():
            filenames = data_file.selectedFiles()
            self.parent.v.amdock_path = str(filenames[0])
            self.parent.result_tab.import_text.setText(self.parent.v.amdock_path)
            self.parent.v.amdock_file = open(self.parent.v.amdock_path)
            alltable = []
            for line in self.parent.v.amdock_file:
                line = line.strip('\n')
                alltable.append(line)
                if not re.search('>',line):
                    continue
                if re.search('>> WORKING_DIRECTORY:', line):
                    if (line.split()[2]).strip() == os.path.split(self.parent.v.amdock_path)[0]:
                        self.parent.v.WDIR = (line.split()[2]).strip()
                    else:
                        self.parent.v.WDIR = os.path.split(self.parent.v.amdock_path)[0]
                elif re.search('>> DOCKING_PROGRAM:', line):
                    self.parent.v.docking_program = (line[20:]).strip()
                elif re.search('>> MODE:', line):
                    if (line.split()[2]).strip() == 'SIMPLE':
                        self.parent.v.program_mode = 'SIMPLE'
                        self.parent.v.cr = False
                        self.parent.v.scoring = False
                    elif (line.split()[2]).strip() == 'CROSS':
                        self.parent.v.program_mode = 'CROSS'
                        self.parent.v.cr = True
                        self.parent.v.scoring = False
                    else:
                        self.parent.v.program_mode = 'SCORING'
                        self.parent.v.cr = False
                        self.parent.v.scoring = True
                elif re.search('>> TARGET_PROTEIN:', line):
                    self.parent.v.protein_name = (line.split()[2]).strip()
                elif re.search('>  Target_Ligands:', line):
                    self.parent.v.ligands = (line[19:]).strip()
                elif re.search('>  Target_Metals(Zn):', line):
                    self.parent.v.metals = (line[22:]).strip()
                elif re.search('>> CONTROL_PROTEIN:', line):
                    self.parent.v.analog_protein_name = (line.split()[2]).strip()
                elif re.search('>  Control_Ligands:', line):
                    self.parent.v.analog_ligands = (line[20:]).strip()
                elif re.search('>  Control_Metals(Zn):', line):
                    self.parent.v.analog_metals = (line[23:]).strip()
                elif re.search('>> LIGAND:', line):
                    self.parent.v.ligand_name = (line.split()[2]).strip()
                elif re.search('>  heavy_atoms:', line):
                    self.parent.v.heavy_atoms = (line.split()[2]).strip()
                elif re.search('>  all_poses_target_file:', line):
                    self.parent.v.result_file = (line.split()[2]).strip()
                elif re.search('>  best_pose_target_file:', line):
                    self.parent.v.best_result_file = (line.split()[2]).strip()
                elif re.search('>  all_poses_control_file:', line):
                    self.parent.v.analog_result_file = (line.split()[2]).strip()
                elif re.search('>  best_pose_control_file', line):
                    self.parent.v.best_analog_result_file = (line.split()[2]).strip()
            self.parent.v.amdock_file.close()
            complete = ''
            #0
            if os.path.exists(self.parent.v.WDIR):
                complete += '0'
            else:
                complete += '1'
            #1
            if os.path.exists(os.path.join(self.parent.v.WDIR, 'input')):
                    complete += '0'
                    self.parent.v.input_dir = os.path.join(self.parent.v.WDIR, 'input')
            else:
                complete += '1'
            #2
            if os.path.exists(os.path.join(self.parent.v.WDIR, 'results')):
                complete += '0'
                self.parent.v.result_dir = os.path.join(self.parent.v.WDIR, 'results')
            else:
                complete += '1'
            #3
            if os.path.exists(os.path.join(self.parent.v.input_dir,self.parent.v.protein_name+'_h.pdbqt')):
                complete += '0'
                self.parent.v.protein_pdbqt = os.path.join(self.parent.v.input_dir, self.parent.v.protein_name+'_h.pdbqt')
            elif os.path.exists(os.path.join(self.parent.v.input_dir,self.parent.v.protein_name+'.pdbqt')):
                complete += '0'
                self.parent.v.protein_pdbqt = os.path.join(self.parent.v.input_dir,self.parent.v.protein_name+'.pdbqt')
            else:
                complete += '1'
            if self.parent.v.program_mode is not 'SCORING':
                #4
                if os.path.exists(os.path.join(self.parent.v.result_dir,self.parent.v.result_file)):
                    complete += '0'
                else:
                    complete += '1'
                #5
                if os.path.exists(os.path.join(self.parent.v.result_dir, self.parent.v.best_result_file)):
                    complete += '0'
                else:
                    complete += '1'
                if self.parent.v.program_mode is 'CROSS':
                    #6
                    if os.path.exists(os.path.join(self.parent.v.input_dir, self.parent.v.analog_protein_name + '_h.pdbqt')):
                        complete += '0'
                        self.parent.v.analog_protein_pdbqt = os.path.join(self.parent.v.input_dir,self.parent.v.analog_protein_name+'_h.pdbqt')
                    elif os.path.exists(os.path.join(self.parent.v.input_dir, self.parent.v.analog_protein_name + '.pdbqt')):
                        complete += '0'
                        self.parent.v.analog_protein_pdbqt = os.path.join(self.parent.v.input_dir,self.parent.v.analog_protein_name + '.pdbqt')
                    else:
                        complete += '1'
                    #7
                    if self.parent.v.analog_result_file != '':
                        if os.path.exists(os.path.join(self.parent.v.result_dir, self.parent.v.analog_result_file)):
                            complete += '0'
                        else:
                            complete += '1'
                    else:
                        complete += '1'
                    #8
                    if self.parent.v.best_analog_result_file != '':
                        if os.path.exists(os.path.join(self.parent.v.result_dir, self.parent.v.best_analog_result_file)):
                            complete += '0'
                        else:
                            complete += '1'
                    else:
                        complete += '1'
            else:
                #9
                if os.path.exists(os.path.join(self.parent.v.input_dir, self.parent.v.ligand_name + '_h.pdbqt')):
                    complete += '0'
                    self.parent.v.ligand_pdbqt = os.path.join(self.parent.v.input_dir,self.parent.v.ligand_name + '_h.pdbqt')
                elif os.path.exists(os.path.join(self.parent.v.input_dir, self.parent.v.ligand_name + '.pdbqt')):
                    complete += '0'
                    self.parent.v.ligand_pdbqt = os.path.join(self.parent.v.input_dir,
                                                                      self.parent.v.ligand_name + '.pdbqt')
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
                if c.startswith('|'):
                    if mode1 is not 0 and f > mode1 + 2:
                        if '__' in c:
                            break
                        else:
                            table1.append(c.split()[1::2])
                f += 1
            if self.parent.v.cr:
                ff = 0
                table2 = []
                for c in alltable:
                    if c.startswith('|'):
                        if mode2 is not 0 and ff > mode2 + 2:
                            if '__' in c:
                                break
                            else:
                                table2.append(c.split()[1::2])
                    ff += 1
                return table1, complete, table2
            else:
                return table1, complete
