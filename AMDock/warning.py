from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

def m_filter(s, rg):
    return s < rg


def smallbox_warning(self, dicc, rg, prot):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon("amdock_icon.png"))
    self.msg.setIcon(QMessageBox.Critical)
    self.msg.setWindowTitle("Warning")
    list_ = ''
    for dim in dicc:
        if dicc[dim] < rg:
            if not list_:
                list_ = dim
            else:
                list_ = list_ + ',' + dim
    self.msg.setText(
        '%s-dimensions are smaller than optimal box dimension(%s) for protein "%s".                                   '
        '      ' % (list_, rg, prot))
    self.msg.setInformativeText('Do you want to replace this value?')
    self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    self.msg.setMinimumSize(450, 150)
    retval = self.msg.exec_()
    return retval, list_


def reset_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Warning)
    self.msg.setWindowTitle("Warning")
    self.msg.setText(
        "The program will be restarted.                                                                      ")
    self.msg.setInformativeText('Do you wish to continue?')
    self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    self.msg.setMinimumSize(650, 150)
    retval = self.msg.exec_()
    return retval


def error_message(self, prog, exitcode, exitstatus):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Critical)
    self.msg.setWindowTitle("Error")
    self.msg.setDetailedText('{} finalized with exitcode {} and existstatus {}'.format(prog, exitcode, exitstatus))
    self.msg.setText(
        "The program %s has not finalized correctly.                                                      " % prog)
    self.msg.setInformativeText('The details of the error are shown below')
    self.msg.setStandardButtons(QMessageBox.Ok)
    retval = self.msg.exec_()
    return retval


def internal_error(parent, error):
    msg = QMessageBox(parent)
    msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Error")
    msg.setDetailedText(error)
    msg.setText("An internal error has occurred\n")
    msg.setInformativeText('The details of the error are shown below. Please, contact with us')
    msg.setStandardButtons(QMessageBox.Ok)


def stop_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Critical)
    self.msg.setWindowTitle("Warning")
    self.msg.setText("Do you really wish to stop the simulation?                                  ")
    self.msg.setInformativeText("The whole work accomplished until now will get lost.")
    self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    self.msg.setMinimumSize(450, 150)
    retval = self.msg.exec_()
    return retval


def wdir_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Critical)
    self.msg.setWindowTitle("Error")
    self.msg.setText("It's not possible to create the working directory.                              ")
    self.msg.setInformativeText(
        "It's possible that the selected directory is being used or do not have permission to write on it")
    self.msg.setStandardButtons(QMessageBox.Ok)
    retval = self.msg.exec_()
    return retval


def define_wdir_loc(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Critical)
    self.msg.setWindowTitle("Warning")
    self.msg.setText(
        "Please define the project location.                                                           ")
    self.msg.setStandardButtons(QMessageBox.Ok)
    self.msg.setMinimumSize(450, 150)
    retval = self.msg.exec_()
    return retval


def wdir2_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Critical)
    self.msg.setWindowTitle("Warning")
    self.msg.setText(
        "The working directory is already defined.                                                           ")
    self.msg.setInformativeText(
        "Do you wish to define a new working directory?. All the content of the previous directory will be deleted")
    self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    self.msg.setMinimumSize(450, 150)
    retval = self.msg.exec_()
    return retval


def wdir3_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Warning)
    self.msg.setWindowTitle("Error")
    self.msg.setText("This project name already exist.                              ")
    self.msg.setInformativeText('The existing one will be renamed "(Project_Name)_(old)_(date)". Do you want to rename '
                                'it?')
    self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    retval = self.msg.exec_()
    return retval


# (2) and (2')
def empty_file_warning(self, file_):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Critical)
    self.msg.setWindowTitle("Error")
    self.msg.setText(
        "The %s it empty.                                                                                    " % file_)
    self.msg.setInformativeText("Check the file contains the coordinates of the atoms of %s" % file_)
    self.msg.setStandardButtons(QMessageBox.Ok)
    retval = self.msg.exec_()
    return retval


# (4) para cuando se marque la opcion una vez definida la proteina, entonces se comprueba si existe el metal o no.
# de lo contrario habria que comprobarlo cuando se cargue la proteina
def prot_no_metal_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Warning)
    self.msg.setWindowTitle("Error")
    self.msg.setText(
        "Zn Atom not found.                                                                               ")
    self.msg.setInformativeText(
        'The option "Protein with Zn" is checked, however the protein molecule does not contain any atom of Zn. '
        'The option "Protein with Zn will be unchecked "')
    self.msg.setStandardButtons(QMessageBox.Ok)
    retval = self.msg.exec_()
    return retval


def prot_with_metal_warning(parent, text):
    msg = QMessageBox(parent)
    msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Warning")
    if len(text) == 2:
        msg.setText("This protein contains at least one atom of Zn:                                                   "
                    "                         \n %s (Target)\n %s (Off-target)" % (text['Target'].name,
                                                                                   text['Off-Target'].name))
    else:
        msg.setText("This protein contains at least one atom of Zn:                                                   "
                    "        \n %s (%s)" % (text[list(text.keys())[0]].name, list(text.keys())[0]))
    msg.setInformativeText('AutoDock4Zn is recommendable in this case. However, the current docking program is %s. '
                           'Do you wish to change to AutoDock4Zn?' % parent.docking_program)
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    retval = msg.exec_()
    return retval


def prot_with_metal_warning1(self, prot):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Warning)
    self.msg.setWindowTitle("Warning")
    self.msg.setText(
        "This protein contains at least one Zn atom.                                                      ")
    self.msg.setInformativeText(
        'It is worth noting that %s engine does not contain parameters for this atom.\nDo you wish to move to'
        'AutoDock4Zn?' % self.v.docking_program)
    self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    retval = self.msg.exec_()
    return retval


# (5)

def metal_no_ADzn_od_warning(parent, text):
    msg = QMessageBox(parent)
    msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    msg.setIcon(QMessageBox.Warning)
    msg.setWindowTitle("Warning")
    if len(text) == 2:
        msg.setText("AutoDock4Zn is selected, but the following proteins do not contain Zn atoms:                    "
                    "                         \n %s (Target)\n %s (Off-target)" % (text['Target'].name,
                                                                                   text['Off-Target'].name))
    else:
        msg.setText("AutoDock4Zn is selected, but the following protein do not contain Zn atoms:                    "
                    "                                  \n %s (%s)" % (text[list(text.keys())[0]].name,
                                                                      list(text.keys())[0]))
    msg.setInformativeText('Please, make sure that proteins contains Zn atoms. Press "OK" if you want to change the '
                           'program docking or "Cancel" if you want to select a new protein.')
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    retval = msg.exec_()
    return retval


def metal_no_ADzn_warning1(parent):
    msg = QMessageBox(parent)
    msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Error")
    msg.setText("AutoDock4Zn selected, but the protein not contains Zn atoms. "
                "                                                     ")
    msg.setInformativeText('The program AutoDock4Zn was selected, but the protein not contains Zn atoms. Please, '
                           'select a new protein')
    msg.setStandardButtons(QMessageBox.Ok)
    retval = msg.exec_()
    return retval


def same_protein(self, prot, name, prot2, input='protein'):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Critical)
    self.msg.setWindowTitle("Error")
    self.msg.setText('This %s has the same name "%s" than %s.                             ' % (prot, name, prot2))
    self.msg.setInformativeText('Please, select a new %s' % input)
    self.msg.setStandardButtons(QMessageBox.Ok)
    retval = self.msg.exec_()
    return retval


# (5')
def no_ADzn_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("images/amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Information)
    self.msg.setWindowTitle("Error")
    self.msg.setText('Protein with Zn, but AutoDock4Zn is not selected')

    self.msg.setInformativeText(
        'The option "Protein with the Zn" was selected, however the current program is %s. Do you wish to change to AutoDock4Zn program? ' % self.docking_program)
    self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    retval = self.msg.exec_()
    return retval


# (6)
def more_mol_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("images/amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Critical)
    self.msg.setWindowTitle("Error")
    self.msg.setText("It's not possible to create the working directory")
    self.msg.setInformativeText(
        "It's possible that the selected directory is being used or do not have permission to write on it")
    self.msg.setStandardButtons(QMessageBox.Ok)
    # self.msg.buttonClicked.connect(lambda: select_option(self))
    retval = self.msg.exec_()


# (7)
def sel_res_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("images/amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Critical)
    self.msg.setWindowTitle("Error")
    self.msg.setText("It's not possible to create the working directory")
    self.msg.setInformativeText(
        "It's possible that the selected directory is being used or do not have permission to write on it")
    self.msg.setStandardButtons(QMessageBox.Ok)
    # self.msg.buttonClicked.connect(lambda: select_option(self))
    retval = self.msg.exec_()


# (8)
def ADzn_no_metal_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("images/amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Critical)
    self.msg.setWindowTitle("Error")
    self.msg.setText("It's not possible to create the working directory")
    self.msg.setInformativeText(
        "It's possible that the selected directory is being used or do not have permission to write on it")
    self.msg.setStandardButtons(QMessageBox.Ok)
    # self.msg.buttonClicked.connect(lambda: select_option(self))
    self.msg.exec_()


def prot_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("images/amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Warning)
    self.msg.setWindowTitle("Warning")
    self.msg.setText(
        "The protein file is already defined.                                                                ")
    self.msg.setInformativeText(
        "Do you wish to define a new protein file?. The previous protein file will be eliminated")
    self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    self.msg.setMinimumSize(450, 150)
    retval = self.msg.exec_()
    return retval


def amdock_file_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("images/amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Warning)
    self.msg.setWindowTitle("Warning")
    self.msg.setText(
        "Actually a file amdock is being used.                                                                ")
    self.msg.setInformativeText("Do you wish to change it?.")
    self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    self.msg.setMinimumSize(450, 150)
    retval = self.msg.exec_()
    return retval


def lig_warning(self):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("images/amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Warning)
    self.msg.setWindowTitle("Warning")
    self.msg.setText(
        "The ligand file is already defined.                                                                 ")
    self.msg.setInformativeText(
        "Do you wish to define a new ligand file?. The previous ligand file will be eliminated")
    self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    self.msg.setMinimumSize(450, 150)
    retval = self.msg.exec_()
    return retval


def not_find_warning(self, ele, loc):
    self.msg = QMessageBox()
    self.msg.setWindowIcon(QIcon(QPixmap("images/amdock_icon.png")))
    self.msg.setIcon(QMessageBox.Critical)
    self.msg.setWindowTitle("Error")
    self.msg.setText(
        "The element %s does not find in %s                                                                " % (
            ele, loc))
    self.msg.setInformativeText(
        "Please, make sure that the directory of the project contains all archives and folders, as well as the amdock file with the names of those files.")
    self.msg.setStandardButtons(QMessageBox.Ok)
    self.msg.setMinimumSize(450, 150)
    retval = self.msg.exec_()
    return retval
