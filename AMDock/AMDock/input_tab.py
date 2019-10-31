from warning import wdir2_warning, prot_warning, lig_warning, stop_warning, error_warning, smallbox_warning, \
    reset_warning, amdock_file_warning, define_wdir_loc
from PyQt4 import QtGui, QtCore
import shutil, os, glob, re, Queue
from result2tab import Result_Analysis, Scoring2table
from some_slots import progress
from tools import GridDefinition, Fix_PQR
from variables import Variables, WorkersAndScripts
from command_runner import Worker

__version__ = "1.0 For Windows and Linux"


class Program_body(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Program_body, self).__init__(parent)
        self.setObjectName("program_body")
        self.parent = parent
        with open(self.parent.objects.style_file) as f:
            self.setStyleSheet(f.read())

        self.part = 0
        self.total = 0
        self.grid = 0
        self.need_grid = True
        self.need_gridB = True
        self.build = self.buildB = False
        self.process_list = []
        self.ws = WorkersAndScripts()
        self.wdir_loc = None

        self.sc_area = QtGui.QScrollArea(self)
        self.sc_area_widget = QtGui.QWidget()
        self.sc_area_widget.setMinimumHeight(200)

        # **project_box
        self.project_box = QtGui.QGroupBox(self.sc_area_widget)
        self.project_box.setObjectName("project_box")
        self.project_box.setTitle("Project")
        self.project_box.setToolTip(self.parent.tt.project_tt)

        self.project_label = QtGui.QLabel(self.project_box)
        self.project_label.setText("Project Name:")

        self.project_text = QtGui.QLineEdit(self.project_box)
        self.project_text.setObjectName("project_text")
        self.project_text.setPlaceholderText(self.parent.v.project_name)
        self.proj_name_validator = QtGui.QRegExpValidator(QtCore.QRegExp("\\S+"))
        self.project_text.setValidator(self.proj_name_validator)

        self.wdir_button = QtGui.QPushButton(self.project_box)
        self.wdir_button.setObjectName("wdir_button")
        self.wdir_button.setText("Project Folder")
        self.wdir_button.clicked.connect(lambda: self.load_file(self.wdir_button))

        self.wdir_text = QtGui.QLineEdit(self.project_box)
        self.wdir_text.setReadOnly(True)
        self.wdir_text.setObjectName("wdir_text")
        self.wdir_text.setPlaceholderText("Location for the project")

        self.proj_loc_label = QtGui.QLabel()
        self.proj_loc_label.hide()

        self.project_layout = QtGui.QGridLayout()
        self.project_layout.addWidget(self.project_label, 0, 0)
        self.project_layout.addWidget(self.project_text, 0, 1, 1, 1)
        self.project_layout.addWidget(self.wdir_button, 1, 0)
        self.project_layout.addWidget(self.wdir_text, 1, 1, 1, 1)
        self.project_layout.addWidget(self.proj_loc_label, 2, 0, 1, 3)

        self.create_project = QtGui.QPushButton('Create \nProject')
        self.create_project.setObjectName('create_project')
        self.create_project.clicked.connect(lambda: self.load_file(self.create_project))

        self.project_box_layout = QtGui.QHBoxLayout(self.project_box)
        self.project_box_layout.addLayout(self.project_layout, 10)
        self.project_box_layout.addWidget(self.create_project)

        # **Input_box
        self.input_box = QtGui.QGroupBox(self.sc_area_widget)
        self.input_box.setObjectName("input_box")
        self.input_box.setTitle("Input")
        # self.input_box.setEnabled(False)
        self.input_box.setToolTip(self.parent.tt.input_tt)

        self.pH_label = QtGui.QLabel(self.input_box)
        self.pH_label.setObjectName("ph_button")
        self.pH_label.setText("Set pH:")

        self.pH_value = QtGui.QDoubleSpinBox(self.input_box)
        self.pH_value.setAlignment(QtCore.Qt.AlignCenter)
        self.pH_value.setDecimals(1)
        self.pH_value.setMinimum(0)
        self.pH_value.setMaximum(14)
        self.pH_value.setSingleStep(0.1)
        self.pH_value.setValue(self.parent.v.pH)
        self.pH_value.setObjectName("pH_value")

        self.docking_mode = QtGui.QButtonGroup(self.input_box)

        self.simple_docking = QtGui.QRadioButton('Simple Docking', self.input_box)
        self.simple_docking.setObjectName("simple_docking")
        self.simple_docking.setChecked(True)
        self.docking_mode.addButton(self.simple_docking, 1)

        self.cross_reaction = QtGui.QRadioButton('Off-Target Docking', self.input_box)
        self.cross_reaction.setObjectName("cross_reaction")
        self.docking_mode.addButton(self.cross_reaction, 2)

        self.rescoring = QtGui.QRadioButton('Scoring', self.input_box)
        self.rescoring.setObjectName("rescoring")
        self.docking_mode.addButton(self.rescoring, 3)

        self.protein_button = QtGui.QPushButton(self.input_box)
        self.protein_button.setObjectName("protein_buttonA")
        self.protein_button.setText("Protein")
        self.protein_button.clicked.connect(lambda: self.load_file(self.protein_button))

        self.protein_text = QtGui.QLineEdit(self.input_box)
        self.protein_text.setObjectName("protein_text")
        self.protein_text.setReadOnly(True)
        self.protein_text.setPlaceholderText('target protein')

        self.protein_label = QtGui.QLabel(self.input_box)
        self.protein_label.hide()

        self.protein_buttonB = QtGui.QPushButton(self.input_box)
        self.protein_buttonB.setObjectName("protein_buttonB")
        self.protein_buttonB.setText("Off-Target")
        self.protein_buttonB.hide()
        self.protein_buttonB.clicked.connect(lambda: self.load_file(self.protein_buttonB))

        self.protein_textB = QtGui.QLineEdit(self.input_box)
        self.protein_textB.setObjectName("protein_textB")
        self.protein_textB.setReadOnly(True)
        self.protein_textB.setPlaceholderText('off-target protein')
        self.protein_textB.hide()

        self.protein_labelB = QtGui.QLabel(self.input_box)
        self.protein_labelB.hide()

        self.ligand_button = QtGui.QPushButton(self.input_box)
        self.ligand_button.setObjectName("ligand_button")
        self.ligand_button.setText("Ligand")
        self.ligand_button.clicked.connect(lambda: self.load_file(self.ligand_button))

        self.ligand_text = QtGui.QLineEdit(self.input_box)
        self.ligand_text.setObjectName("ligand_text")
        self.ligand_text.setReadOnly(True)
        self.ligand_text.setPlaceholderText('ligand')

        self.ligand_label = QtGui.QLabel(self.input_box)
        self.ligand_label.hide()

        self.prep_rec_lig_button = QtGui.QPushButton(self.input_box)
        self.prep_rec_lig_button.setObjectName("prep_rec_lig_button")
        self.prep_rec_lig_button.setText("Prepare\nInput")
        self.prep_rec_lig_button.setEnabled(False)

        self.flags_layout = QtGui.QHBoxLayout()
        self.flags_layout.addWidget(self.pH_label)
        self.flags_layout.addWidget(self.pH_value)
        self.flags_layout.addWidget(self.simple_docking)
        self.flags_layout.addWidget(self.cross_reaction)
        self.flags_layout.addWidget(self.rescoring)
        self.flags_layout.addStretch(1)

        self.input_layout = QtGui.QGridLayout()
        self.input_layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.input_layout.addWidget(self.protein_button, 0, 0)
        self.input_layout.addWidget(self.protein_text, 0, 1)
        self.input_layout.addWidget(self.protein_label, 1, 1)

        self.input_layout.addWidget(self.protein_buttonB, 2, 0)
        self.input_layout.addWidget(self.protein_textB, 2, 1)
        self.input_layout.addWidget(self.protein_labelB, 3, 1)
        self.input_layout.addWidget(self.ligand_button, 4, 0)
        self.input_layout.addWidget(self.ligand_text, 4, 1)
        self.input_layout.addWidget(self.ligand_label, 5, 1)

        self.content_layout = QtGui.QHBoxLayout()
        self.content_layout.addLayout(self.input_layout)
        self.content_layout.addWidget(self.prep_rec_lig_button)

        self.input_box_layout = QtGui.QVBoxLayout(self.input_box)
        self.input_box_layout.addLayout(self.flags_layout)
        self.input_box_layout.addLayout(self.content_layout)

        # **Grid_box
        self.grid_box = QtGui.QGroupBox(self.sc_area_widget)
        self.grid_box.setObjectName("grid_box")
        self.grid_box.setTitle("Search Space")
        # self.grid_box.setEnabled(False)
        self.grid_box.setToolTip(self.parent.tt.grid_tt)

        self.protein_column_label = QtGui.QLabel('Target', self.grid_box)
        self.protein_column_label.setAlignment(QtCore.Qt.AlignCenter)

        self.protein_column_group_btnA = QtGui.QButtonGroup(self.grid_box)

        self.btnA_auto = QtGui.QRadioButton(self.grid_box)
        self.btnA_auto.setObjectName('btnA_auto')
        self.btnA_auto.setChecked(True)
        self.protein_column_group_btnA.addButton(self.btnA_auto, 1)
        self.btnA_auto.toggled.connect(lambda: self.grid_prot(self.btnA_auto))

        self.btnA_res = QtGui.QRadioButton(self.grid_box)
        self.protein_column_group_btnA.addButton(self.btnA_res, 2)
        self.btnA_res.setObjectName('btnA_res')
        self.btnA_res.toggled.connect(lambda: self.grid_prot(self.btnA_res))

        self.btnA_lig = QtGui.QRadioButton(self.grid_box)
        self.btnA_lig.setObjectName('btnA_lig')
        self.protein_column_group_btnA.addButton(self.btnA_lig, 3)
        self.btnA_lig.toggled.connect(lambda: self.grid_prot(self.btnA_lig))

        self.btnA_user = QtGui.QRadioButton(self.grid_box)
        self.protein_column_group_btnA.addButton(self.btnA_user, 4)
        self.btnA_user.setObjectName('btnA_user')
        self.btnA_user.toggled.connect(lambda: self.grid_prot(self.btnA_user))

        self.protein1_column_label = QtGui.QLabel('Off-Target', self.grid_box)
        self.protein1_column_label.hide()
        self.protein1_column_label.setAlignment(QtCore.Qt.AlignCenter)

        self.protein_column_group_btnB = QtGui.QButtonGroup(self.grid_box)

        self.btnB_auto = QtGui.QRadioButton(self.grid_box)
        self.btnB_auto.setChecked(True)
        self.protein_column_group_btnB.addButton(self.btnB_auto, 1)
        self.btnB_auto.hide()
        self.btnB_auto.toggled.connect(lambda: self.grid_prot(self.btnB_auto))

        self.btnB_res = QtGui.QRadioButton(self.grid_box)
        self.btnB_res.toggled.connect(lambda: self.grid_prot(self.btnB_res))

        self.protein_column_group_btnB.addButton(self.btnB_res, 2)
        self.btnB_res.hide()

        self.btnB_lig = QtGui.QRadioButton(self.grid_box)
        self.protein_column_group_btnB.addButton(self.btnB_lig, 3)
        self.btnB_lig.hide()
        self.btnB_lig.toggled.connect(lambda: self.grid_prot(self.btnB_lig))

        self.btnB_user = QtGui.QRadioButton(self.grid_box)
        self.protein_column_group_btnB.addButton(self.btnB_user, 4)
        self.btnB_user.hide()
        self.btnB_user.toggled.connect(lambda: self.grid_prot(self.btnB_user))

        self.grid_auto_cr = QtGui.QLabel(self.grid_box)
        self.grid_auto_cr.setText("Automatic")

        self.grid_predef_cr = QtGui.QLabel(self.grid_box)
        self.grid_predef_cr.setText("Center on Residue(s)")

        self.grid_predef_text = QtGui.QLineEdit(self.grid_box)
        self.grid_predef_text.setObjectName("grid_predef_text")
        self.grid_predef_text.setPlaceholderText('CHN:RES:NUM,...,CHN:RES:NUM (chain:residue:number of residue)')
        self.grid_predef_text.hide()
        self.grid_predef_text.textChanged.connect(lambda: self.check_res(self.grid_predef_text))

        self.grid_predef_textB = QtGui.QLineEdit(self.grid_box)
        self.grid_predef_textB.setObjectName("grid_predef_textB")
        self.grid_predef_textB.setPlaceholderText('CHN:RES:NUM,...,CHN:RES:NUM (chain:residue:number of residue)')
        self.grid_predef_textB.hide()
        self.grid_predef_textB.textChanged.connect(lambda: self.check_res(self.grid_predef_textB))

        self.grid_by_lig_cr = QtGui.QLabel(self.grid_box)
        self.grid_by_lig_cr.setText("Center on Ligand")

        self.lig_list = QtGui.QComboBox(self.grid_box)
        self.lig_list.setObjectName("lig_list")
        self.lig_list.hide()
        self.lig_list.currentIndexChanged.connect(lambda: self.lig_select(self.lig_list))

        self.lig_listB = QtGui.QComboBox(self.grid_box)
        self.lig_listB.setObjectName("lig_listB")
        self.lig_listB.hide()
        self.lig_listB.currentIndexChanged.connect(lambda: self.lig_select(self.lig_listB))

        self.grid_user_cr = QtGui.QLabel(self.grid_box)
        self.grid_user_cr.setText('Box')

        self.coor_box = QtGui.QGroupBox(self.grid_box)
        self.coor_box.setTitle("Center")
        self.coor_box.setAlignment(QtCore.Qt.AlignCenter)
        self.coor_box.hide()

        self.coor_x_label = QtGui.QLabel(self.coor_box)
        self.coor_x_label.setText('X:')
        self.coor_x = QtGui.QLineEdit(self.coor_box)
        self.coor_x.setValidator(QtGui.QDoubleValidator(-100, 100, 2))
        self.coor_x.setMaxLength(5)
        self.coor_x.setObjectName('coor_x')
        self.coor_x.textChanged.connect(self.check_grid)

        self.coor_y_label = QtGui.QLabel(self.coor_box)
        self.coor_y_label.setText('Y:')
        self.coor_y = QtGui.QLineEdit(self.coor_box)
        self.coor_y.setValidator(QtGui.QDoubleValidator(-100, 100, 2))
        self.coor_y.setMaxLength(5)
        self.coor_y.setObjectName('coor_y')
        self.coor_y.textChanged.connect(self.check_grid)

        self.coor_z_label = QtGui.QLabel(self.coor_box)
        self.coor_z_label.setText('Z:')
        self.coor_z = QtGui.QLineEdit(self.coor_box)
        self.coor_z.setValidator(QtGui.QDoubleValidator(-100, 100, 2))
        self.coor_z.setMaxLength(5)
        self.coor_z.setObjectName('coor_z')
        self.coor_z.textChanged.connect(self.check_grid)

        self.size_box = QtGui.QGroupBox(self.grid_box)
        self.size_box.setTitle("Size")
        self.size_box.setAlignment(QtCore.Qt.AlignCenter)
        self.size_box.hide()

        self.size_x_label = QtGui.QLabel(self.size_box)
        self.size_x_label.setText('X:')
        self.size_x = QtGui.QLineEdit(self.size_box)
        self.size_x.setValidator(QtGui.QIntValidator(8, 150))
        self.size_x.setMaxLength(5)
        self.size_x.setObjectName('size_x')
        self.size_x.textChanged.connect(self.check_grid)

        self.size_y_label = QtGui.QLabel(self.size_box)
        self.size_y_label.setText('Y:')
        self.size_y = QtGui.QLineEdit(self.size_box)
        self.size_y.setValidator(QtGui.QIntValidator(8, 150))
        self.size_y.setMaxLength(5)
        self.size_y.setObjectName('size_y')
        self.size_y.textChanged.connect(self.check_grid)

        self.size_z_label = QtGui.QLabel(self.size_box)
        self.size_z_label.setText('Z:')
        self.size_z = QtGui.QLineEdit(self.size_box)
        self.size_z.setValidator(QtGui.QIntValidator(8, 150))
        self.size_z.setMaxLength(5)
        self.size_z.setObjectName('size_z')
        self.size_z.textChanged.connect(self.check_grid)

        self.coor_boxB = QtGui.QGroupBox(self.grid_box)
        self.coor_boxB.setTitle("Center")
        self.coor_boxB.setAlignment(QtCore.Qt.AlignCenter)
        self.coor_boxB.hide()

        self.coor_x_labelB = QtGui.QLabel(self.coor_boxB)
        self.coor_x_labelB.setText('X:')
        self.coor_xB = QtGui.QLineEdit(self.coor_boxB)
        self.coor_xB.setValidator(QtGui.QDoubleValidator(-100, 100, 2))
        self.coor_xB.setMaxLength(6)
        self.coor_xB.setObjectName('coor_xB')
        self.coor_xB.textChanged.connect(self.check_grid)

        self.coor_y_labelB = QtGui.QLabel(self.coor_boxB)
        self.coor_y_labelB.setText('Y:')
        self.coor_yB = QtGui.QLineEdit(self.coor_boxB)
        self.coor_yB.setValidator(QtGui.QDoubleValidator(-100, 100, 2))
        self.coor_yB.setMaxLength(6)
        self.coor_yB.setObjectName('coor_yB')
        self.coor_yB.textChanged.connect(self.check_grid)

        self.coor_z_labelB = QtGui.QLabel(self.coor_boxB)
        self.coor_z_labelB.setText('Z:')
        self.coor_zB = QtGui.QLineEdit(self.coor_boxB)
        self.coor_zB.setValidator(QtGui.QDoubleValidator(-100, 100, 2))
        self.coor_zB.setMaxLength(6)
        self.coor_zB.setObjectName('coor_zB')
        self.coor_zB.textChanged.connect(self.check_grid)

        self.size_boxB = QtGui.QGroupBox(self.grid_box)
        self.size_boxB.setTitle("Size")
        self.size_boxB.setAlignment(QtCore.Qt.AlignCenter)
        self.size_boxB.hide()

        self.size_x_labelB = QtGui.QLabel(self.size_boxB)
        self.size_x_labelB.setText('X:')
        self.size_xB = QtGui.QLineEdit(self.size_boxB)
        self.size_xB.setValidator(QtGui.QIntValidator(8, 150))
        self.size_xB.setMaxLength(6)
        self.size_xB.setObjectName('size_xB')
        self.size_xB.textChanged.connect(self.check_grid)

        self.size_y_labelB = QtGui.QLabel(self.size_boxB)
        self.size_y_labelB.setText('Y:')
        self.size_yB = QtGui.QLineEdit(self.size_boxB)
        self.size_yB.setValidator(QtGui.QIntValidator(8, 150))
        self.size_yB.setMaxLength(6)
        self.size_yB.setObjectName('size_yB')
        self.size_yB.textChanged.connect(self.check_grid)

        self.size_z_labelB = QtGui.QLabel(self.size_boxB)
        self.size_z_labelB.setText('Z:')
        self.size_zB = QtGui.QLineEdit(self.size_boxB)
        self.size_zB.setValidator(QtGui.QIntValidator(8, 150))
        self.size_zB.setMaxLength(6)
        self.size_zB.setObjectName('size_zB')
        self.size_zB.textChanged.connect(self.check_grid)
        self.spacer = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        self.center_layout = QtGui.QHBoxLayout(self.coor_box)
        self.center_layout.setContentsMargins(0, 0, 0, 0)
        self.center_layout.addWidget(self.coor_x_label)
        self.center_layout.addWidget(self.coor_x)
        self.center_layout.addWidget(self.coor_y_label)
        self.center_layout.addWidget(self.coor_y)
        self.center_layout.addWidget(self.coor_z_label)
        self.center_layout.addWidget(self.coor_z)
        self.center_layoutB = QtGui.QHBoxLayout(self.coor_boxB)
        self.center_layoutB.setContentsMargins(0, 0, 0, 0)
        self.center_layoutB.addWidget(self.coor_x_labelB)
        self.center_layoutB.addWidget(self.coor_xB)
        self.center_layoutB.addWidget(self.coor_y_labelB)
        self.center_layoutB.addWidget(self.coor_yB)
        self.center_layoutB.addWidget(self.coor_z_labelB)
        self.center_layoutB.addWidget(self.coor_zB)

        self.size_layout = QtGui.QHBoxLayout(self.size_box)
        self.size_layout.setContentsMargins(0, 0, 0, 0)
        self.size_layout.addWidget(self.size_x_label)
        self.size_layout.addWidget(self.size_x)
        self.size_layout.addWidget(self.size_y_label)
        self.size_layout.addWidget(self.size_y)
        self.size_layout.addWidget(self.size_z_label)
        self.size_layout.addWidget(self.size_z)
        self.size_layoutB = QtGui.QHBoxLayout(self.size_boxB)
        self.size_layoutB.setContentsMargins(0, 0, 0, 0)
        self.size_layoutB.addWidget(self.size_x_labelB)
        self.size_layoutB.addWidget(self.size_xB)
        self.size_layoutB.addWidget(self.size_y_labelB)
        self.size_layoutB.addWidget(self.size_yB)
        self.size_layoutB.addWidget(self.size_z_labelB)
        self.size_layoutB.addWidget(self.size_zB)

        self.bind_site_button = QtGui.QPushButton(self.grid_box)
        self.bind_site_button.setObjectName("bind_site_button")
        self.bind_site_button.setText("Define\nSearch Space")
        self.bind_site_button.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))

        self.grid_pymol_button = QtGui.QPushButton(self.grid_box)
        self.grid_pymol_button.setObjectName("grid_pymol_button")
        self.grid_pymol_button.setText('Show in PyMol')
        self.grid_pymol_button.clicked.connect(lambda: self.grid_actions(self.grid_pymol_button))
        self.grid_pymol_button.setEnabled(False)

        self.grid_pymol_buttonB = QtGui.QPushButton(self.grid_box)
        self.grid_pymol_buttonB.setObjectName("grid_pymol_buttonB")
        self.grid_pymol_buttonB.setText("Show in PyMol")
        self.grid_pymol_buttonB.hide()
        self.grid_pymol_buttonB.clicked.connect(lambda: self.grid_actions(self.grid_pymol_buttonB))
        self.grid_pymol_buttonB.setEnabled(False)

        self.reset_grid_button = QtGui.QPushButton(self.grid_box)
        self.reset_grid_button.setObjectName("reset_grid_button")
        self.reset_grid_button.setText("Reset")
        self.reset_grid_button.clicked.connect(lambda: self.grid_actions(self.reset_grid_button))
        self.reset_grid_button.setEnabled(False)

        self.reset_grid_buttonB = QtGui.QPushButton(self.grid_box)
        self.reset_grid_buttonB.setObjectName("reset_grid_buttonB")
        self.reset_grid_buttonB.setText("Reset")
        self.reset_grid_buttonB.hide()
        self.reset_grid_buttonB.clicked.connect(lambda: self.grid_actions(self.reset_grid_buttonB))
        self.reset_grid_buttonB.setEnabled(False)

        self.checker_icon = QtGui.QLabel(self.grid_box)
        self.checker_icon.setPixmap(QtGui.QPixmap(self.parent.objects.error_checker))
        self.checker_icon.hide()

        self.checker_icon_ok = QtGui.QLabel(self.grid_box)
        self.checker_icon_ok.setPixmap(QtGui.QPixmap(self.parent.objects.error_checker_ok))
        self.checker_icon_ok.hide()

        self.run_button = QtGui.QPushButton(self)
        self.run_button.setObjectName("run_button")
        self.run_button.setText("Run Docking")
        self.run_button.setEnabled(False)

        self.run_scoring = QtGui.QPushButton(self)
        self.run_scoring.setObjectName("run_scoring")
        self.run_scoring.setText("Run Scoring")
        self.run_scoring.setEnabled(False)
        self.run_scoring.hide()

        self.stop_button = QtGui.QPushButton(self)
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setText("Stop Docking")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_docking)

        self.non_button = QtGui.QPushButton(self)
        self.non_button.setObjectName("non_button")
        self.non_button.setText("")
        self.non_button.setEnabled(False)
        self.non_button.hide()

        self.reset_button = QtGui.QPushButton(self)
        self.reset_button.setObjectName("reset_button")
        self.reset_button.setText("  Reset")
        self.reset_button.setIcon(QtGui.QIcon(QtGui.QPixmap(self.parent.objects.reset_icon)))
        self.reset_button.setEnabled(True)
        self.reset_button.clicked.connect(self.reset_function)

        self.progressBar = QtGui.QProgressBar(self)
        self.progressBar.setValue(0)
        self.progressBar.setAlignment(QtCore.Qt.AlignCenter)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setTextDirection(QtGui.QProgressBar.TopToBottom)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setFormat("%p%")

        self.progressBar_label = QtGui.QLabel(self)
        font3 = QtGui.QFont()
        font3.setPointSize(6)

        self.p1 = QtGui.QLabel('|')
        self.p1.setFont(font3)
        self.p2 = QtGui.QLabel('|')
        self.p2.setFont(font3)
        self.p3 = QtGui.QLabel('|')
        self.p3.setFont(font3)
        self.p4 = QtGui.QLabel('|')
        self.p4.setFont(font3)
        self.p5 = QtGui.QLabel('|')
        self.p5.setFont(font3)
        self.init_conf = QtGui.QLabel('Init Conf')
        self.init_conf.setFont(font3)
        self.input_files = QtGui.QLabel('Prep. Input Files')
        self.input_files.setFont(font3)
        self.search_space = QtGui.QLabel('Search Space Definition')
        self.search_space.setFont(font3)
        self.mol_docking = QtGui.QLabel('Molecular Docking Simulation')
        self.mol_docking.setFont(font3)

        self.label_prog = QtGui.QHBoxLayout()
        self.label_prog.setContentsMargins(0, 0, 0, 0)
        self.label_prog.setMargin(0)
        self.label_prog.addWidget(self.init_conf, 9.8, QtCore.Qt.AlignCenter)
        self.label_prog.addWidget(self.p2)
        self.label_prog.addWidget(self.input_files, 14.8, QtCore.Qt.AlignCenter)
        self.label_prog.addWidget(self.p3)
        self.label_prog.addWidget(self.search_space, 24.8, QtCore.Qt.AlignCenter)
        self.label_prog.addWidget(self.p4)
        self.label_prog.addWidget(self.mol_docking, 50, QtCore.Qt.AlignCenter)

        self.checker_icon = QtGui.QLabel(self.grid_box)
        self.checker_icon.setPixmap(QtGui.QPixmap(self.parent.objects.error_checker))
        self.checker_icon.hide()

        self.checker_iconB = QtGui.QLabel(self.grid_box)
        self.checker_iconB.setPixmap(QtGui.QPixmap(self.parent.objects.error_checker))
        self.checker_iconB.hide()

        self.checker_icon_ok = QtGui.QLabel(self.grid_box)
        self.checker_icon_ok.setPixmap(QtGui.QPixmap(self.parent.objects.error_checker_ok))
        self.checker_icon_ok.hide()

        self.checker_icon_okB = QtGui.QLabel(self.grid_box)
        self.checker_icon_okB.setPixmap(QtGui.QPixmap(self.parent.objects.error_checker_ok))
        self.checker_icon_okB.hide()

        self.grid_icon = QtGui.QLabel()
        self.grid_icon.setPixmap(QtGui.QPixmap(self.parent.objects.error_checker))
        self.grid_icon.hide()

        self.grid_iconB = QtGui.QLabel(self.grid_box)
        self.grid_iconB.setPixmap(QtGui.QPixmap(self.parent.objects.error_checker))
        self.grid_iconB.hide()

        self.grid_icon_ok = QtGui.QLabel(self.grid_box)
        self.grid_icon_ok.setPixmap(QtGui.QPixmap(self.parent.objects.error_checker_ok))
        self.grid_icon_ok.hide()

        self.grid_icon_okB = QtGui.QLabel(self.grid_box)
        self.grid_icon_okB.setPixmap(QtGui.QPixmap(self.parent.objects.error_checker_ok))
        self.grid_icon_okB.hide()

        self.res_text = QtGui.QHBoxLayout()
        self.res_text.addWidget(self.grid_predef_text, 1)
        self.res_text.addWidget(self.checker_icon_ok)
        self.res_text.addWidget(self.checker_icon)
        self.res_lay = QtGui.QVBoxLayout()
        self.res_lay.addWidget(self.btnA_res, 0, QtCore.Qt.AlignCenter)
        self.res_lay.addLayout(self.res_text)

        self.res_textB = QtGui.QHBoxLayout()
        self.res_textB.addWidget(self.grid_predef_textB, 1)
        self.res_textB.addWidget(self.checker_icon_okB, 0)
        self.res_textB.addWidget(self.checker_iconB, 0)
        self.res_layB = QtGui.QVBoxLayout()
        self.res_layB.addWidget(self.btnB_res, 0, QtCore.Qt.AlignCenter)
        self.res_layB.addLayout(self.res_textB)

        self.lig_lay = QtGui.QVBoxLayout()
        self.lig_lay.addWidget(self.btnA_lig, 0, QtCore.Qt.AlignCenter)
        self.lig_lay.addWidget(self.lig_list, 1)
        self.lig_layB = QtGui.QVBoxLayout()
        self.lig_layB.addWidget(self.btnB_lig, 0, QtCore.Qt.AlignCenter)
        self.lig_layB.addWidget(self.lig_listB, 1)

        self.coor_box_layout = QtGui.QHBoxLayout()
        self.coor_box_layout.addWidget(self.coor_box, 1)
        self.coor_box_layout.addWidget(self.size_box, 1)
        self.coor_box_layout.addWidget(self.grid_icon)
        self.coor_box_layout.addWidget(self.grid_icon_ok)
        self.coor_lay = QtGui.QVBoxLayout()
        self.coor_lay.addWidget(self.btnA_user, 0, QtCore.Qt.AlignCenter)
        self.coor_lay.addLayout(self.coor_box_layout)

        self.coor_boxB_layout = QtGui.QHBoxLayout()
        self.coor_boxB_layout.addWidget(self.coor_boxB, 1)
        self.coor_boxB_layout.addWidget(self.size_boxB, 1)
        self.coor_boxB_layout.addWidget(self.grid_iconB)
        self.coor_boxB_layout.addWidget(self.grid_icon_okB)

        self.coor_layB = QtGui.QVBoxLayout()
        self.coor_layB.addWidget(self.btnB_user, 0, QtCore.Qt.AlignCenter)
        self.coor_layB.addLayout(self.coor_boxB_layout)

        self.conf_buttons = QtGui.QHBoxLayout()
        self.conf_buttons.addWidget(self.grid_pymol_button)
        self.conf_buttons.addWidget(self.reset_grid_button)
        self.conf_buttonsB = QtGui.QHBoxLayout()
        self.conf_buttonsB.addWidget(self.grid_pymol_buttonB)
        self.conf_buttonsB.addWidget(self.reset_grid_buttonB)

        self.autoligand_table = QtGui.QTableWidget()
        self.autoligand_table.setColumnCount(2)
        self.autoligand_table.setHorizontalHeaderLabels(["Total Volume (A**3)","EPV (Kcal/mol A**3)"])
        self.autoligand_table.setRowCount(10)
        self.autoligand_table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

        self.autolig_layout = QtGui.QHBoxLayout()
        self.autolig_layout.addWidget(self.autoligand_table, 1)

        self.autoligand_tableB = QtGui.QTableWidget()
        self.autoligand_tableB.setColumnCount(2)
        self.autoligand_tableB.setHorizontalHeaderLabels(["Total Volume (A**3)","EPV (Kcal/mol A**3)"])
        self.autoligand_tableB.setRowCount(10)
        self.autoligand_tableB.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

        self.autolig_layoutB = QtGui.QHBoxLayout()
        self.autolig_layoutB.addWidget(self.autoligand_tableB, 1)

        self.all_options = QtGui.QGridLayout()
        self.all_options.setSizeConstraint(QtGui.QLayout.SetFixedSize)

        self.all_options.setColumnStretch(1, 1)  # make column 1 and 2 regular width
        self.all_options.addItem(self.spacer, 0, 0)
        self.all_options.addWidget(self.protein_column_label, 0, 1, 1, 1, QtCore.Qt.AlignCenter)
        self.all_options.addWidget(self.protein1_column_label, 0, 2, 1, 1, QtCore.Qt.AlignCenter)
        self.all_options.addItem(self.spacer, 0, 3)

        self.all_options.addWidget(self.grid_auto_cr, 1, 0)
        self.all_options.addWidget(self.btnA_auto, 1, 1, 1, 1, QtCore.Qt.AlignCenter)
        self.all_options.addWidget(self.btnB_auto, 1, 2, 1, 1, QtCore.Qt.AlignCenter)
        self.all_options.addLayout(self.autolig_layout, 2, 1, 1, 1, QtCore.Qt.AlignCenter)
        self.all_options.addLayout(self.autolig_layoutB, 2, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.all_options.addWidget(self.grid_predef_cr, 3, 0)
        self.all_options.addLayout(self.res_lay, 3, 1, 1, 1, QtCore.Qt.AlignCenter)
        self.all_options.addLayout(self.res_layB, 3, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.all_options.addWidget(self.grid_by_lig_cr, 4, 0)
        self.all_options.addLayout(self.lig_lay, 4, 1, 1, 1, QtCore.Qt.AlignCenter)
        self.all_options.addLayout(self.lig_layB, 4, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.all_options.addWidget(self.grid_user_cr, 5, 0)
        self.all_options.addLayout(self.coor_lay, 5, 1, 1, 1, QtCore.Qt.AlignCenter)
        self.all_options.addLayout(self.coor_layB, 5, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.all_options.addItem(self.spacer, 6, 0)
        self.all_options.addLayout(self.conf_buttons, 6, 1, 1, 1, QtCore.Qt.AlignCenter)
        self.all_options.addLayout(self.conf_buttonsB, 6, 2, 1, 1, QtCore.Qt.AlignCenter)

        self.binding_layout = QtGui.QVBoxLayout()
        self.binding_layout.addStretch(1)
        self.binding_layout.addWidget(self.bind_site_button)
        self.binding_layout.addStretch(1)

        self.grid_content = QtGui.QHBoxLayout(self.grid_box)
        self.grid_content.addLayout(self.all_options, 1)
        self.grid_content.addLayout(self.binding_layout)

        self.worker = Worker()
        self.worker.readyReadStandardOutput.connect(self.readStdOutput)
        self.worker.readyReadStandardError.connect(self.readStdError)
        self.worker.prog_started.connect(self.prog_show)
        self.worker.prog_finished.connect(self.process_progress)
        self.worker.prog_finished.connect(self.run_queue)
        self.worker.queue_finished.connect(self.check_queue)

        self.cross_reaction.toggled.connect(lambda: self.simulation_form(self.cross_reaction))
        self.simple_docking.toggled.connect(lambda: self.simulation_form(self.simple_docking))
        self.rescoring.toggled.connect(lambda: self.simulation_form(self.rescoring))
        self.prep_rec_lig_button.clicked.connect(self.prepare_receptor)
        self.bind_site_button.clicked.connect(self.binding_site)
        self.run_button.clicked.connect(self.start_docking_prog)
        self.run_scoring.clicked.connect(self.scoring)

        self.pH_value.valueChanged.connect(lambda: self.values(self.pH_value))

        self.reset_button_layout = QtGui.QHBoxLayout()
        self.reset_button_layout.addStretch(1)
        self.reset_button_layout.addWidget(self.reset_button)
        self.reset_button_layout.addStretch(1)

        self.progressbar_layout = QtGui.QVBoxLayout()
        self.progressbar_layout.addLayout(self.label_prog)
        self.progressbar_layout.addWidget(self.progressBar)
        self.progressbar_layout.addLayout(self.reset_button_layout)

        self.progress_layout = QtGui.QHBoxLayout()
        self.progress_layout.addWidget(self.stop_button)
        self.progress_layout.addWidget(self.non_button)
        self.progress_layout.addLayout(self.progressbar_layout)
        self.progress_layout.addWidget(self.run_button)
        self.progress_layout.addWidget(self.run_scoring)

        self.sc_area_widget_layout = QtGui.QVBoxLayout(self.sc_area_widget)
        self.sc_area_widget_layout.addWidget(self.project_box)
        self.sc_area_widget_layout.addWidget(self.input_box)
        self.sc_area_widget_layout.addWidget(self.grid_box)
        self.sc_area_widget_layout.addStretch(1)

        self.sc_area_layout = QtGui.QHBoxLayout(self.sc_area)
        self.sc_area_layout.addWidget(self.sc_area_widget)
        self.sc_area.setWidgetResizable(True)
        self.sc_area.setWidget(self.sc_area_widget)

        self.body_layout = QtGui.QVBoxLayout(self)
        self.body_layout.addWidget(self.sc_area, 1)
        self.body_layout.addLayout(self.progress_layout)

    def reset_function(self):
        if self.parent.v.WDIR is None:
            self.parent.statusbar.showMessage("Version: %s" % __version__)
            self.parent.main_window.setTabEnabled(0, True)
            self.parent.main_window.setCurrentIndex(0)
            self.parent.main_window.setTabEnabled(1, False)
            self.project_text.clear()
        else:
            reset_opt = reset_warning(self)
            if reset_opt == QtGui.QMessageBox.Yes:
                self.parent.statusbar.showMessage("Version: %s" % __version__)
                self.parent.main_window.setTabEnabled(0, True)
                self.parent.main_window.setCurrentIndex(0)
                self.parent.main_window.setTabEnabled(1, False)
                self.project_text.setEnabled(True)
                self.wdir_button.setEnabled(True)
                self.wdir_button.setEnabled(True)
                self.project_text.clear()
                self.wdir_text.clear()
                self.input_box.setEnabled(False)
                self.prep_rec_lig_button.setEnabled(False)
                self.bind_site_button.setEnabled(True)
                self.protein_text.clear()
                self.protein_label.clear()
                self.protein_textB.clear()
                self.protein_labelB.clear()
                self.ligand_text.clear()
                self.ligand_label.clear()
                self.grid_pymol_button.setText('Show in PyMol')
                self.grid_pymol_buttonB.setText('Show in PyMol')

                self.hide_all('all')
                self.grid_box.setEnabled(False)
                self.progressBar.setValue(0)
                self.run_button.setEnabled(False)
                self.stop_button.setEnabled(False)
                try:
                    self.b_pymol.__del__()
                except:
                    pass
                try:
                    self.b_pymolB.__del__()
                except:
                    pass
                try:
                    self.b_pymol_timer.stop()
                except:
                    pass
                try:
                    self.b_pymol_timerB.stop()
                except:
                    pass
                if self.parent.v.WDIR is not None:
                    rm_folder = QtGui.QMessageBox.warning(self, 'Warning',
                                                          "Do you wish to delete the previous project's folder?.",
                                                          QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    if rm_folder == QtGui.QMessageBox.Yes:
                        try:
                            self.parent.output2file.conclude()
                            os.chdir(self.parent.v.loc_project)
                            shutil.rmtree(self.parent.v.WDIR)
                        except:
                            QtGui.QMessageBox.warning(self, 'Error',
                                                      "The directory cannot be deleted. Probably is being used by "
                                                      "another program.", QtGui.QMessageBox.Ok)
                self.parent.v = Variables()
                self.parent.configuration_tab.initial_config()

    def hide_all(self, l):
        if l == 'A':
            self.grid_predef_text.hide()
            self.checker_icon.hide()
            self.checker_icon_ok.hide()
            self.lig_list.hide()
            self.coor_box.hide()
            self.size_box.hide()
            self.grid_icon_ok.hide()
            self.grid_icon.hide()
        elif l == 'B':
            self.grid_predef_textB.hide()
            self.checker_iconB.hide()
            self.checker_icon_okB.hide()
            self.lig_listB.hide()
            self.coor_boxB.hide()
            self.size_boxB.hide()
            self.grid_icon_okB.hide()
            self.grid_iconB.hide()
        else:
            self.grid_predef_text.hide()
            self.checker_icon.hide()
            self.checker_icon_ok.hide()
            self.lig_list.hide()
            self.coor_box.hide()
            self.size_box.hide()
            self.grid_predef_textB.hide()
            self.checker_iconB.hide()
            self.checker_icon_okB.hide()
            self.lig_listB.hide()
            self.coor_boxB.hide()
            self.size_boxB.hide()
            self.grid_icon_okB.hide()
            self.grid_iconB.hide()
            self.grid_icon_ok.hide()
            self.grid_icon.hide()
            self.btnA_auto.setChecked(True)
            self.btnB_auto.setChecked(True)

    def grid_prot(self, b):
        if b.isChecked():
            if self.protein_column_group_btnA.id(b) == 1:
                self.hide_all('A')
                self.parent.v.grid_def = 'auto'
                self.grid_pymol_button.setEnabled(False)
                self.grid_pymol_button.setText('Show in PyMol')
            elif self.protein_column_group_btnA.id(b) == 2:
                self.hide_all('A')
                self.grid_predef_text.clear()
                self.grid_predef_text.setReadOnly(False)
                self.grid_predef_text.show()
                self.checker_icon.show()
                self.parent.v.grid_def = 'by_residues'
                self.grid_pymol_button.setText('Show in PyMol')
                self.grid_pymol_button.setEnabled(False)
            elif self.protein_column_group_btnA.id(b) == 3:
                self.hide_all('A')
                self.lig_list.show()
                self.parent.v.grid_def = 'by_ligand'
                self.grid_pymol_button.setEnabled(False)
                self.grid_pymol_button.setText('Show in PyMol')
            elif self.protein_column_group_btnA.id(b) == 4:
                self.hide_all('A')
                self.parent.v.grid_def = 'by_user'
                self.coor_box.show()
                self.size_box.show()
                self.coor_x.clear()
                self.coor_y.clear()
                self.coor_z.clear()
                self.size_x.clear()
                self.size_y.clear()
                self.size_z.clear()
                self.coor_x.setReadOnly(False)
                self.coor_y.setReadOnly(False)
                self.coor_z.setReadOnly(False)
                self.size_x.setReadOnly(False)
                self.size_y.setReadOnly(False)
                self.size_z.setReadOnly(False)
                self.grid_icon.show()
                self.grid_pymol_button.setText('Build in PyMol')
                self.grid_pymol_button.setEnabled(True)
            if self.protein_column_group_btnB.id(b) == 1:
                self.hide_all('B')
                self.parent.v.analog_grid_def = 'auto'
                self.grid_pymol_buttonB.setEnabled(False)
                self.grid_pymol_buttonB.setText('Show in PyMol')
            elif self.protein_column_group_btnB.id(b) == 2:
                self.hide_all('B')
                self.grid_predef_textB.clear()
                self.grid_predef_textB.setReadOnly(False)
                self.grid_predef_textB.show()
                self.checker_iconB.show()
                self.parent.v.analog_grid_def = 'by_residues'
                self.grid_pymol_buttonB.setEnabled(False)
                self.grid_pymol_buttonB.setText('Show in PyMol')
            elif self.protein_column_group_btnB.id(b) == 3:
                self.hide_all('B')
                self.lig_listB.show()
                self.parent.v.analog_grid_def = 'by_ligand'
                self.grid_pymol_buttonB.setEnabled(False)
                self.grid_pymol_buttonB.setText('Show in PyMol')
            elif self.protein_column_group_btnB.id(b) == 4:
                self.hide_all('B')
                self.parent.v.analog_grid_def = 'by_user'
                self.coor_boxB.show()
                self.size_boxB.show()
                self.coor_xB.clear()
                self.coor_yB.clear()
                self.coor_zB.clear()
                self.size_xB.clear()
                self.size_yB.clear()
                self.size_zB.clear()
                self.coor_xB.setReadOnly(False)
                self.coor_yB.setReadOnly(False)
                self.coor_zB.setReadOnly(False)
                self.size_xB.setReadOnly(False)
                self.size_yB.setReadOnly(False)
                self.size_zB.setReadOnly(False)
                self.grid_iconB.show()
                self.grid_pymol_buttonB.setText('Build in PyMol')
                self.grid_pymol_buttonB.setEnabled(True)

            if (self.protein_column_group_btnA.id(b) == 1 and self.protein_column_group_btnB.id(
                    self.protein_column_group_btnB.checkedButton()) == 2) or (
                    self.protein_column_group_btnB.id(b) == 2 and self.protein_column_group_btnA.id(
                self.protein_column_group_btnA.checkedButton()) == 1):
                if self.parent.v.errorB == 1:
                    self.checker_iconB.show()
                    self.bind_site_button.setEnabled(False)
                else:
                    self.checker_icon_okB.show()
                    self.bind_site_button.setEnabled(True)
            elif (self.protein_column_group_btnA.id(b) == 1 and self.protein_column_group_btnB.id(
                    self.protein_column_group_btnB.checkedButton()) == 4) or (
                    self.protein_column_group_btnB.id(b) == 4 and self.protein_column_group_btnA.id(
                self.protein_column_group_btnA.checkedButton()) == 1):
                self.grid = 2
                if self.parent.v.gerrorB == 1:
                    self.grid_iconB.show()
                    self.bind_site_button.setEnabled(False)
                else:
                    self.grid_icon_okB.show()
                    self.bind_site_button.setEnabled(True)
            elif (self.protein_column_group_btnA.id(b) == 2 and self.protein_column_group_btnB.id(
                    self.protein_column_group_btnB.checkedButton()) == 1) or (
                    self.protein_column_group_btnB.id(b) == 1 and self.protein_column_group_btnA.id(
                self.protein_column_group_btnA.checkedButton()) == 2):
                if self.parent.v.error == 1:
                    self.checker_icon.show()
                    self.bind_site_button.setEnabled(False)
                else:
                    self.checker_icon_ok.show()
                    self.bind_site_button.setEnabled(True)
            elif (self.protein_column_group_btnA.id(b) == 2 and self.protein_column_group_btnB.id(
                    self.protein_column_group_btnB.checkedButton()) == 2) or (
                    self.protein_column_group_btnB.id(b) == 2 and self.protein_column_group_btnA.id(
                self.protein_column_group_btnA.checkedButton()) == 2):
                if self.parent.v.errorB == 1:
                    self.checker_iconB.show()
                else:
                    self.checker_icon_okB.show()
                if self.parent.v.error == 1:
                    self.checker_icon.show()
                else:
                    self.checker_icon_ok.show()
                if self.parent.v.errorB == 0 and self.parent.v.error == 0:
                    self.bind_site_button.setEnabled(True)
                else:
                    self.bind_site_button.setEnabled(False)
            elif (self.protein_column_group_btnA.id(b) == 2 and self.protein_column_group_btnB.id(
                    self.protein_column_group_btnB.checkedButton()) == 3) or (
                    self.protein_column_group_btnB.id(b) == 3 and self.protein_column_group_btnA.id(
                self.protein_column_group_btnA.checkedButton()) == 2):
                if self.parent.v.error == 1:
                    self.checker_icon.show()
                    self.bind_site_button.setEnabled(False)
                else:
                    self.checker_icon_ok.show()
                    self.bind_site_button.setEnabled(True)
            elif (self.protein_column_group_btnA.id(b) == 2 and self.protein_column_group_btnB.id(
                    self.protein_column_group_btnB.checkedButton()) == 4) or (
                    self.protein_column_group_btnB.id(b) == 4 and self.protein_column_group_btnA.id(
                self.protein_column_group_btnA.checkedButton()) == 2):
                self.grid = 2
                if self.parent.v.gerrorB == 1:
                    self.grid_iconB.show()
                else:
                    self.grid_icon_okB.show()
                if self.parent.v.error == 1:
                    self.checker_icon.show()
                else:
                    self.checker_icon_ok.show()
                if self.parent.v.gerrorB == 0 and self.parent.v.error == 0:
                    self.bind_site_button.setEnabled(True)
                else:
                    self.bind_site_button.setEnabled(False)
            elif (self.protein_column_group_btnA.id(b) == 3 and self.protein_column_group_btnB.id(
                    self.protein_column_group_btnB.checkedButton()) == 2) or (
                    self.protein_column_group_btnB.id(b) == 2 and self.protein_column_group_btnA.id(
                self.protein_column_group_btnA.checkedButton()) == 3):
                if self.parent.v.errorB == 1:
                    self.checker_iconB.show()
                    self.bind_site_button.setEnabled(False)
                else:
                    self.checker_icon_okB.show()
                    self.bind_site_button.setEnabled(True)
            elif (self.protein_column_group_btnA.id(b) == 3 and self.protein_column_group_btnB.id(
                    self.protein_column_group_btnB.checkedButton()) == 4) or (
                    self.protein_column_group_btnB.id(b) == 4 and self.protein_column_group_btnA.id(
                self.protein_column_group_btnA.checkedButton()) == 3):
                self.grid = 2
                if self.parent.v.gerrorB == 1:
                    self.grid_iconB.show()
                    self.bind_site_button.setEnabled(False)
                else:
                    self.grid_icon_okB.show()
                    self.bind_site_button.setEnabled(True)
            elif (self.protein_column_group_btnA.id(b) == 4 and self.protein_column_group_btnB.id(
                    self.protein_column_group_btnB.checkedButton()) == 1) or (
                    self.protein_column_group_btnB.id(b) == 1 and self.protein_column_group_btnA.id(
                self.protein_column_group_btnA.checkedButton()) == 4):
                self.grid = 1
                if self.parent.v.gerror == 1:
                    self.grid_icon.show()
                    self.grid_icon_ok.hide()
                    self.bind_site_button.setEnabled(False)
                else:
                    self.grid_icon_ok.show()
                    self.grid_icon.hide()
                    self.bind_site_button.setEnabled(True)
            elif (self.protein_column_group_btnA.id(b) == 4 and self.protein_column_group_btnB.id(
                    self.protein_column_group_btnB.checkedButton()) == 2) or (
                    self.protein_column_group_btnB.id(b) == 2 and self.protein_column_group_btnA.id(
                self.protein_column_group_btnA.checkedButton()) == 4):
                self.grid = 1
                if self.parent.v.errorB == 1:
                    self.checker_iconB.show()
                else:
                    self.checker_icon_okB.show()
                if self.parent.v.gerror == 1:
                    self.grid_icon.show()
                else:
                    self.grid_icon_ok.show()
                if self.parent.v.errorB == 0 and self.parent.v.gerror == 0:
                    self.bind_site_button.setEnabled(True)
                else:
                    self.bind_site_button.setEnabled(False)
            elif (self.protein_column_group_btnA.id(b) == 4 and self.protein_column_group_btnB.id(
                    self.protein_column_group_btnB.checkedButton()) == 3) or (
                    self.protein_column_group_btnB.id(b) == 3 and self.protein_column_group_btnA.id(
                self.protein_column_group_btnA.checkedButton()) == 4):
                self.grid = 1
                if self.parent.v.gerror == 1:
                    self.grid_icon.show()
                    self.bind_site_button.setEnabled(False)
                else:
                    self.grid_icon_ok.show()
                    self.bind_site_button.setEnabled(True)
            elif (self.protein_column_group_btnA.id(b) == 4 and self.protein_column_group_btnB.id(
                    self.protein_column_group_btnB.checkedButton()) == 4) or (
                    self.protein_column_group_btnB.id(b) == 4 and self.protein_column_group_btnA.id(
                self.protein_column_group_btnA.checkedButton()) == 4):
                self.grid = 3
                if self.parent.v.gerrorB == 1:
                    self.grid_iconB.show()
                else:
                    self.grid_icon_okB.show()
                if self.parent.v.gerror == 1:
                    self.grid_icon.show()
                else:
                    self.grid_icon_ok.show()
                if self.parent.v.gerrorB == 0 and self.parent.v.gerror == 0:
                    self.bind_site_button.setEnabled(True)
                else:
                    self.bind_site_button.setEnabled(False)
            else:
                self.bind_site_button.setEnabled(True)

    def simulation_form(self, btn):
        if btn.isChecked():
            if btn.text() == 'Off-Target Docking':
                self.grid_box.setEnabled(False)
                self.all_options.setColumnStretch(1, 1)
                self.all_options.setColumnStretch(2, 1)
                self.prep_rec_lig_button.setEnabled(False)
                self.parent.v.scoring = False
                self.parent.v.cr = True
                self.parent.v.program_mode = 'OFF-TARGET'
                self.run_button.show()
                self.stop_button.show()
                self.run_scoring.hide()
                self.non_button.hide()
                self.progressBar.setValue(2)
                ## Input box
                self.protein_button.setText('Target')
                self.protein_buttonB.show()
                self.protein_textB.show()
                # self.protein_labelB.show()
                self.grid_pymol_buttonB.show()
                self.reset_grid_buttonB.show()
                ### Grid definition box
                self.protein_column_label.show()
                self.btnA_auto.show()
                self.btnA_res.show()
                self.btnA_lig.show()
                self.btnA_user.show()
                self.protein1_column_label.show()
                self.btnB_auto.show()
                self.btnB_res.show()
                self.btnB_lig.show()
                self.btnB_user.show()
                if os.path.exists(`self.parent.v.input_offtarget`):
                    try:
                        os.remove(`self.parent.v.input_offtarget`)
                    except:
                        pass
                self.parent.v.input_offtarget = None
                self.parent.v.protein_name = None
                self.parent.v.ligands = None
                self.protein_text.clear()
                self.protein_label.clear()
                self.lig_list.hide()
                if os.path.exists(`self.parent.v.input_lig`):
                    try:
                        os.remove(`self.parent.v.input_lig`)
                    except:
                        pass
                self.parent.v.input_lig = None
                self.ligand_text.clear()
                self.ligand_label.clear()
                self.parent.v.ligand_name = None
                if os.path.exists(`self.parent.v.input_target`):
                    try:
                        os.remove(`self.parent.v.input_target`)
                    except:
                        pass
                self.parent.v.input_target = None
                self.parent.v.analog_protein_name = None
                self.parent.v.analog_ligands = None
                self.protein_textB.clear()
                self.protein_labelB.clear()
                self.lig_listB.hide()
                self.lig_list.clear()
                self.lig_listB.clear()
                self.checker_icon.hide()
                self.checker_icon_ok.hide()
                self.grid_icon.hide()
                self.grid_icon_ok.hide()
                self.grid_predef_text.hide()
                self.grid_auto_cr.show()
                self.grid_predef_cr.show()
                self.grid_by_lig_cr.show()
                self.grid_user_cr.show()
                self.coor_box.hide()
                self.size_box.hide()
                self.lig_list.hide()
            elif btn.text() == 'Scoring':
                self.all_options.setColumnStretch(2, 0)
                self.grid_box.setEnabled(False)
                self.run_button.hide()
                self.prep_rec_lig_button.setEnabled(False)
                self.parent.v.scoring = True
                self.parent.v.cr = False
                self.parent.v.program_mode = 'SCORING'
                self.stop_button.hide()
                self.run_scoring.show()
                self.non_button.show()
                self.progressBar.setValue(2)
                if os.path.exists(`self.parent.v.input_offtarget`):
                    try:
                        os.remove(`self.parent.v.input_offtarget`)
                    except:
                        pass
                self.parent.v.input_offtarget = None
                self.parent.v.protein_name = None
                self.parent.v.ligands = None
                self.protein_text.clear()
                self.protein_label.clear()
                self.lig_list.hide()
                if os.path.exists(`self.parent.v.input_lig`):
                    try:
                        os.remove(`self.parent.v.input_lig`)
                    except:
                        pass
                self.parent.v.input_lig = None
                self.parent.v.ligand_name = None
                self.ligand_text.clear()
                self.ligand_label.clear()
                if os.path.exists(`self.parent.v.input_target`):
                    try:
                        os.remove(`self.parent.v.input_target`)
                    except:
                        pass
                self.parent.v.input_target = None
                self.parent.v.analog_protein_name = None
                self.parent.v.analog_ligands = None
                self.protein_textB.clear()
                self.protein_labelB.clear()
                self.lig_listB.hide()
                self.lig_list.clear()
                self.lig_listB.clear()
                self.parent.v.cr = False
                self.protein_button.setText('Protein')
                self.btnA_auto.setChecked(True)
                self.btnB_auto.setChecked(True)
                self.protein_buttonB.hide()
                self.protein_textB.hide()
                self.protein_labelB.hide()
                self.protein1_column_label.hide()
                self.btnB_auto.hide()
                self.btnB_res.hide()
                self.btnB_lig.hide()
                self.btnB_user.hide()
                self.grid_predef_text.hide()
                self.grid_predef_textB.hide()
                self.checker_icon.hide()
                self.checker_iconB.hide()
                self.checker_icon_ok.hide()
                self.checker_icon_okB.hide()
                self.grid_iconB.hide()
                self.grid_icon.hide()
                self.grid_icon_okB.hide()
                self.grid_icon_ok.hide()
                self.coor_box.hide()
                self.coor_boxB.hide()
                self.size_box.hide()
                self.size_boxB.hide()
                self.lig_listB.hide()
                self.lig_list.hide()
            else:
                self.grid_box.setEnabled(False)
                self.all_options.setColumnStretch(2, 0)
                self.prep_rec_lig_button.setEnabled(False)
                self.parent.v.scoring = False
                self.parent.v.cr = False
                self.parent.v.program_mode = 'SIMPLE'
                self.run_button.show()
                self.stop_button.show()
                self.run_scoring.hide()
                self.non_button.hide()
                self.progressBar.setValue(2)
                self.grid_pymol_buttonB.hide()
                self.reset_grid_buttonB.hide()
                if os.path.exists(`self.parent.v.input_offtarget`):
                    try:
                        os.remove(`self.parent.v.input_offtarget`)
                    except:
                        pass
                self.parent.v.input_offtarget = None
                self.parent.v.protein_name = None
                self.parent.v.ligands = None
                self.protein_text.clear()
                self.protein_label.clear()
                self.lig_list.hide()
                if os.path.exists(`self.parent.v.input_lig`):
                    try:
                        os.remove(`self.parent.v.input_lig`)
                    except:
                        pass
                self.parent.v.input_lig = None
                self.parent.v.ligand_name = None
                self.ligand_text.clear()
                self.ligand_label.clear()
                if os.path.exists(`self.parent.v.input_target`):
                    try:
                        os.remove(`self.parent.v.input_target`)
                    except:
                        pass
                self.parent.v.input_target = None
                self.parent.v.analog_protein_name = None
                self.parent.v.analog_ligands = None
                self.protein_textB.clear()
                self.protein_labelB.clear()
                self.lig_listB.hide()
                self.lig_list.clear()
                self.lig_listB.clear()
                self.parent.v.cr = False
                self.protein_button.setText('Protein')
                self.btnA_auto.setChecked(True)
                self.btnB_auto.setChecked(True)
                self.protein_buttonB.hide()
                self.protein_textB.hide()
                self.protein_labelB.hide()
                self.protein1_column_label.hide()
                self.btnB_auto.hide()
                self.btnB_res.hide()
                self.btnB_lig.hide()
                self.btnB_user.hide()
                self.grid_predef_text.hide()
                self.grid_predef_textB.hide()
                self.checker_icon.hide()
                self.checker_iconB.hide()
                self.checker_icon_ok.hide()
                self.checker_icon_okB.hide()
                self.grid_iconB.hide()
                self.grid_icon.hide()
                self.grid_icon_okB.hide()
                self.grid_icon_ok.hide()
                self.coor_box.hide()
                self.coor_boxB.hide()
                self.size_box.hide()
                self.size_boxB.hide()
                self.lig_listB.hide()
                self.lig_list.hide()

    def info_pass(self, prot):
        if prot == 'target':
            if os.path.exists('user_target_dim.txt'):
                tfile = open('user_target_dim.txt')
                for line in tfile:
                    line = line.strip('\n')
                    self.dim_data_target = line.split()
                tfile.close()
                if self.dim_data_target != self.ttemp:
                    if self.parent.v.cr:
                        # self.btnA_user.setChecked(True)
                        if self.need_gridB:
                            self.progressBar.setValue(25)
                        else:
                            self.progressBar.setValue(37)
                    else:
                        # self.grid_user.setChecked(True)
                        self.progressBar.setValue(25)
                    self.btnA_user.setChecked(True)
                    self.coor_x.setText(self.dim_data_target[0])
                    self.coor_y.setText(self.dim_data_target[1])
                    self.coor_z.setText(self.dim_data_target[2])
                    self.size_x.setText(self.dim_data_target[3])
                    self.size_y.setText(self.dim_data_target[4])
                    self.size_z.setText(self.dim_data_target[5])
                    self.ttemp = self.dim_data_target
                    self.bind_site_button.setEnabled(True)
                    self.run_button.setEnabled(False)
                    self.need_grid = True
                    os.remove('user_target_dim.txt')
                    self.b_pymol_timer.stop()
                    self.grid_pymol_button.setEnabled(False)
        elif prot == 'target_build':
            if os.path.exists('user_target_dim.txt'):
                tfile = open('user_target_dim.txt')
                for line in tfile:
                    line = line.strip('\n')
                    self.dim_data_target = line.split()
                tfile.close()
                if self.dim_data_target != self.bttemp:
                    self.coor_x.setText(self.dim_data_target[0])
                    self.coor_y.setText(self.dim_data_target[1])
                    self.coor_z.setText(self.dim_data_target[2])
                    self.size_x.setText(self.dim_data_target[3])
                    self.size_y.setText(self.dim_data_target[4])
                    self.size_z.setText(self.dim_data_target[5])
                    self.bttemp = self.dim_data_target
                    self.check_grid()
                    self.run_button.setEnabled(False)
                    self.need_grid = True
                    os.remove('user_target_dim.txt')
                    try:
                        self.b_pymol_timer.stop()
                    except:
                        pass
                    try:
                        self.bld_pymol_timer.stop()
                    except:
                        pass
        elif prot == 'offtarget':
            if os.path.exists('user_off_target_dim.txt'):
                cfile = open('user_off_target_dim.txt')
                for line in cfile:
                    line = line.strip('\n')
                    self.dim_data_offtarget = line.split()
                cfile.close()
                if self.dim_data_offtarget != self.ttempB:
                    if self.need_grid:
                        self.progressBar.setValue(25)
                    else:
                        self.progressBar.setValue(37)
                    self.btnB_user.setChecked(True)
                    self.coor_xB.setText(self.dim_data_offtarget[0])
                    self.coor_yB.setText(self.dim_data_offtarget[1])
                    self.coor_zB.setText(self.dim_data_offtarget[2])
                    self.size_xB.setText(self.dim_data_offtarget[3])
                    self.size_yB.setText(self.dim_data_offtarget[4])
                    self.size_zB.setText(self.dim_data_offtarget[5])
                    self.ttempB = self.dim_data_offtarget
                    self.bind_site_button.setEnabled(True)
                    self.run_button.setEnabled(False)
                    self.need_gridB = True
                    os.remove('user_off_target_dim.txt')
                    self.b_pymol_timerB.stop()
                    self.grid_pymol_buttonB.setEnabled(False)
        elif prot == 'offtarget_build':
            if os.path.exists('user_off_target_dim.txt'):
                cfile = open('user_off_target_dim.txt')
                for line in cfile:
                    line = line.strip('\n')
                    self.dim_data_offtarget = line.split()
                cfile.close()
                if self.dim_data_offtarget != self.bttempB:
                    self.btnB_user.setChecked(True)
                    self.coor_xB.setText(self.dim_data_offtarget[0])
                    self.coor_yB.setText(self.dim_data_offtarget[1])
                    self.coor_zB.setText(self.dim_data_offtarget[2])
                    self.size_xB.setText(self.dim_data_offtarget[3])
                    self.size_yB.setText(self.dim_data_offtarget[4])
                    self.size_zB.setText(self.dim_data_offtarget[5])
                    self.bttempB = self.dim_data_offtarget
                    self.check_grid()
                    self.run_button.setEnabled(False)
                    self.need_gridB = True
                    os.remove('user_off_target_dim.txt')
                    try:
                        self.b_pymol_timerB.stop()
                    except:
                        pass
                    try:
                        self.bld_pymol_timerB.stop()
                    except:
                        pass

    def grid_actions(self, btn):
        if btn.objectName() == 'grid_pymol_button' and btn.text() == 'Show in PyMol':
            visual_arg = [self.parent.v.protein_pdbqt, self.parent.ws.grid_pymol, '--', '-c',
                          self.parent.v.obj_center, '-s', '%s,%s,%s' % (self._size_x, self._size_y, self._size_z), '-p',
                          'target']
            self.box_pymol = {'pymol_boxA': [self.parent.ws.pymol, visual_arg]}
            self.b_pymol = Worker()
            self.b_pymol.readyReadStandardOutput.connect(self.readStdOutput)
            self.b_pymol.readyReadStandardError.connect(self.readStdError)
            self.b_pymol.prog_started.connect(self.prog_show)
            self.b_pymol.prog_finished.connect(self.process_progress)
            self.b_pymol.queue_finished.connect(self.check_queue)
            self.b_pymolq = Queue.Queue()
            self.b_pymolq.put(self.box_pymol)
            self.b_pymol.init(self.b_pymolq, 'Visualization')
            self.b_pymol.start_process()
            if os.path.exists(self.parent.v.obj_center):
                tf = open(self.parent.v.obj_center)
                for line in tf:
                    line = line.strip('\n')
                    if re.search('center_x', line):
                        self.center_x = line.split()[2]
                    if re.search('center_y', line):
                        self.center_y = line.split()[2]
                    if re.search('center_z', line):
                        self.center_z = line.split()[2]
                tf.close()
                self.ttemp = [self.center_x, self.center_y, self.center_z, `self._size_x`, `self._size_y`,
                              `self._size_z`]
            else:
                self.ttemp = [0, 0, 0, 0, 0, 0]
            self.b_pymol_timer = QtCore.QTimer()
            self.b_pymol_timer.timeout.connect(lambda: self.info_pass('target'))
            self.b_pymol_timer.start(15)
        elif btn.objectName() == 'grid_pymol_buttonB' and btn.text() == 'Show in PyMol':
            visual_arg = [self.parent.v.analog_protein_pdbqt, self.parent.ws.grid_pymol, '--', '-c',
                          self.parent.v.obj_center1, '-s', '%s,%s,%s' % (self._size_xB, self._size_yB, self._size_zB),
                          '-p', 'off-target']
            self.box_pymolB = {'pymol_boxB': [self.parent.ws.this_python, visual_arg]}
            self.b_pymolB = Worker()
            self.b_pymolB.readyReadStandardOutput.connect(self.readStdOutput)
            self.b_pymolB.readyReadStandardError.connect(self.readStdError)
            self.b_pymolB.prog_started.connect(self.prog_show)
            self.b_pymolB.prog_finished.connect(self.process_progress)
            self.b_pymolB.queue_finished.connect(self.check_queue)
            self.b_pymolqB = Queue.Queue()
            self.b_pymolqB.put(self.box_pymolB)
            self.b_pymolB.init(self.b_pymolqB, 'Visualization')
            self.b_pymolB.start_process()
            if os.path.exists(self.parent.v.obj_center1):
                tf = open(self.parent.v.obj_center1)
                for line in tf:
                    line = line.strip('\n')
                    if re.search('center_x', line):
                        self.center_xB = line.split()[2]
                    if re.search('center_y', line):
                        self.center_yB = line.split()[2]
                    if re.search('center_z', line):
                        self.center_zB = line.split()[2]
                self.ttempB = [self.center_xB, self.center_yB, self.center_zB, `self._size_xB`, `self._size_yB`,
                               `self._size_zB`]
            else:
                self.ttempB = [0, 0, 0, 0, 0, 0]
            self.b_pymol_timerB = QtCore.QTimer()
            self.b_pymol_timerB.timeout.connect(lambda: self.info_pass('offtarget'))
            self.b_pymol_timerB.start(15)
        elif btn.objectName() == 'reset_grid_button':
            self.hide_all('A')
            self.reset_grid_button.setEnabled(False)
            self.grid_pymol_button.setEnabled(False)
            self.run_button.setEnabled(False)
            self.bind_site_button.setEnabled(True)
            self.ttemp = [0, 0, 0, 0, 0, 0]
            self.need_grid = True

            self.btnA_auto.setChecked(True)
            self.btnA_auto.setEnabled(True)
            self.btnA_res.setEnabled(True)
            if self.parent.v.ligands is not None:
                self.btnA_lig.setEnabled(True)
                self.lig_list.setEnabled(True)
            else:
                self.btnA_lig.setEnabled(False)
                # self.lig_list.setEnabled(False)
            self.btnA_user.setEnabled(True)
            files = []
            dd = '%s*.map' % self.parent.v.protein_name
            files.extend(glob.glob(dd))
            dd = '%s*.fld' % self.parent.v.protein_name
            files.extend(glob.glob(dd))
            dd = '%s*.xyz' % self.parent.v.protein_name
            files.extend(glob.glob(dd))
            dd = '%s*.gpf' % self.parent.v.protein_name
            files.extend(glob.glob(dd))
            files.extend(['user_target_dim.txt', self.parent.v.FILL, self.parent.v.obj_center, self.parent.v.res_center,
                        self.parent.v.gd])
            for file in files:
                try:
                    os.remove(file)
                except:
                    pass
            if self.parent.v.cr:
                if self.need_gridB:
                    self.progressBar.setValue(25)
                else:
                    self.progressBar.setValue(37)
            else:
                self.progressBar.setValue(25)
        elif btn.objectName() == 'reset_grid_buttonB':
            self.hide_all('B')
            self.reset_grid_buttonB.setEnabled(False)
            self.grid_pymol_buttonB.setEnabled(False)
            self.run_button.setEnabled(False)
            self.bind_site_button.setEnabled(True)
            self.ttempB = [0, 0, 0, 0, 0, 0]
            self.need_gridB = True
            self.btnB_auto.setChecked(True)
            self.btnB_auto.setEnabled(True)
            self.btnB_res.setEnabled(True)
            if self.parent.v.analog_ligands is not None:
                self.btnB_lig.setEnabled(True)
                self.lig_listB.setEnabled(True)
            else:
                self.btnB_lig.setEnabled(False)
            self.btnB_user.setEnabled(True)

            files = []
            dd = '%s*.map' % self.parent.v.analog_protein_name
            files.extend(glob.glob(dd))
            dd = '%s*.fld' % self.parent.v.analog_protein_name
            files.extend(glob.glob(dd))
            dd = '%s*.xyz' % self.parent.v.analog_protein_name
            files.extend(glob.glob(dd))
            dd = '%s*.gpf' % self.parent.v.analog_protein_name
            files.extend(glob.glob(dd))
            files.extend(['user_off_target_dim.txt', self.parent.v.FILL, self.parent.v.obj_center1,
                          self.parent.v.res_center1, self.parent.v.gd1])

            for file in files:
                try:
                    os.remove(file)
                except:
                    pass
            if self.need_grid:
                self.progressBar.setValue(25)
            else:
                self.progressBar.setValue(37)
        elif btn.objectName() == 'grid_pymol_button' and btn.text() == 'Build in PyMol':
            build_arg = [self.parent.v.protein_pdbqt, self.parent.ws.build_pymol, '--', '-s',
                         '%s,%s,%s' % (self.parent.v.rg, self.parent.v.rg,
                                       self.parent.v.rg), '-p', 'target']
            self.box_pymol = {'pymol_buildA': [self.parent.ws.pymol, build_arg]}
            self.bld_pymol = Worker()
            self.bld_pymol.readyReadStandardOutput.connect(self.readStdOutput)
            self.bld_pymol.readyReadStandardError.connect(self.readStdError)
            self.bld_pymol.prog_started.connect(self.prog_show)
            self.bld_pymol.prog_finished.connect(self.process_progress)
            self.bld_pymol.queue_finished.connect(self.check_queue)
            self.bld_pymolq = Queue.Queue()
            self.bld_pymolq.put(self.box_pymol)
            self.bld_pymol.init(self.bld_pymolq, 'Construction')
            self.bld_pymol.start_process()
            self.bttemp = [0, 0, 0, 0, 0, 0]
            self.bld_pymol_timer = QtCore.QTimer()
            self.bld_pymol_timer.timeout.connect(lambda: self.info_pass('target_build'))
            self.bld_pymol_timer.start(15)
        elif btn.objectName() == 'grid_pymol_buttonB' and btn.text() == 'Build in PyMol':
            build_arg = [self.parent.v.analog_protein_pdbqt, self.parent.ws.build_pymol, '--', '-s',
                         '%s,%s,%s' % (self.parent.v.rg, self.parent.v.rg,
                                       self.parent.v.rg), '-p', 'off-target']
            self.box_pymolB = {'pymol_buildB': [self.parent.ws.pymol, build_arg]}
            self.bld_pymolB = Worker()
            self.bld_pymolB.readyReadStandardOutput.connect(self.readStdOutput)
            self.bld_pymolB.readyReadStandardError.connect(self.readStdError)
            self.bld_pymolB.prog_started.connect(self.prog_show)
            self.bld_pymolB.prog_finished.connect(self.process_progress)
            self.bld_pymolB.queue_finished.connect(self.check_queue)
            self.bld_pymolqB = Queue.Queue()
            self.bld_pymolqB.put(self.box_pymolB)
            self.bld_pymolB.init(self.bld_pymolqB, 'Construction')
            self.bld_pymolB.start_process()
            self.bttempB = [0, 0, 0, 0, 0, 0]
            self.bld_pymol_timerB = QtCore.QTimer()
            self.bld_pymol_timerB.timeout.connect(lambda: self.info_pass('offtarget_build'))
            self.bld_pymol_timerB.start(15)

    def check_queue(self, qname, finished):
        if finished:
            self.reset_button.setEnabled(True)
            if qname == 'Prepare Input Files':
                self.grid_pymol_button.setEnabled(False)
                self.grid_pymol_buttonB.setEnabled(False)
                self.reset_grid_button.setEnabled(False)
                self.reset_grid_buttonB.setEnabled(False)
                if self.parent.v.scoring:
                    self.grid_box.setEnabled(False)
                    self.input_box.setEnabled(False)
                    self.run_scoring.setEnabled(True)
                else:
                    self.grid_box.setEnabled(True)
                    self.input_box.setEnabled(False)
                    self.grid_predef_text.setReadOnly(False)
                    self.grid_predef_textB.setReadOnly(False)
                    self.coor_xB.setReadOnly(False)
                    self.coor_yB.setReadOnly(False)
                    self.coor_zB.setReadOnly(False)
                    self.size_xB.setReadOnly(False)
                    self.size_yB.setReadOnly(False)
                    self.size_zB.setReadOnly(False)
                    self.coor_x.setReadOnly(False)
                    self.coor_y.setReadOnly(False)
                    self.coor_z.setReadOnly(False)
                    self.size_x.setReadOnly(False)
                    self.size_y.setReadOnly(False)
                    self.size_z.setReadOnly(False)
                if self.parent.v.cr:
                    self.btnA_auto.setEnabled(True)
                    self.btnA_res.setEnabled(True)
                    self.btnA_user.setEnabled(True)
                    self.btnA_lig.setEnabled(True)
                    self.btnB_auto.setEnabled(True)
                    self.btnB_res.setEnabled(True)
                    self.btnB_user.setEnabled(True)
                    self.btnB_lig.setEnabled(True)
                    if self.parent.v.protein_pdbqt is not None and self.parent.v.analog_protein_pdbqt is not None and self.parent.v.ligand_pdbqt is not None:
                        self.progressBar.setValue(25)
                else:
                    if self.parent.v.protein_pdbqt is not None and self.parent.v.ligand_pdbqt is not None:
                        if self.parent.v.scoring:
                            self.progressBar.setValue(50)
                        else:
                            self.progressBar.setValue(25)
                self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IF Prepare Initial Files...Done\n')
            elif qname == 'Binding Site Determination':
                self.grid_box.setEnabled(True)
                self.bind_site_button.setEnabled(False)
                self.grid_pymol_button.setEnabled(True)
                self.reset_grid_button.setEnabled(True)
                self.reset_grid_buttonB.setEnabled(True)
                self.grid_pymol_buttonB.setEnabled(True)
                if self.parent.v.cr:
                    self.btnA_user.setEnabled(False)
                    self.btnA_auto.setEnabled(False)
                    self.btnA_lig.setEnabled(False)
                    self.btnA_res.setEnabled(False)
                    self.btnB_user.setEnabled(False)
                    self.btnB_auto.setEnabled(False)
                    self.btnB_lig.setEnabled(False)
                    self.btnB_res.setEnabled(False)
                    self.grid_predef_textB.setReadOnly(True)
                    self.lig_listB.setEnabled(False)
                    self.coor_xB.setReadOnly(True)
                    self.coor_yB.setReadOnly(True)
                    self.coor_zB.setReadOnly(True)
                    self.size_xB.setReadOnly(True)
                    self.size_yB.setReadOnly(True)
                    self.size_zB.setReadOnly(True)
                    self.grid_pymol_buttonB.setText('Show in PyMol')
                    self.need_gridB = False
                self.grid_predef_text.setReadOnly(True)
                self.lig_list.setEnabled(False)
                self.coor_x.setReadOnly(True)
                self.coor_y.setReadOnly(True)
                self.coor_z.setReadOnly(True)
                self.size_x.setReadOnly(True)
                self.size_y.setReadOnly(True)
                self.size_z.setReadOnly(True)

                self.run_button.setEnabled(True)
                self.need_grid = False
                self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: BSD Binding Site Definition...Done\n')
                self.grid_pymol_button.setText('Show in PyMol')
                if self.parent.v.program_mode == 'SCORING':
                    self.progressBar.setValue(10)
                else:
                    self.progressBar.setValue(50)

            elif qname == 'Molecular Docking Simulation':
                self.go_result()
                self.parent.configuration_tab.log_wdw.textedit.append(
                    'AMDOCK: MDS Molecular Docking Simulation...Done\n')
            else:
                self.grid_box.setEnabled(False)
                self.progressBar.setValue(100)
                self.go_scoring()
        else:
            self.queue_name = qname

    def prog_show(self, prog):
        self.prog = prog
        if self.queue_name == 'Prepare Input Files':
            if self.parent.v.cr:
                if prog == 'PDB2PQR':
                    progress(self, 1, 1, 14, time=20, mess='Running PDB2PQR for Target...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: IF Running PDB2PQR for Target Protein...')
                elif prog == 'PDB2PQR B':
                    progress(self, 1, 1, 18, time=20, mess='Running PDB2PQR for Off-Target...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: IF Running PDB2PQR for Off-Target Protein...')
                elif prog == 'Prepare_Receptor4':
                    progress(self, 1, 1, 20, time=7, mess='Prepare receptor A...')
                    self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IF Prepare Target Protein...')
                elif prog == 'Prepare_Receptor4 B':
                    progress(self, 1, 1, 22, time=7, mess='Prepare receptor B...')
                    self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IF Prepare Off-Target Protein...')
                elif prog == 'Prepare_Ligand4':
                    progress(self, 1, 1, 25, time=5, mess='Prepare ligand...')
                    self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IF Prepare Ligand...')
            else:
                if prog == 'PDB2PQR':
                    progress(self, 1, 1, 18, time=15, mess='Running %s...' % prog)
                    self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IF Running PDB2PQR for Protein...')
                elif prog == 'Prepare_Receptor4':
                    progress(self, 1, 1, 22, time=7, mess='Prepare receptor...')
                    self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IF Prepare Protein...')
                elif prog == 'Prepare_Ligand4':
                    progress(self, 1, 1, 25, time=5, mess='Prepare ligand...')
                    self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IF Prepare Ligand...')
        elif self.queue_name == 'Binding Site Determination':
            if self.parent.v.cr:
                if self.parent.v.grid_def == 'auto':
                    if prog == 'function GridDefinition: Protein Center':
                        progress(self, 0, 2, 25, mess='Determination of Target Center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Target Protein Center...')
                    if prog == 'Prepare_gpf4':
                        progress(self, 0, 2, 25, mess='Generate GPF file...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Generate GPF file for Target Protein...')
                    if prog == 'AutoGrid4':
                        self.part = 0
                        progress(self, 0, 2, 25, mess='Running AutoGrid4 for Target...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Running AutoGrid4 for Target Protein...')
                    if prog == 'AutoLigand':
                        progress(self, 1, 2, 37, time=1000, mess='Searching Ligand Binding Site in Target...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Searching Ligand Binding Site in Target Protein...')
                    if prog == 'function GridDefinition: FILL Center':
                        progress(self, 0, 2, 37, mess='FILL Center Determination...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Center for Search Space in Target Protein...')
                elif self.parent.v.grid_def == 'by_residues':
                    if prog == 'function GridDefinition: Selected Residues Center':
                        progress(self, 0, 2, 25, mess='Determination of Selected Residues Center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Selected Residues Center in Target Protein...')
                    if prog == 'function GridDefinition: Protein Center':
                        progress(self, 0, 2, 26, mess='Determination of Protein center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Target Protein Center...')
                    if prog == 'Prepare_gpf4':
                        progress(self, 0, 2, 25, mess='Generate GPF file...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Generate GPF file for Target Protein...')
                    if prog == 'AutoGrid4':
                        self.part = 0
                        progress(self, 0, 2, 25, mess='Running AutoGrid4 for proein A...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Running AutoGrid4 for Target Protein...')
                    if prog == 'AutoLigand':
                        progress(self, 0, 2, 30, mess='Searching Ligand Binding Site in Target...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Searching Ligand Binding Site in Target Protein...')
                    if prog == 'function GridDefinition: FILL Center':
                        progress(self, 0, 2, 37, mess='FILL Center Determination...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Center for Search Space in Target Protein...')
                elif self.parent.v.grid_def == 'by_ligand':
                    if prog == 'function GridDefinition: Previous Ligand Center':
                        progress(self, 0, 2, 25, mess='Determination of Previous Ligand A Center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Center of Previous Ligand in Target Protein...')

                if self.parent.v.analog_grid_def == 'auto':
                    if prog == 'function GridDefinition: Zn Center B':
                        progress(self, 0, 2, 37, mess='Determination of Zn B center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Zn Center...')
                    if prog == 'function GridDefinition: Protein Center':
                        progress(self, 0, 2, 25, mess='Determination of Protein center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Off-Target Protein Center...')
                    if prog == 'Prepare_gpf4 B':
                        progress(self, 0, 2, 37, mess='Generate GPF file...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Generate GPF file for Off-Target Protein...')
                    if prog == 'AutoGrid4 B':
                        self.part = 0
                        progress(self, 0, 2, 37, mess='Running AutoGrid4 for Off-Target...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Running AutoGrid4 for Off-Target Protein...')
                    if prog == 'AutoLigand B':
                        progress(self, 1, 2, 50, time=1000, mess='Searching Ligand Binding Site in Off-Target...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Searching Ligand Binding Site in Off-Target Protein...')
                    if prog == 'function GridDefinition: FILL Center B':
                        progress(self, 0, 2, 37, mess='FILL Center Determination...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Center for Search Space in Off-Target Protein...')
                elif self.parent.v.analog_grid_def == 'by_residues':
                    if prog == 'function GridDefinition: Selected Residues Center':
                        progress(self, 0, 2, 25, mess='Determination of Selected Residues Center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD SDetermination of Selected Residues Center in Off-Target Protein...')
                    if prog == 'function GridDefinition: Protein Center B':
                        progress(self, 0, 2, 37, mess='Determination of Off-Target Center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Off-Target Protein Center...')
                    if prog == 'Prepare_gpf4 B':
                        progress(self, 0, 2, 38, mess='Generate GPF file...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Generate GPF file for Off-Target Protein...')
                    if prog == 'AutoGrid4 B':
                        self.part = 0
                        progress(self, 0, 2, 38, mess='Running AutoGrid4 for Off-Target...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Running AutoGrid4 for Off-Target Protein...')
                    if prog == 'AutoLigand B':
                        progress(self, 0, 2, 43, mess='Searching Ligand Binding Site in Off-Target...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Searching Ligand Binding Site in Off-Target Protein...')
                    if prog == 'function GridDefinition: FILL Center B':
                        progress(self, 0, 2, 50, mess='FILL Center Determination...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Center for Search Space in Off-Target Protein...')
                elif self.parent.v.analog_grid_def == 'by_ligand':
                    if prog == 'function GridDefinition: Previous Ligand Center B':
                        progress(self, 0, 2, 37, mess='Determination of Previous Ligand B Center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Center of Previous Ligand in Off-Target Protein...')
            else:
                if self.parent.v.grid_def == 'auto':

                    if prog == 'function GridDefinition: Protein Center':
                        progress(self, 0, 2, 25, mess='Determination of Protein center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Protein Center...')

                    if prog == 'Prepare_gpf4':
                        progress(self, 0, 2, 26, mess='Generate GPF file...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Generate GPF file for Protein...')

                    if prog == 'AutoGrid4':
                        self.part = 0
                        progress(self, 0, 2, 27, mess='Running AutoGrid4...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Running AutoGrid4 for Protein...')

                    if prog == 'AutoLigand':
                        progress(self, 1, 2, 50, time=1000, mess='Searching Ligand Binding Site...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Searching Ligand Binding Site in Protein...')
                    if prog == 'function GridDefinition: FILL Center B':
                        progress(self, 0, 2, 50, mess='FILL Center Determination...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Center for Search Space in Protein...')
                elif self.parent.v.grid_def == 'by_residues':
                    if prog == 'function GridDefinition: Selected Residues Center':
                        progress(self, 0, 2, 25, mess='Determination of Selected Residues Center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD SDetermination of Selected Residues Center in Protein...')
                    if prog == 'function GridDefinition: Protein Center':
                        progress(self, 0, 2, 26, mess='Determination of Protein center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Protein Center...')
                    if prog == 'Prepare_gpf4':
                        progress(self, 0, 2, 27, mess='Generate GPF file...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Generate GPF file for Protein...')
                    if prog == 'AutoGrid4':
                        self.part = 0
                        progress(self, 0, 2, 28, mess='Running AutoGrid4...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Running AutoGrid4 for Protein...')
                    if prog == 'AutoLigand':
                        progress(self, 0, 2, 38, mess='Searching Ligand Binding Site...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Searching Ligand Binding Site in Protein...')
                    if prog == 'function GridDefinition: FILL Center':
                        progress(self, 0, 2, 50, mess='FILL Center Determination...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Center for Search Space in Protein...')
                elif self.parent.v.grid_def == 'by_ligand':
                    if prog == 'function GridDefinition: Previous Ligand Center':
                        progress(self, 0, 2, 25, mess='Determination of Previous Ligand Center...')
                        self.parent.configuration_tab.log_wdw.textedit.append(
                            'AMDOCK: BSD Determination of Center of Previous Ligand in Protein...')
        elif self.queue_name == 'Molecular Docking Simulation':
            if self.parent.v.cr:
                if prog == 'AutoDock Vina':
                    self.part = 0
                    progress(self, 0, 2, 50, mess='Determining better poses for Target...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Determination of better poses for Target Protein...')
                if prog == 'AutoDock Vina B':
                    self.part = 0
                    progress(self, 0, 2, 75, mess='Determining better poses for Off-Target...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Determination of better poses for Off-Target Protein...')
                if prog == 'Prepare_gpf4':
                    progress(self, 0, 2, 50, mess='Generate GPF file...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Generate GPF file for Target Protein...')
                if prog == 'Prepare_gpf4 B':
                    progress(self, 0, 2, 75, mess='Generate GPF file...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Generate GPF file for Off-Target Protein...')
                if prog == 'AutoGrid4':
                    self.part = 0
                    progress(self, 0, 2, 50, mess='Running AutoGrid4 for Target...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Running AutoGrid4 for Target Protein...')
                if prog == 'AutoGrid4 B':
                    self.part = 0
                    progress(self, 0, 2, 75, mess='Running AutoGrid4 for Off-Target...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Running AutoGrid4 for Off-Target Protein...')
                if prog == 'Prepare_dpf4':
                    progress(self, 0, 2, 55, mess='Generate DPF file...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Generate DPF file for Target Protein...')
                if prog == 'Prepare_dpf4 B':
                    progress(self, 0, 2, 80, mess='Generate DPF file...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Generate DPF file for Off-Target Protein...')
                if prog == 'AutoDock4':
                    self.part = 0
                    progress(self, 0, 2, 55, mess='Determining better poses for Target...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Determination of better poses for Target Protein...')
                    self.timerAD = QtCore.QTimer()
                    self.timerAD.timeout.connect(self.autodock_output)
                    self.timerAD.start(5000)
                if prog == 'AutoDock4 B':
                    self.part = 0
                    progress(self, 0, 2, 80, mess='Determining better poses for Off-Target...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Determination of better poses for Off-Target Protein...')
                    self.timerAD = QtCore.QTimer()
                    self.timerAD.timeout.connect(self.autodock_output)
                    self.timerAD.start(5000)
                if prog == 'AutoDock4ZN':
                    self.part = 0
                    progress(self, 0, 2, 55, mess='Determining better poses for Target...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Determination of better poses for Target Protein...')
                    self.timerAD = QtCore.QTimer()
                    self.timerAD.timeout.connect(self.autodock_output)
                    self.timerAD.start(5000)
                if prog == 'AutoDock4ZN B':
                    self.part = 0
                    progress(self, 0, 2, 80, mess='Determining better poses for Off-Target...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Determination of better poses for Off-Target Protein...')
                    self.timerAD = QtCore.QTimer()
                    self.timerAD.timeout.connect(self.autodock_output)
                    self.timerAD.start(5000)
            else:
                if prog == 'AutoDock Vina':
                    self.part = 0
                    progress(self, 0, 2, 50, mess='Determining better poses...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Determination of better poses for Protein...')
                if prog == 'Prepare_gpf4':
                    progress(self, 0, 2, 50, mess='Generate GPF file...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Generate GPF file for Protein...')
                if prog == 'AutoGrid4':
                    self.part = 0
                    progress(self, 0, 2, 51, mess='Running AutoGrid4...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Running AutoGrid4 for Protein...')
                if prog == 'Prepare_dpf4':
                    progress(self, 0, 2, 59, mess='Generate DPF file...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Generate DPF file for Protein...')
                if prog == 'AutoDock4':
                    self.part = 0
                    progress(self, 0, 2, 60, mess='Determining better poses...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Determination of better poses for Protein...')
                    self.timerAD = QtCore.QTimer()
                    self.timerAD.timeout.connect(self.autodock_output)
                    self.timerAD.start(5000)
                if prog == 'AutoDock4ZN':
                    self.part = 0
                    progress(self, 0, 2, 60, mess='Determining better poses...')
                    self.parent.configuration_tab.log_wdw.textedit.append(
                        'AMDOCK: MDS Determination of better poses for Protein...')
                    self.timerAD = QtCore.QTimer()
                    self.timerAD.timeout.connect(self.autodock_output)
                    self.timerAD.start(5000)
        elif self.queue_name == 'Visualization':
            if self.prog == 'pymol_boxA':
                self.grid_pymol_buttonB.setEnabled(False)
                self.reset_grid_buttonB.setEnabled(False)
            elif self.prog == 'pymol_boxB':
                self.grid_pymol_button.setEnabled(False)
                self.reset_grid_button.setEnabled(False)
        elif self.queue_name == 'Construction':
            if self.prog == 'pymol_buildA':
                self.reset_grid_buttonB.setEnabled(False)
                self.reset_grid_buttonB.setEnabled(False)
            elif self.prog == 'pymol_buildB':
                self.reset_grid_button.setEnabled(False)
                self.reset_grid_button.setEnabled(False)

    def process_progress(self, prog, i, err):
        if prog == 'pymol_boxA' or prog == 'pymol_boxB' or prog == 'pymol_buildA' or prog == 'pymol_buildB':
            try:
                os.remove('pymol_data.txt')
            except:
                pass
        if prog in ['pymol_buildA', 'pymol_buildB', 'pymol_boxA', 'pymol_boxB']:
            # TODO: change status for pymol buttons
            self.grid_pymol_button.setEnabled(True)
            self.grid_pymol_buttonB.setEnabled(True)
            self.reset_grid_button.setEnabled(True)
            self.reset_grid_buttonB.setEnabled(True)
            # pass
        if self.queue_name == 'Prepare Input Files':
            if self.parent.v.cr:
                if prog == 'PDB2PQR':
                    if i == 0:
                        progress(self, 1, 1, 14, finish=True, mess='Running PDB2PQR for Target...')
                    else:
                        progress(self, 1, 1, 10, reverse=True, mess='Running PDB2PQR for Target...')
                elif prog == 'PDB2PQR B':
                    if i == 0:
                        progress(self, 1, 1, 18, finish=True, mess='Running PDB2PQR for Off-Target...')
                    else:
                        progress(self, 1, 1, 14, reverse=True, mess='Running PDB2PQR for Off-Target...')
                elif prog == 'Prepare_Receptor4':
                    if i == 0:
                        progress(self, 1, 1, 20, finish=True, mess='Prepare receptor A...')
                    else:
                        progress(self, 1, 1, 18, reverse=True, mess='Prepare receptor A...')
                elif prog == 'Prepare_Receptor4 B':
                    if i == 0:
                        progress(self, 1, 1, 22, finish=True, mess='Prepare receptor B...')
                    else:
                        progress(self, 1, 1, 20, reverse=True, mess='Prepare receptor B...')

                elif prog == 'Prepare_Ligand4':
                    if i == 0:
                        progress(self, 1, 1, 25, finish=True, mess='Prepare ligand...')
                    else:
                        progress(self, 1, 1, 22, reverse=True, mess='Prepare ligand...')
            else:
                if prog == 'PDB2PQR':
                    if i == 0:
                        progress(self, 1, 1, 18, finish=True, mess='Running PDB2PQR...')
                    else:
                        progress(self, 1, 1, 10, reverse=True, mess='Running PDB2PQR...')
                elif prog == 'Prepare_Receptor4':
                    if i == 0:
                        progress(self, 1, 1, 22, finish=True, mess='Prepare receptor...')
                    else:
                        progress(self, 1, 1, 18, reverse=True, mess='Prepare receptor...')
                elif prog == 'Prepare_Ligand4':
                    if i == 0:
                        progress(self, 1, 1, 25, finish=True, mess='Prepare ligand...')
                    else:
                        progress(self, 1, 1, 22, reverse=True, mess='Prepare ligand...')
        elif self.queue_name == 'Binding Site Determination':
            if self.parent.v.cr:
                if self.parent.v.grid_def == 'auto':
                    if prog == 'Prepare_gpf4':
                        if i == 0:
                            progress(self, 0, 2, 25, finish=True, mess='Generate GPF file...')
                        else:
                            progress(self, 0, 2, 25, reverse=True, mess='Generate GPF file...')
                    elif prog == 'AutoGrid4':
                        if i == 0:
                            progress(self, 0, 2, 30, finish=True, mess='Running AutoGrid4 for Target...')
                        else:
                            progress(self, 0, 2, 25, reverse=True, mess='Running AutoGrid4 for Target...')
                    elif prog == 'AutoLigand':
                        if i == 0:
                            progress(self, 0, 2, 37, finish=True, mess='Searching Ligand Binding Site in Target...')
                        else:
                            progress(self, 0, 2, 30, reverse=True, mess='Searching Ligand Binding Site in Target...')
                    elif prog == 'function GridDefinition: FILL Center':
                        if i == 0:
                            progress(self, 0, 2, 37, finish=True, mess='FILL Center Determination...')
                        else:
                            progress(self, 0, 2, 37, reverse=True, mess='FILL Center Determination...')
                elif self.parent.v.grid_def == 'by_residues':
                    if prog == 'function GridDefinition: Selected Residues Center':
                        if i == 0:
                            progress(self, 0, 2, 25, finish=True, mess='Determination of Selected Residues Center...')
                        else:
                            progress(self, 0, 2, 25, reverse=True, mess='Determination of Selected Residues Center...')
                    elif prog == 'function GridDefinition: Protein Center':
                        if i == 0:
                            progress(self, 0, 2, 25, finish=True, mess='Determination of Target center...')
                        else:
                            progress(self, 0, 2, 25, reverse=True, mess='Determination of Target center...')
                    elif prog == 'Prepare_gpf4':
                        if i == 0:
                            progress(self, 0, 2, 25, finish=True, mess='Generate GPF file...')
                        else:
                            progress(self, 0, 2, 25, reverse=True, mess='Generate GPF file...')
                    elif prog == 'AutoGrid4':
                        if i == 0:
                            progress(self, 0, 2, 30, finish=True, mess='Running AutoGrid4 for Target...')
                        else:
                            progress(self, 0, 2, 25, reverse=True, mess='Running AutoGrid4 for Target...')
                    elif prog == 'AutoLigand':
                        if i == 0:
                            progress(self, 0, 2, 37, finish=True, mess='Searching Ligand Binding Site in Target...')
                        else:
                            progress(self, 0, 2, 30, reverse=True, mess='Searching Ligand Binding Site in Target...')
                    elif prog == 'function GridDefinition: FILL Center':
                        if i == 0:
                            progress(self, 0, 2, 37, finish=True, mess='FILL Center Determination...')
                        else:
                            progress(self, 0, 2, 37, reverse=True, mess='FILL Center Determination...')
                elif self.parent.v.grid_def == 'by_ligand':
                    if prog == 'function GridDefinition: Previous Ligand Center':
                        if i == 0:
                            progress(self, 0, 2, 37, finish=True, mess='Determination of Previous Ligand A Center...')
                        else:
                            progress(self, 0, 2, 25, reverse=True, mess='Determination of Previous Ligand A Center...')

                if self.parent.v.analog_grid_def == 'auto':
                    if prog == 'function GridDefinition: Zn Center B':
                        if i == 0:
                            progress(self, 0, 2, 50, finish=True, mess='Determination of Zn B Center...')
                        else:
                            progress(self, 0, 2, 37, reverse=True, mess='Determination of Zn B Center...')
                    elif prog == 'Prepare_gpf4 B':
                        if i == 0:
                            progress(self, 0, 2, 38, finish=True, mess='Generate GPF file...')
                        else:
                            progress(self, 0, 2, 37, reverse=True, mess='Generate GPF file...')
                    elif prog == 'AutoGrid4 B':
                        if i == 0:
                            progress(self, 0, 2, 43, finish=True, mess='Running AutoGrid4...')
                        else:
                            progress(self, 0, 2, 38, reverse=True, mess='Running AutoGrid4...')
                    elif prog == 'AutoLigand B':
                        if i == 0:
                            progress(self, 1, 2, 50, finish=True, mess='Searching Ligand Binding Site...')
                        else:
                            progress(self, 1, 2, 43, reverse=True, mess='Searching Ligand Binding Site...')
                    elif prog == 'function GridDefinition: FILL Center B':
                        if i == 0:
                            progress(self, 0, 2, 50, finish=True, mess='FILL Center Determination...')
                        else:
                            progress(self, 0, 2, 50, reverse=True, mess='FILL Center Determination...')
                elif self.parent.v.analog_grid_def == 'by_residues':
                    if prog == 'function GridDefinition: Selected Residues Center B':
                        if i == 0:
                            progress(self, 0, 2, 38, finish=True, mess='Determination of Selected Residues Center...')
                        else:
                            progress(self, 0, 2, 37, reverse=True, mess='Determination of Selected Residues Center...')
                    elif prog == 'function GridDefinition: Protein Center B':
                        if i == 0:
                            progress(self, 0, 2, 38, finish=True, mess='Determination of Protein center...')
                        else:
                            progress(self, 0, 2, 38, reverse=True, mess='Determination of Protein center...')
                    elif prog == 'Prepare_gpf4 B':
                        if i == 0:
                            progress(self, 0, 2, 38, finish=True, mess='Generate GPF file...')
                        else:
                            progress(self, 0, 2, 38, reverse=True, mess='Generate GPF file...')
                    elif prog == 'AutoGrid4 B':
                        if i == 0:
                            progress(self, 0, 2, 43, finish=True, mess='Running AutoGrid4...')
                        else:
                            progress(self, 0, 2, 38, reverse=True, mess='Running AutoGrid4...')
                    elif prog == 'AutoLigand B':
                        if i == 0:
                            progress(self, 0, 2, 50, finish=True, mess='Searching Ligand Binding Site...')
                        else:
                            progress(self, 0, 2, 43, reverse=True, mess='Searching Ligand Binding Site...')
                    elif prog == 'function GridDefinition: FILL Center B':
                        if i == 0:
                            progress(self, 0, 2, 50, finish=True, mess='FILL Center Determination...')
                        else:
                            progress(self, 0, 2, 50, reverse=True, mess='FILL Center Determination...')
                elif self.parent.v.analog_grid_def == 'by_ligand':
                    if prog == 'function GridDefinition: Previous Ligand Center B':
                        if i == 0:
                            progress(self, 0, 2, 50, finish=True, mess='Determination of Previous Ligand Center...')
                        else:
                            progress(self, 0, 2, 37, reverse=True, mess='Determination of Previous Ligand Center...')
            else:
                if self.parent.v.grid_def == 'auto':
                    if prog == 'function GridDefinition: Protein Center':
                        if i == 0:
                            progress(self, 0, 2, 26, finish=True, mess='Determination of Protein Center...')
                        else:
                            progress(self, 0, 2, 25, reverse=True, mess='Determination of Protein Center...')
                    elif prog == 'Prepare_gpf4':
                        if i == 0:
                            progress(self, 0, 2, 27, finish=True, mess='Generate GPF file...')
                        else:
                            progress(self, 0, 2, 26, reverse=True, mess='Generate GPF file...')
                    elif prog == 'AutoGrid4':
                        if i == 0:
                            progress(self, 0, 2, 37, finish=True, mess='Running AutoGrid4...')
                        else:
                            progress(self, 0, 2, 27, reverse=True, mess='Running AutoGrid4...')
                    elif prog == 'AutoLigand':
                        if i == 0:
                            progress(self, 0, 2, 50, finish=True, mess='Searching Ligand Binding Site...')
                        else:
                            progress(self, 0, 2, 37, reverse=True, mess='Searching Ligand Binding Site...')
                    elif prog == 'function GridDefinition: FILL Center':
                        if i == 0:
                            progress(self, 0, 2, 50, finish=True, mess='FILL Center Determination...')
                        else:
                            progress(self, 0, 2, 50, reverse=True, mess='FILL Center Determination...')
                elif self.parent.v.grid_def == 'by_residues':
                    if prog == 'function GridDefinition: Selected Residues Center':
                        if i == 0:
                            progress(self, 0, 2, 25, finish=True, mess='Determination of Selected Residues Center...')
                        else:
                            progress(self, 0, 2, 25, reverse=True, mess='Determination of Selected Residues Center...')
                    elif prog == 'function GridDefinition: Protein Center':
                        if i == 0:
                            progress(self, 0, 2, 26, finish=True, mess='Determination of Protein center...')
                        else:
                            progress(self, 0, 2, 25, reverse=True, mess='Determination of Protein center...')
                    elif prog == 'Prepare_gpf4':
                        if i == 0:
                            progress(self, 0, 2, 27, finish=True, mess='Generate GPF file...')
                        else:
                            progress(self, 0, 2, 26, reverse=True, mess='Generate GPF file...')
                    elif prog == 'AutoGrid4':
                        if i == 0:
                            progress(self, 0, 2, 37, finish=True, mess='Running AutoGrid4...')
                        else:
                            progress(self, 0, 2, 27, reverse=True, mess='Running AutoGrid4...')
                    elif prog == 'AutoLigand':
                        if i == 0:
                            progress(self, 0, 2, 50, finish=True, mess='Searching Ligand Binding Site...')
                        else:
                            progress(self, 0, 2, 37, reverse=True, mess='Searching Ligand Binding Site...')
                    elif prog == 'function GridDefinition: FILL Center':
                        if i == 0:
                            progress(self, 0, 2, 50, finish=True, mess='FILL Center Determination...')
                        else:
                            progress(self, 0, 2, 50, reverse=True, mess='FILL Center Determination...')
                elif self.parent.v.grid_def == 'by_ligand':
                    if prog == 'function GridDefinition: Previous Ligand Center':
                        if i == 0:
                            progress(self, 0, 2, 50, finish=True, mess='Determination of Previous Ligand Center...')
                        else:
                            progress(self, 0, 2, 25, reverse=True, mess='Determination of Previous Ligand Center...')
        elif self.queue_name == 'Molecular Docking Simulation':
            if self.parent.v.cr:
                if prog == 'AutoDock Vina':
                    if i == 0:
                        progress(self, 0, 3, 75, finish=True, mess='Determining better poses for Target...')
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Determining better poses for Target...')
                if prog == 'AutoDock Vina B':
                    if i == 0:
                        progress(self, 0, 3, 100, finish=True, mess='Determining better poses for Off-Target...')
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Determining better poses for Off-Target...')
                if prog == 'Prepare_gpf4':
                    if i == 0:
                        progress(self, 0, 2, 51, finish=True, mess='Generate GPF file...')
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Generate GPF file...')
                if prog == 'Prepare_gpf4 B':
                    if i == 0:
                        progress(self, 0, 2, 76, finish=True, mess='Generate GPF file...')
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Generate GPF file...')
                if prog == 'AutoGrid4':
                    if i == 0:
                        progress(self, 0, 2, 55, finish=True, mess='Running AutoGrid4 for Target...')
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Running AutoGrid4 for Target...')
                if prog == 'AutoGrid4 B':
                    if i == 0:
                        progress(self, 0, 2, 80, finish=True, mess='Running AutoGrid4 for Off-Target...')
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Running AutoGrid4 for Off-Target...')
                if prog == 'Prepare_dpf4':
                    if i == 0:
                        progress(self, 0, 2, 56, finish=True, mess='Generate DPF file...')
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Generate DPF file...')
                if prog == 'Prepare_dpf4 B':
                    if i == 0:
                        progress(self, 0, 2, 81, finish=True, mess='Generate DPF file...')
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Generate DPF file...')
                if prog == 'AutoDock4':
                    if i == 0:
                        progress(self, 0, 2, 75, finish=True, mess='Determining better poses for Target...')
                        self.part = 0
                        self.timerAD.stop()
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Determining better poses for Target...')
                        self.timerAD.stop()
                if prog == 'AutoDock4 B':
                    if i == 0:
                        progress(self, 0, 2, 100, finish=True, mess='Determining better poses for Off-Target...')
                        self.part = 0
                        self.timerAD.stop()
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Determining better poses for Off-Target...')
                        self.timerAD.stop()
            else:
                if prog == 'AutoDock Vina':
                    if i == 0:
                        progress(self, 0, 3, 100, finish=True, mess='Determining better poses...')
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Determining better poses...')
                if prog == 'Prepare_gpf4':
                    if i == 0:
                        progress(self, 0, 2, 51, finish=True, mess='Generate GPF file...')
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Generate GPF file...')
                if prog == 'AutoGrid4':
                    if i == 0:
                        progress(self, 0, 2, 59, finish=True, mess='Running AutoGrid4...')
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Running AutoGrid4...')
                if prog == 'Prepare_dpf4':
                    if i == 0:
                        progress(self, 0, 2, 60, finish=True, mess='Generate DPF file...')
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Generate DPF file...')
                if prog == 'AutoDock4':
                    if i == 0:
                        progress(self, 0, 2, 100, finish=True, mess='Determining better poses...')
                        self.part = 0
                        self.timerAD.stop()
                    else:
                        progress(self, 0, 2, 50, reverse=True, mess='Determining better poses...')
                        self.timerAD.stop()

    def run_queue(self, prog, i, err):

        if i == 0:
            self.worker.start_process()
        elif i == -9999999999:
            error_warning(self, prog, err)
            self.reset_button.setEnabled(True)
        else:
            if prog == 'AutoDock4' or prog == 'AutoDock4 B' or prog == 'AutoDock4ZN' or prog == 'AutoDock4ZN B':
                error_warning(self, prog, 'The program was finalized manually or closed by the occurrence of an '
                                          'internal error.')
                self.reset_button.setEnabled(True)
            elif prog == 'AutoLigand':
                if self.parent.v.grid_def == 'by_residues':
                    select_res = QtGui.QMessageBox.critical(self, 'Warning',
                                                            'Autoligand has failed generating an object '
                                                            'centered on the selected residue(s) (See the Manual). Now the box will be centered on the '
                                                            'selected residues.\n Take into account that this could decrease the search space'
                                                            ' considerably. Do you wish to continue?',
                                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    if select_res == QtGui.QMessageBox.Yes:
                        os.rename(self.parent.v.res_center, self.parent.v.obj_center)
                        self.run_button.setEnabled(True)
                        self.reset_button.setEnabled(True)
                        self.reset_grid_button.setEnabled(True)
                        self.grid_pymol_button.setEnabled(True)
                        self.grid_box.setEnabled(True)
                        if self.parent.v.cr:
                            self.progressBar.setValue(37)
                        else:
                            self.progressBar.setValue(50)
                    else:
                        self.grid_box.setEnabled(True)
                        self.progressBar.setValue(25)
                        self.reset_button.setEnabled(True)
                        files = []
                        dd = '%s*.map' % self.parent.v.protein_name
                        files.extend(glob.glob(dd))
                        dd = '%s*.fld' % self.parent.v.protein_name
                        # files.extend(glob.glob('%s*.fld') % self.parent.v.protein_name)
                        files.extend(glob.glob(dd))
                        dd = '%s*.xyz' % self.parent.v.protein_name
                        # files.extend(glob.glob('%s*.xyz') % self.parent.v.protein_name)
                        # dd = '%s*.fld' % self.parent.v.protein_name
                        files.extend(glob.glob(dd))
                        # files.extend(glob.glob('%s*.gpf') % self.parent.v.protein_name)
                        dd = '%s*.gpf' % self.parent.v.protein_name
                        files.extend(glob.glob(dd))
                        files.extend([self.parent.v.res_center, self.parent.v.obj_center])
                        # os.get
                        for file in files:
                            try:
                                os.remove(file)
                            except:
                                pass
                else:
                    error_warning(self, prog, 'The program was finalized manually or closed by the occurrence of an '
                                              'internal error.')
                    self.grid_box.setEnabled(True)
                    self.reset_button.setEnabled(True)
            elif prog == 'AutoLigand B':
                if self.parent.v.analog_grid_def == 'by_residues':
                    select_res = QtGui.QMessageBox.critical(self, 'Warning',
                                                            'Autoligand has failed generating an object '
                                                            'centered on the selected residue(s) (See the Manual). Now the box will be centered on the '
                                                            'selected residues.\n Take into account that this could decrease the search space'
                                                            'considerably. Do you wish to continue?',
                                                            QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
                    if select_res == QtGui.QMessageBox.Yes:
                        os.rename(self.parent.v.res_center1, self.parent.v.obj_center1)
                        self.run_button.setEnabled(True)
                        self.progressBar.setValue(50)
                        self.reset_button.setEnabled(True)
                        self.reset_grid_buttonB.setEnabled(True)
                        self.grid_pymol_buttonB.setEnabled(True)
                    else:
                        try:
                            os.remove(glob.glob('%s*.map') % self.parent.v.analog_protein_name)
                        except:
                            pass
                        try:
                            os.remove(glob.glob('%s*.fld') % self.parent.v.analog_protein_name)
                        except:
                            pass
                        try:
                            os.remove(glob.glob('%s*.xyz') % self.parent.v.analog_protein_name)
                        except:
                            pass
                        try:
                            os.remove(glob.glob('%s*.gpf') % self.parent.v.analog_protein_name)
                        except:
                            pass
                        ##FIXME
                        self.grid_box.setEnabled(True)
                        self.progressBar.setValue(37)
                        self.reset_button.setEnabled(True)
                else:
                    error_warning(self, prog, 'The program was finalized manually or closed by the occurrence of an '
                                              'internal error.')
                    self.reset_button.setEnabled(True)
            else:
                error_warning(self, prog, err)
                self.reset_button.setEnabled(True)

    def readStdOutput(self):
        self.output = QtCore.QString(self.worker.readAllStandardOutput())
        print self.output

        self.out = str(self.output)
        if self.prog == 'AutoGrid4':
            if re.search('%', self.out):
                if self.part == 0:
                    try:
                        self.total = (int(self.out.split()[20]) * -2) + 1
                    except:
                        self.total = 100
                self.part += 1
                if self.queue_name == 'Binding Site Determination':
                    if self.parent.v.cr:
                        if self.parent.v.grid_def == 'auto':
                            try:
                                progress(self, 3, 2, [25, (self.part * 5) / self.total],
                                         mess='Running AutoGrid4 for Target...')
                            except:
                                pass
                        elif self.parent.v.grid_def == 'by_residues':
                            try:
                                progress(self, 3, 2, [25, (self.part * 5) / self.total],
                                         mess='Running AutoGrid4 for Target...')
                            except:
                                pass
                    else:
                        if self.parent.v.grid_def == 'auto':
                            try:
                                progress(self, 3, 2, [27, (self.part * 10) / self.total], mess='Running AutoGrid4...')
                            except:
                                pass
                        elif self.parent.v.grid_def == 'by_residues':
                            try:
                                progress(self, 3, 2, [28, (self.part * 9) / self.total], mess='Running AutoGrid4...')
                            except:
                                pass
                else:
                    if self.parent.v.cr:
                        try:
                            progress(self, 3, 2, [51, (self.part * 4) / self.total], mess='Running AutoGrid4...')
                        except:
                            pass
                    else:
                        try:
                            progress(self, 3, 2, [51, (self.part * 8) / self.total], mess='Running AutoGrid4...')
                        except:
                            pass
            if self.part == self.total:
                self.part = 0
        elif self.prog == 'AutoGrid4 B':
            if re.search('%', self.out):
                if self.part == 0:
                    try:
                        self.total = (int(self.out.split()[20]) * -2) + 1
                    except:
                        self.total = 100
                self.part += 1
                if self.queue_name == 'Binding Site Determination':
                    if self.parent.v.analog_grid_def == 'auto':
                        progress(self, 3, 2, [37, (self.part * 5) / self.total],
                                 mess='Running AutoGrid4 for Off-Target...')
                    elif self.parent.v.analog_grid_def == 'by_residues':
                        progress(self, 3, 2, [37, (self.part * 5) / self.total],
                                 mess='Running AutoGrid4 for Off-Target...')
                else:
                    progress(self, 3, 2, [76, (self.part * 4) / self.total], mess='Running AutoGrid4...')
            if self.part == self.total:
                self.part = 0
        elif self.prog == 'AutoDock Vina':
            v = 0
            self.total = 51
            if re.search('\*', self.out):
                self.part += self.out.count('*')
                if self.parent.v.cr:
                    progress(self, 3, 3, [50, (self.part * 25) / self.total],
                             mess='Running Molecular Docking Simulation...')
                else:
                    progress(self, 3, 3, [50, (self.part * 50) / self.total],
                             mess='Running Molecular Docking Simulation...')
            if self.part == self.total:
                self.part = 0
        elif self.prog == 'AutoDock Vina B':
            v = 0
            self.total = 51
            if re.search('\*', self.out):
                self.part += self.out.count('*')
                progress(self, 3, 2, [75, (self.part * 25) / self.total],
                         mess='Running Molecular Docking Simulation...')
            if self.part == self.total:
                self.part = 0

        if '*' in self.output:
            try:
                if v <= 50:
                    cursor = self.parent.configuration_tab.log_wdw.textedit.textCursor()
                    cursor.movePosition(cursor.PreviousWord)
                    cursor.insertText(self.output)
                else:
                    cursor = self.parent.configuration_tab.log_wdw.textedit.textCursor()
                    cursor.movePosition(cursor.End)
                    cursor.insertText(self.output)
                v += 1
            except:
                pass
        else:
            cursor = self.parent.configuration_tab.log_wdw.textedit.textCursor()
            cursor.movePosition(cursor.End)
            cursor.insertText(self.output)

    def readStdError(self):
        self.error = QtCore.QString(self.worker.readAllStandardError())

    def autodock_output(self):
        self.part_AD = 0
        # try:
        if self.parent.v.cr:
            if self.prog == 'AutoDock4' or self.prog == 'AutoDock4ZN':
                self.ADout_file = os.path.join(self.parent.v.result_dir, self.autodock_dlg)
            elif self.prog == 'AutoDock4 B' or self.prog == 'AutoDock4ZN B':
                self.ADout_file = os.path.join(self.parent.v.result_dir, self.autodock_dlgB)
        else:
            if self.prog == 'AutoDock4' or self.prog == 'AutoDock4ZN':
                self.ADout_file = os.path.join(self.parent.v.result_dir, self.autodock_dlg)
        ADout = open(self.ADout_file)
        try:
            for line in ADout:
                line = line.strip('\n')
                if re.search('DOCKED: MODEL', line):
                    self.part_AD += 1
                else:
                    continue

            if self.part != self.part_AD:
                self.part = self.part_AD
                if self.prog == 'AutoDock4' or self.prog == 'AutoDock4ZN':
                    if self.parent.v.cr:
                        progress(self, 3, 3, [54, self.part * 20 / self.parent.v.runs],
                                 mess='Determining better poses for Target...')
                    else:
                        progress(self, 3, 3, [59, self.part * 40 / self.parent.v.runs],
                                 mess='Determining better poses...')
                elif self.prog == 'AutoDock4 B' or self.prog == 'AutoDock4ZN B':
                    progress(self, 3, 3, [79, self.part * 20 / self.parent.v.runs],
                             mess='Determining better poses for Off-Target...')
            if self.part == self.parent.v.runs:
                self.part = 0
                self.timerAD.stop()

            ADout.close()
        except:
            pass

    def values(self, k):  # ok
        self.parent.v.pH = str(self.pH_value.value())

    def lig_select(self, lig):
        if lig.objectName() == 'lig_list':
            self.parent.v.selected_ligand = str(self.lig_list.currentText())
        else:
            self.parent.v.analog_selected_ligand = str(self.lig_listB.currentText())

    def amdock_load(self):
        elements = {0: 'Working Directory', 1: 'Input Directory', 2: 'Results Directory', 3: 'PDBQT of Target Protein',
                    4: 'All Poses File of Target Result', 5: 'Best Pose File of Target Result',
                    6: 'PDBQT of Off-Target Protein', 7: 'All Poses File of Off-Target Result',
                    8: 'Best Pose File of Off-Target Result'}
        elements_score = {0: 'Working Directory', 1: 'Input Directory', 2: 'Results Directory',
                          3: 'PDBQT of Target Protein', 4: 'PDBQT of Ligand'}
        self.parent.statusbar.showMessage(" Loading .amdock file...", 2000)
        # if self.
        self.data = self.parent.loader.load_amdock_file()
        if self.data is not None:
            if self.parent.v.cr:
                self.table1 = self.data[0]
                self.complete = self.data[1]
                self.table2 = self.data[2]
            else:
                self.table1 = self.data[0]
                self.complete = self.data[1]
            errlist = ''
            errlist2 = []
            if self.parent.v.program_mode is not 'SCORING':
                for index in range(0, len(self.complete)):
                    if self.complete[index] == '1':
                        errlist += '\n-%s' % elements[index]
                if len(errlist) != 0:
                    QtGui.QMessageBox.critical(self, 'Error', 'Some files defined in .amdock file were not found or '
                                                              'they are inaccessible.\nMissing elements:%s' % errlist)
                    self.parent.result_tab.import_text.clear()
                    self.parent.v = Variables()
                else:
                    os.chdir(self.parent.v.result_dir)
                    self.parent.result_tab.prot_label.setText('Target: %s' % self.parent.v.protein_name)
                    self.parent.result_tab.prot_label_sel.setText('%s' % self.parent.v.protein_name)
                    self.parent.result_tab.best_button.setEnabled(True)
                    self.parent.result_tab.all_button.setEnabled(True)

                    self.parent.result_tab.result_table.setRowCount(len(self.table1))
                    self.parent.result_tab.sele1.setRange(1, len(self.table1))
                    f = 0
                    for x in self.table1:
                        c = 0
                        for item in x:
                            item = str(item)
                            self.parent.result_tab.result_table.setItem(f, c, QtGui.QTableWidgetItem(item))
                            self.parent.result_tab.result_table.item(f, c).setTextAlignment(
                                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                            if c == 4:
                                item_v = float(item)
                                if item_v <= -0.3:
                                    self.parent.result_tab.result_table.item(f, c).setBackgroundColor(
                                        QtGui.QColor(0, 255, 128, 200))
                            c += 1
                        f += 1
                    self.parent.result_tab.value1 = float(self.parent.result_tab.result_table.item(0, 1).text())
                    self.parent.result_tab.result_table.item(0, 1).setBackgroundColor(QtGui.QColor('darkGray'))

                    if self.parent.v.cr:
                        self.parent.result_tab.prot_labelB.setText('Off-Target: %s' % self.parent.v.analog_protein_name)
                        self.parent.result_tab.prot_label_selB.setText('%s' % self.parent.v.analog_protein_name)
                        self.parent.result_tab.best_button.setText('Best Pose + Target')
                        self.parent.result_tab.all_button.setText('All Poses + Target')
                        self.parent.result_tab.best_buttonB.show()
                        self.parent.result_tab.all_buttonB.show()
                        self.parent.result_tab.result_tableB.show()
                        self.parent.result_tab.selectivity_value_text.show()
                        self.parent.result_tab.selectivity.show()
                        self.parent.result_tab.sele1.show()
                        self.parent.result_tab.sele2.show()
                        self.parent.result_tab.prot_label_sel.show()
                        self.parent.result_tab.prot_label_selB.show()
                        self.parent.result_tab.minus.show()
                        self.parent.result_tab.equal.show()
                        self.parent.result_tab.prot_labelB.show()

                        self.parent.result_tab.result_tableB.setRowCount(len(self.table2))
                        self.parent.result_tab.sele2.setRange(1, len(self.table2))
                        f = 0
                        for x in self.table2:
                            c = 0
                            for item in x:
                                item = str(item)
                                self.parent.result_tab.result_tableB.setItem(f, c, QtGui.QTableWidgetItem(item))
                                self.parent.result_tab.result_tableB.item(f, c).setTextAlignment(
                                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                                if c == 4:
                                    item_v = float(item)
                                    if item_v <= -0.3:
                                        self.parent.result_tab.result_tableB.item(f, c).setBackgroundColor(
                                            QtGui.QColor(0, 255, 128, 200))
                                c += 1
                            f += 1
                            self.parent.result_tab.value2 = float(
                                self.parent.result_tab.result_tableB.item(0, 1).text())
                        self.parent.result_tab.result_tableB.item(0, 1).setBackgroundColor(QtGui.QColor('darkGray'))
                        self.parent.result_tab.selectivity_value = self.parent.result_tab.value1 - self.parent.result_tab.value2
                        self.parent.result_tab.selectivity_value_text.setText(
                            '%s kcal/mol' % self.parent.result_tab.selectivity_value)
            else:
                for index in range(0, len(self.complete)):
                    if self.complete[index] == '1':
                        errlist += '\n-%s' % elements_score[index]
                        errlist2.append(index)
                if len(errlist) != 0:
                    QtGui.QMessageBox.critical(self, 'Error', 'Some files defined in .amdock file were not found or '
                                                              'they are inaccessible.\nMissing elements:%s' % errlist)
                    self.parent.result_tab.import_text.clear()
                    self.parent.v = Variables()
                else:
                    os.chdir(self.parent.v.result_dir)
                    self.parent.result_tab.prot_label.setText('Target: %s' % self.parent.v.protein_name)
                    self.parent.result_tab.best_button.hide()
                    self.parent.result_tab.all_button.hide()
                    self.parent.result_tab.show_complex.show()

                    self.parent.result_tab.result_table.setRowCount(len(self.table1))
                    self.parent.result_tab.sele1.setRange(1, len(self.table1))
                    f = 0
                    for x in self.table1:
                        c = 0
                        for item in x:
                            item = str(item)
                            self.parent.result_tab.result_table.setItem(f, c, QtGui.QTableWidgetItem(item))
                            self.parent.result_tab.result_table.item(f, c).setTextAlignment(
                                QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                            if c == 4:
                                item_v = float(item)
                                if item_v <= -0.3:
                                    self.parent.result_tab.result_table.item(f, c).setBackgroundColor(
                                        QtGui.QColor(0, 255, 128, 200))
                            c += 1
                        f += 1
                    self.parent.result_tab.result_table.item(0, 1).setBackgroundColor(QtGui.QColor('darkGray'))

    def load_file(self, file):  # ok
        if file.objectName() == 'create_project':
            if not self.wdir_loc:
                define_wdir_loc(self)
            else:
                if self.parent.v.WDIR:
                    self.options = wdir2_warning(self)
                    if self.options == QtGui.QMessageBox.Yes:
                        progress(self, 0, 0, 0, reverse=True, mess='Working Directory Definition...')
                        self.parent.output2file.conclude()
                        os.chdir(self.parent.v.loc_project)
                        shutil.rmtree(self.parent.v.WDIR)
                        if not self.parent.loader.create_project_function():
                            #TODO: poner un warning
                            pass
                        else:
                            self.proj_loc_label.setText('Project: %s' % self.parent.v.WDIR)
                            self.proj_loc_label.show()
                else:
                    if not self.parent.loader.create_project_function():
                        # TODO: poner un warning
                        pass
                    else:
                        self.proj_loc_label.setText('Project: %s' % self.parent.v.WDIR)
                        self.proj_loc_label.show()

        if file.text() == "Project Folder":
            self.wdir_loc = self.parent.loader.project_location()
            if self.wdir_loc:
                self.wdir_text.setText("%s" % self.wdir_loc)
                # self.create_project.setEnabled(True)

        if file.text() == "Load Data":
            if self.parent.v.amdock_file == None:
                self.parent.statusbar.showMessage(" Loading amdock file...", 2000)
                self.amdock_load()
            else:
                self.prot_opt = amdock_file_warning(self)
                if self.prot_opt == QtGui.QMessageBox.Yes:
                    self.parent.result_tab.clear_result_tab()
                    self.amdock_load()

        if file.objectName() == "protein_buttonA":
            if self.parent.v.input_target is None:
                self.parent.loader.load_protein()
            else:
                self.prot_opt = prot_warning(self)
                if self.prot_opt == QtGui.QMessageBox.Yes:
                    os.remove(self.parent.v.input_target)
                    self.parent.v.input_target = None
                    self.parent.v.metals = None
                    self.parent.v.ligands = None
                    self.parent.v.target_prepare = True
                    self.lig_list.hide()
                    self.lig_list.clear()
                    self.protein_label.clear()
                    self.protein_text.clear()
                    if self.parent.v.cr:
                        self.btnA_lig.show()
                        if self.parent.v.input_lig == None and self.parent.v.input_target == None:
                            progress(self, 0, 0, 2, reverse=True, mess='Target Definition...')
                        elif self.parent.v.input_lig == None and self.parent.v.input_target != None:
                            progress(self, 0, 0, 5, reverse=True, mess='Target Definition...')
                        elif self.parent.v.input_lig != None and self.parent.v.input_target == None:
                            progress(self, 0, 0, 4, reverse=True, mess='Target Definition...')
                        else:
                            progress(self, 0, 0, 7, reverse=True, mess='Target Definition...')
                    else:
                        if self.parent.v.input_lig is None:
                            progress(self, 0, 0, 2, reverse=True, mess='Protein Definition...')
                        else:
                            progress(self, 0, 0, 6, reverse=True, mess='Protein Definition...')
                    self.parent.loader.load_protein()
            if self.parent.v.input_target:
                if self.parent.v.docking_program == 'AutoDockZn':
                    self.check_opt = self.parent.checker.autodockzn_check('A')
                    if self.check_opt == QtGui.QMessageBox.Ok:
                        os.remove(self.parent.v.input_target)
                        self.parent.v.input_target = None
                        self.parent.v.metals = None
                        self.parent.v.ligands = None
                        self.btnA_lig.show()
                        self.protein_text.clear()
                        self.protein_label.clear()
                        if self.parent.v.cr:
                            if self.parent.v.input_lig is None and self.parent.v.input_target == None:
                                progress(self, 0, 0, 2, mess='Target Definition...')
                            elif self.parent.v.input_lig is None and self.parent.v.input_target != None:
                                progress(self, 0, 0, 5, mess='Target Definition...')
                            elif self.parent.v.input_lig is not None and self.parent.v.input_target == None:
                                progress(self, 0, 0, 4, mess='Target Definition...')
                            else:
                                progress(self, 0, 0, 7, mess='Target Definition...')
                        else:
                            if self.parent.v.input_lig is None:
                                progress(self, 0, 0, 2, reverse=True, mess='Protein Definition...')
                            else:
                                progress(self, 0, 0, 6, reverse=True, mess='Protein Definition...')

                    elif self.check_opt == QtGui.QMessageBox.Cancel:
                        self.parent.main_window.setCurrentIndex(0)
                        self.parent.main_window.setTabEnabled(1, False)
                        self.parent.main_window.setTabEnabled(0, True)
                else:
                    self.check_opt = self.parent.checker.check_correct_prog('A')
                    if self.check_opt == QtGui.QMessageBox.Yes:
                        if self.parent.v.analog_metals is None and self.parent.v.input_target is not None:
                            self.parent.v.input_target = None
                            self.protein_text.clear()
                            self.protein_text.clear()
                            self.protein_label.clear()
                            self.parent.loader.load_protein()
                        else:
                            self.parent.v.docking_program = "AutoDockZn"
                            self.parent.statusbar.showMessage(self.parent.v.docking_program + " is selected")
        if file.objectName() == "protein_buttonB":
            if self.parent.v.input_offtarget is None:
                self.parent.loader.load_proteinB()
            else:
                self.prot_opt = prot_warning(self)
                if self.prot_opt == QtGui.QMessageBox.Yes:
                    os.remove(self.parent.v.input_offtarget)
                    self.parent.v.analog_metals = None
                    self.parent.v.analog_ligands = None
                    self.parent.v.offtarget_prepare = True
                    self.lig_listB.clear()
                    self.lig_listB.hide()
                    self.btnB_lig.show()
                    self.protein_labelB.clear()
                    self.protein_textB.clear()
                    if self.parent.v.input_lig is None and self.parent.v.input_offtarget is None:
                        progress(self, 0, 0, 2, reverse=True, mess='Off-Target Definition...')
                    elif self.parent.v.input_lig is None and self.parent.v.input_offtarget is None:
                        progress(self, 0, 0, 5, reverse=True, mess='Off-Target Definition...')
                    elif self.parent.v.input_lig is not None and self.parent.v.input_offtarget is None:
                        progress(self, 0, 0, 4, reverse=True, mess='Off-Target Definition...')
                    else:
                        progress(self, 0, 0, 7, reverse=True, mess='Off-Target Definition...')
                    self.parent.loader.load_proteinB()
            if self.parent.v.input_offtarget:
                if self.parent.v.docking_program == 'AutoDockZn':
                    self.check_opt = self.parent.checker.autodockzn_check('B')
                    if self.check_opt == QtGui.QMessageBox.Ok:
                        os.remove(self.parent.v.input_offtarget)
                        self.parent.v.input_offtarget = None
                        self.btnB_lig.show()
                        self.parent.v.analog_metals = None
                        self.parent.v.analog_ligands = None
                        self.protein_textB.clear()
                        self.protein_labelB.clear()

                        if self.parent.v.input_lig == '' and self.parent.v.input_offtarget == None:
                            progress(self, 0, 0, 2, reverse=True, mess='Off-Target Definition...')
                        elif self.parent.v.input_lig == '' and self.parent.v.input_offtarget != None:
                            progress(self, 0, 0, 5, reverse=True, mess='Off-Target Definition...')
                        elif self.parent.v.input_lig != '' and self.parent.v.input_offtarget == None:
                            progress(self, 0, 0, 4, reverse=True, mess='Off-Target Definition...')
                        else:
                            progress(self, 0, 0, 7, reverse=True, mess='Off-Target Definition...')

                    elif self.check_opt == QtGui.QMessageBox.Cancel:
                        self.parent.main_window.setCurrentIndex(0)
                        self.parent.main_window.setTabEnabled(1, False)
                        self.parent.main_window.setTabEnabled(0, True)
                else:
                    self.check_opt = self.parent.checker.check_correct_prog('B')
                    if self.check_opt == QtGui.QMessageBox.Yes:
                        if self.parent.v.metals is None and self.parent.v.input_offtarget is not None:
                            self.parent.v.input_offtarget = None
                            self.btnB_lig.show()
                            self.parent.v.analog_metals = None
                            self.parent.v.analog_ligands = None
                            self.protein_textB.clear()
                            self.protein_labelB.clear()
                            self.parent.loader.load_proteinB()
                        else:
                            self.parent.v.docking_program = "AutoDockZn"
                            self.parent.statusbar.showMessage(self.parent.v.docking_program + " is selected")
        if file.text() == "Ligand":
            if self.parent.v.input_lig is None:
                self.parent.loader.load_ligand()
            else:
                self.lig_opt = lig_warning(self)
                if self.lig_opt == QtGui.QMessageBox.Yes:
                    os.remove(self.parent.v.input_lig)
                    self.parent.v.ligand_prepare = True
                    self.parent.v.ligand_pdbqt = None
                    self.ligand_text.clear()
                    self.ligand_label.clear()
                    if self.parent.v.cr:
                        if self.parent.v.input_offtarget == None and self.parent.v.input_target == None:
                            progress(self.parent.program_body, 0, 0, 2, reverse=True, mess='Ligand Definition...')
                        elif self.parent.v.input_offtarget == None and self.parent.v.input_target != None:
                            progress(self.parent.program_body, 0, 0, 5, reverse=True, mess='Ligand Definition...')
                        elif self.parent.v.input_offtarget != None and self.parent.v.input_target == None:
                            progress(self.parent.program_body, 0, 0, 5, reverse=True, mess='Ligand Definition...')
                        else:
                            progress(self.parent.program_body, 0, 0, 8, reverse=True, mess='Ligand Definition...')
                    else:

                        if self.parent.v.input_offtarget == None:
                            progress(self, 0, 0, 2, reverse=True, mess='Ligand Definition...')
                        else:
                            progress(self, 0, 0, 6, reverse=True, mess='Ligand Definition...')
                    self.parent.loader.load_ligand()

    def go_result(self):
        self.parent.v.amdock_file = os.path.normpath(
            os.path.join(self.parent.v.WDIR, self.parent.v.project_name + '.amdock'))

        self.parent.result_tab.import_text.setText(self.parent.v.amdock_file)
        self.parent.output2file.out2file('>> RESULT\n')
        self.parent.statusbar.showMessage(" Go to Results Analysis", 2000)
        self.parent.main_window.setTabEnabled(2, True)
        self.parent.main_window.setCurrentIndex(2)
        self.parent.main_window.setTabEnabled(1, False)
        self.parent.main_window.setTabEnabled(0, False)
        self.parent.result_tab.load_button.setEnabled(False)
        os.chdir(self.parent.v.result_dir)
        self.parent.result_tab.prot_label.setText('Target: %s' % self.parent.v.protein_name)
        self.parent.result_tab.prot_labelB.setText('Off-Target: %s' % self.parent.v.analog_protein_name)
        self.parent.result_tab.prot_label_sel.setText('%s' % self.parent.v.protein_name)
        self.parent.result_tab.prot_label_selB.setText('%s' % self.parent.v.analog_protein_name)
        self.parent.result_tab.best_button.setEnabled(True)
        self.parent.result_tab.all_button.setEnabled(True)
        self.parent.output2file.out2file('>  Target_Protein: %s\n' % self.parent.v.protein_name)
        if self.parent.v.docking_program == 'AutoDock Vina':
            self.parent.v.result_file = 'all_poses_target_ADV_result.pdb'
            self.parent.v.best_result_file = 'best_pose_target_ADV_result.pdb'
            vina_result = os.path.join(self.parent.v.result_dir, self.parent.v.ligand_name + '_h_out.pdbqt')
            self.re = Result_Analysis(vina_result, 'all_poses_target_ADV_result.pdb',
                                      os.path.join(self.parent.v.input_dir, self.parent.v.protein_pdbqt),
                                      self.parent.v.heavy_atoms)
            self.parent.output2file.out2file('>  all_poses_target_file: %s\n' % self.parent.v.result_file)
            self.parent.output2file.out2file('>  best_pose_target_file: %s\n' % self.parent.v.best_result_file)
        else:
            autodock_result = os.path.join(self.parent.v.result_dir, self.autodock_dlg)
            self.re = Result_Analysis(autodock_result, 'all_poses_target_AD4_result.pdb',
                                      os.path.join(self.parent.v.input_dir, self.parent.v.protein_pdbqt),
                                      self.parent.v.heavy_atoms)
            self.parent.v.result_file = 'all_poses_target_AD4_result.pdb'
            self.parent.v.best_result_file = 'best_pose_target_AD4_result.pdb'
            self.parent.output2file.out2file('>  all_poses_target_file: %s\n' % self.parent.v.result_file)
            self.parent.output2file.out2file('>  best_pose_target_file: %s\n' % self.parent.v.best_result_file)
        self.results = self.re.result2table()

        self.parent.output2file.out2file(
            ' ______________________________________________________________________________ \n'
            '|                                                                              |\n'
            '|'.ljust(1) + (' Result for %s' % self.parent.v.protein_name).ljust(78) + '|\n'
                                                                                       '|______________________________________________________________________________|\n'
                                                                                       '|               |                |              |               |              |\n'
                                                                                       '|     POSES     | BINDING ENERGY | ESTIMATED Ki |    Ki UNITS   |   LIGAND     |\n'
                                                                                       '|               |   (KCAL/MOL)   |              |               |  EFFICIENCY  |\n'
                                                                                       '|_______________|________________|______________|_______________|______________|\n')

        self.parent.result_tab.result_table.setRowCount(len(self.results))
        self.parent.result_tab.sele1.setRange(1, len(self.results))
        f = 0
        for x in self.results:
            c = 0
            out_line = '|' + ('%s' % x[0]).center(15) + '|' + ('%s' % x[1]).center(16) + '|' + ('%s' % x[2]).center(
                14) + '|' + ('%s' % x[3]).center(15) + '|' + ('%s' % x[4]).center(14) + '|\n'
            self.parent.output2file.out2file(out_line)
            for item in x:
                item = str(item)
                self.parent.result_tab.result_table.setItem(f, c, QtGui.QTableWidgetItem(item))
                self.parent.result_tab.result_table.item(f, c).setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                if c == 4:
                    item_v = float(item)
                    if item_v <= -0.3:
                        self.parent.result_tab.result_table.item(f, c).setBackgroundColor(
                            QtGui.QColor(0, 255, 128, 200))
                c += 1
            f += 1
            self.parent.result_tab.value1 = float(self.parent.result_tab.result_table.item(0, 1).text())
        self.parent.result_tab.result_table.item(0, 1).setBackgroundColor(QtGui.QColor('darkGray'))
        self.parent.output2file.out2file(
            '|_______________|________________|______________|_______________|______________|\n\n\n')

        if self.parent.v.cr:
            self.parent.result_tab.best_button.setText('Best Pose + Target')
            self.parent.result_tab.all_button.setText('All Poses + Target')
            self.parent.result_tab.best_buttonB.show()
            self.parent.result_tab.all_buttonB.show()
            self.parent.result_tab.result_tableB.show()
            self.parent.result_tab.selectivity_value_text.show()
            self.parent.result_tab.selectivity.show()
            self.parent.result_tab.sele1.show()
            self.parent.result_tab.sele2.show()
            self.parent.result_tab.prot_label_sel.show()
            self.parent.result_tab.prot_label_selB.show()
            self.parent.result_tab.minus.show()
            self.parent.result_tab.equal.show()
            self.parent.result_tab.prot_labelB.show()
            self.parent.output2file.out2file('>  Off-Target_Protein: %s\n' % self.parent.v.analog_protein_name)
            if self.parent.v.docking_program == 'AutoDock Vina':
                vina_resultB = os.path.join(self.parent.v.result_dir, self.parent.v.ligand_name + '_h_out2.pdbqt')
                self.reB = Result_Analysis(vina_resultB, 'all_poses_off-target_ADV_result.pdb',
                                           os.path.join(self.parent.v.input_dir, self.parent.v.analog_protein_pdbqt),
                                           self.parent.v.heavy_atoms)
                self.parent.v.analog_result_file = 'all_poses_off-target_ADV_result.pdb'
                self.parent.v.best_analog_result_file = 'best_pose_off-target_ADV_result.pdb'
                self.parent.output2file.out2file('>  all_poses_off-target_file: all_poses_off-target_ADV_result.pdb\n')
                self.parent.output2file.out2file('>  best_pose_off-target_file: best_pose_off-target_ADV_result.pdb\n')
            else:
                autodock_resultB = os.path.join(self.parent.v.result_dir, self.autodock_dlgB)
                self.reB = Result_Analysis(autodock_resultB, 'all_poses_off-target_AD4_result.pdb',
                                           os.path.join(self.parent.v.input_dir, self.parent.v.analog_protein_pdbqt),
                                           self.parent.v.heavy_atoms)
                self.parent.v.analog_result_file = 'all_poses_off-target_AD4_result.pdb'
                self.parent.v.best_analog_result_file = 'best_pose_off-target_AD4_result.pdb'
                self.parent.output2file.out2file('>  all_poses_off-target_file: all_poses_off-target_AD4_result.pdb\n')
                self.parent.output2file.out2file('>  best_pose_off-target_file: best_pose_off-target_AD4_result.pdb\n')
            self.resultsB = self.reB.result2table()

            self.parent.output2file.out2file(
                ' ______________________________________________________________________________ \n'
                '|                                                                              |\n'
                '|' + (' Result for %s' % self.parent.v.analog_protein_name).ljust(78) + '|\n'
                                                                                         '|______________________________________________________________________________|\n'
                                                                                         '|               |                |              |               |              |\n'
                                                                                         '|     POSES     | BINDING ENERGY | ESTIMATED Ki |    Ki UNITS   |   LIGAND     |\n'
                                                                                         '|               |   (KCAL/MOL)   |              |               |  EFFICIENCY  |\n'
                                                                                         '|_______________|________________|______________|_______________|______________|\n')
            self.parent.result_tab.result_tableB.setRowCount(len(self.resultsB))
            self.parent.result_tab.sele2.setRange(1, len(self.resultsB))
            f = 0
            for x in self.resultsB:
                c = 0
                out_line = '|' + ('%s' % x[0]).center(15) + '|' + ('%s' % x[1]).center(16) + '|' + ('%s' % x[2]).center(
                    14) + '|' + ('%s' % x[3]).center(15) + '|' + ('%s' % x[4]).center(14) + '|\n'
                self.parent.output2file.out2file(out_line)
                for item in x:
                    item = str(item)
                    self.parent.result_tab.result_tableB.setItem(f, c, QtGui.QTableWidgetItem(item))
                    self.parent.result_tab.result_tableB.item(f, c).setTextAlignment(
                        QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    if c == 4:
                        item_v = float(item)
                        if item_v <= -0.3:
                            self.parent.result_tab.result_tableB.item(f, c).setBackgroundColor(
                                QtGui.QColor(0, 255, 128, 200))
                    c += 1
                f += 1
                self.parent.result_tab.value2 = float(self.parent.result_tab.result_tableB.item(0, 1).text())
            self.parent.output2file.out2file(
                '|_______________|________________|______________|_______________|______________|\n\n\n')
            self.parent.result_tab.result_tableB.item(0, 1).setBackgroundColor(QtGui.QColor('darkGray'))
            self.parent.result_tab.selectivity_value = self.parent.result_tab.value1 - self.parent.result_tab.value2
            self.parent.result_tab.selectivity_value_text.setText(
                '%s kcal/mol' % self.parent.result_tab.selectivity_value)
            self.parent.output2file.out2file(
                '   Selectivity                        #Using only the best pose(smallest energy)\n')
            self.parent.output2file.out2file('   Target  -  Off-Target  =  selectivity\n')
            self.parent.output2file.out2file('   ' + ('%s' % self.parent.result_tab.value1).center(6) + '  -  ' + (
                    '%s' % self.parent.result_tab.value2).center(7) + '  =  ' + (
                                                     '%s' % self.parent.result_tab.selectivity_value).center(
                11) + 'kcal/mol\n')

        else:
            self.parent.result_tab.result_tableB.hide()
            self.parent.result_tab.selectivity_value_text.hide()
            self.parent.result_tab.selectivity.hide()
            self.parent.result_tab.sele1.hide()
            self.parent.result_tab.sele2.hide()
            self.parent.result_tab.prot_label_sel.hide()
            self.parent.result_tab.prot_label_selB.hide()
            self.parent.result_tab.minus.hide()
            self.parent.result_tab.equal.hide()
            self.parent.result_tab.prot_labelB.hide()
            self.parent.result_tab.best_button.setText('Show Best Pose')
            self.parent.result_tab.all_button.setText('Show All Poses')
            self.parent.result_tab.best_buttonB.hide()
            self.parent.result_tab.all_buttonB.hide()
        self.parent.output2file.conclude()

    def go_scoring(self):
        self.parent.v.amdock_file = os.path.normpath(os.path.join(self.parent.v.WDIR, self.parent.v.project_name + '.amdock'))
        self.parent.result_tab.import_text.setText(self.parent.v.amdock_file)
        self.parent.output2file.out2file('>> RESULT\n')
        self.parent.main_window.setTabEnabled(2, True)
        self.parent.main_window.setCurrentIndex(2)
        self.parent.main_window.setTabEnabled(1, False)
        self.parent.main_window.setTabEnabled(0, False)
        self.parent.result_tab.load_button.setEnabled(False)
        os.chdir(self.parent.v.result_dir)

        self.parent.result_tab.best_button.hide()
        self.parent.result_tab.all_button.hide()
        self.parent.result_tab.show_complex.show()
        self.parent.result_tab.prot_label.setText('Target: %s' % self.parent.v.protein_name)
        self.parent.output2file.out2file('>  Target_Protein: %s\n' % self.parent.v.protein_name)

        self.parent.result_tab.result_table.setRowCount(1)
        scoring_file = os.path.join(self.parent.v.result_dir, self.parent.v.ligand_name + '_score.log')
        self.scoring_re = Scoring2table(scoring_file, ha=self.parent.v.heavy_atoms)
        self.results = self.scoring_re.result2table()

        self.parent.output2file.out2file(
            ' ______________________________________________________________________________ \n'
            '|                                                                              |\n'
            '|'.ljust(1) + (' Result for %s' % self.parent.v.protein_name).ljust(78) + '|\n'
                                                                                       '|______________________________________________________________________________|\n'
                                                                                       '|               |                |              |               |              |\n'
                                                                                       '|     POSES     | BINDING ENERGY | ESTIMATED Ki |    Ki UNITS   |   LIGAND     |\n'
                                                                                       '|               |   (KCAL/MOL)   |              |               |  EFFICIENCY  |\n'
                                                                                       '|_______________|________________|______________|_______________|______________|\n')

        f = 0
        for x in self.results:
            c = 0
            out_line = '|' + ('%s' % x[0]).center(15) + '|' + ('%s' % x[1]).center(16) + '|' + ('%s' % x[2]).center(
                14) + '|' + ('%s' % x[3]).center(15) + '|' + ('%s' % x[4]).center(14) + '|\n'
            self.parent.output2file.out2file(out_line)
            for item in x:
                item = str(item)
                self.parent.result_tab.result_table.setItem(f, c, QtGui.QTableWidgetItem(item))
                self.parent.result_tab.result_table.item(f, c).setTextAlignment(
                    QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                if c == 4:
                    item_v = float(item)
                    if item_v <= -0.3:
                        self.parent.result_tab.result_table.item(f, c).setBackgroundColor(
                            QtGui.QColor(0, 255, 128, 200))
                c += 1
            f += 1
        self.parent.output2file.out2file(
            '|_______________|________________|______________|_______________|______________|\n\n\n')
        self.parent.output2file.conclude()

    def check_res(self, text):  # OKOK
        if text.objectName() == 'grid_predef_text':
            try:
                self.check = GridDefinition(self.parent.v.input_target, self.grid_predef_text.text())
                self.parent.v.error = self.check.check_select()
            except:
                self.parent.v.error = 1
            if self.parent.v.error == 0:
                self.checker_icon_ok.show()
                self.checker_icon.hide()
                if self.parent.v.cr:
                    if self.parent.v.analog_grid_def == 'auto':
                        self.bind_site_button.setEnabled(True)
                    elif self.parent.v.analog_grid_def == 'by_residues':
                        if self.parent.v.errorB == 0:
                            self.bind_site_button.setEnabled(True)
                        else:
                            self.bind_site_button.setEnabled(False)
                    elif self.parent.v.analog_grid_def == 'by_ligand':
                        self.bind_site_button.setEnabled(True)
                    else:
                        if self.parent.v.gerrorB == 0:
                            self.bind_site_button.setEnabled(True)
                        else:
                            self.bind_site_button.setEnabled(False)
                else:
                    self.bind_site_button.setEnabled(True)
            else:
                self.checker_icon.show()
                self.checker_icon_ok.hide()
                self.bind_site_button.setEnabled(False)
        else:
            try:
                self.check = GridDefinition(self.parent.v.input_offtarget, self.grid_predef_textB.text())
                self.parent.v.errorB = self.check.check_select()
            except:
                self.parent.v.errorB = 1
            if self.parent.v.errorB == 0:
                self.checker_icon_okB.show()
                self.checker_iconB.hide()

                if self.parent.v.grid_def == 'auto':
                    self.bind_site_button.setEnabled(True)
                elif self.parent.v.grid_def == 'by_residues':
                    if self.parent.v.error == 0:
                        self.bind_site_button.setEnabled(True)
                    else:
                        self.bind_site_button.setEnabled(False)
                elif self.parent.v.grid_def == 'by_ligand':
                    self.bind_site_button.setEnabled(True)
                else:
                    if self.parent.v.gerror == 0:
                        self.bind_site_button.setEnabled(True)
                    else:
                        self.bind_site_button.setEnabled(False)

            else:
                self.checker_iconB.show()
                self.checker_icon_okB.hide()
                self.bind_site_button.setEnabled(False)

    def check_grid(self):
        if self.parent.v.cr:
            if self.coor_x.text() != "" and self.coor_y.text() != "" and self.coor_z.text() != "" and self.size_x.text() != "" and self.size_y.text() != "" \
                    and self.size_z.text() != "" and self.coor_xB.text() != "" and self.coor_yB.text() != "" and self.coor_zB.text() != "" and self.size_xB.text() != "" and self.size_yB.text() != "" and self.size_zB.text() != "":
                self.bind_site_button.setEnabled(True)
            else:
                self.bind_site_button.setEnabled(False)
            if self.grid == 1:
                if self.coor_x.text() != "" and self.coor_y.text() != "" and self.coor_z.text() != "" \
                        and self.size_x.text() != "" and self.size_y.text() != "" \
                        and self.size_z.text() != "":
                    self.grid_icon_ok.show()
                    self.grid_icon.hide()
                    self.bind_site_button.setEnabled(True)
                    self.parent.v.gerror = 0
                else:
                    self.parent.v.gerror = 1
                    self.grid_icon.show()
                    self.grid_icon_ok.hide()
                    self.bind_site_button.setEnabled(False)
            elif self.grid == 2:
                if self.coor_xB.text() != "" and self.coor_yB.text() != "" and self.coor_zB.text() != "" and self.size_xB.text() != "" and self.size_yB.text() != "" and self.size_zB.text() != "":
                    self.grid_icon_okB.show()
                    self.grid_iconB.hide()
                    self.bind_site_button.setEnabled(True)
                    self.parent.v.gerrorB = 0
                else:
                    self.parent.v.gerrorB = 1
                    self.grid_iconB.show()
                    self.grid_icon_okB.hide()
                    self.bind_site_button.setEnabled(False)
            elif self.grid == 3:
                if self.coor_x.text() != "" and self.coor_y.text() != "" and self.coor_z.text() != "" \
                        and self.size_x.text() != "" and self.size_y.text() != "" and self.size_z.text() != "":
                    self.grid_icon_ok.show()
                    self.grid_icon.hide()
                    self.parent.v.gerror = 0
                else:
                    self.parent.v.gerror = 1
                    self.grid_icon.show()
                    self.grid_icon_ok.hide()
                if self.coor_xB.text() != "" and self.coor_yB.text() != "" and self.coor_zB.text() != "" \
                        and self.size_xB.text() != "" and self.size_yB.text() != "" and self.size_zB.text() != "":
                    self.grid_icon_okB.show()
                    self.grid_iconB.hide()
                    self.parent.v.gerrorB = 0
                else:
                    self.parent.v.gerrorB = 1
                    self.grid_iconB.show()
                    self.grid_icon_okB.hide()
        else:
            if self.coor_x.text() != "" and self.coor_y.text() != "" and self.coor_z.text() != "" \
                    and self.size_x.text() != "" and self.size_y.text() != "" \
                    and self.size_z.text() != "":
                self.grid_icon_ok.show()
                self.grid_icon.hide()
                self.bind_site_button.setEnabled(True)
            else:
                self.grid_icon.show()
                self.grid_icon_ok.hide()
                self.bind_site_button.setEnabled(False)

    def scoring(self):
        '''scoring'''
        self.reset_button.setEnabled(False)
        self.run_scoring.setEnabled(False)
        self.queue = Queue.Queue()
        if self.parent.v.docking_program == 'AutoDock Vina':
            scoring_vina_arg = ['--receptor', self.parent.v.protein_pdbqt, '--ligand', self.parent.v.ligand_pdbqt,
                                '--score_only', "--log", os.path.join(self.parent.v.result_dir,
                                                                      self.parent.v.ligand_name + '_score.log')]
            self.vina_score = {'AutoDock Vina Scoring': [self.ws.vina_exec, scoring_vina_arg]}
            self.queue.put(self.vina_score)
        elif self.parent.v.docking_program == 'AutoDock4':
            protein_gpf = str(self.parent.v.protein_pdbqt.split('.')[0] + '.gpf')
            protein_dlg = str(self.parent.v.protein_pdbqt.split('.')[0] + '.dlg')
            protein_dpf = str(self.parent.v.protein_pdbqt.split('.')[0] + '.dpf')

            prepare_gpf4_arg = [self.ws.prepare_gpf4_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                                str(self.parent.v.protein_pdbqt), '-f', self.parent.v.gd, '-p', 'spacing=%.3f' %
                                self.parent.v.spacing_autodock, '-p', 'npts=%d,%d,%d' % (
                                    self._size_x / self.parent.v.spacing_autodock,
                                    self._size_y / self.parent.v.spacing_autodock,
                                    self._size_z / self.parent.v.spacing_autodock)]
            self.prepare_gpf4 = {'Prepare_gpf4': [self.ws.this_python, prepare_gpf4_arg]}
            autogrid_arg = ['-p', protein_gpf]
            self.autogrid4 = {'AutoGrid4': [self.ws.autogrid, autogrid_arg]}
            prepare_dpf_arg = [self.ws.prepare_dpf_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                               str(self.parent.v.protein_pdbqt), '-e']
            self.prepare_dpf4 = {'Prepare_dpf4': [self.ws.this_python, prepare_dpf_arg]}
            self.autodock_dlg = str(self.parent.v.ligand_pdbqt.split('.')[0] + '_' + protein_dlg)
            autodock_arg = ['-p', str(self.parent.v.ligand_pdbqt.split('.')[0] + '_' + protein_dpf), '-l',
                            os.path.join(self.parent.v.result_dir, self.parent.v.ligand_name + '_score.log')]
            self.autodock = {'AutoDock4': [self.ws.autodock, autodock_arg]}
            self.list_process = [self.prepare_gpf4, self.autogrid4, self.prepare_dpf4, self.autodock]
            for process in self.list_process:
                self.queue.put(process)
        else:
            shutil.copy(self.ws.zn_ff, os.getcwd())
            protein_TZ = str(self.parent.v.protein_pdbqt.split('.')[0] + '_TZ.pdbqt')
            protein_gpf = str(self.parent.v.protein_pdbqt.split('.')[0] + '_TZ.gpf')
            protein_dlg = str(self.parent.v.protein_pdbqt.split('.')[0] + '_TZ.dlg')
            protein_dpf = str(self.parent.v.protein_pdbqt.split('.')[0] + '_TZ.dpf')
            pseudozn_arg = [self.ws.zinc_pseudo_py, '-r', str(self.parent.v.protein_pdbqt)]
            self.pseudozn = {'PseudoZn': [self.ws.this_python, pseudozn_arg]}
            prepare_gpf4zn_arg = [self.ws.prepare_gpf4zn_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                                  protein_TZ, '-f', self.parent.v.gd, '-p',
                                  'spacing=%.3f' % self.parent.v.spacing_autodock, '-p', 'npts=%d,%d,%d' %
                                  (self._size_x / self.parent.v.spacing_autodock,
                                   self._size_y / self.parent.v.spacing_autodock,
                                   self._size_z / self.parent.v.spacing_autodock), '-p',
                                  'parameter_file=AD4Zn.dat']
            self.prepare_gpf4zn = {'Prepare_gpf4zn': [self.ws.this_python, prepare_gpf4zn_arg]}
            autogridzn_arg = ['-p', protein_gpf]
            self.autogrid4 = {'AutoGrid4': [self.ws.autogrid, autogridzn_arg]}
            prepare_dpfzn_arg = [self.ws.prepare_dpf_py, '-l', str(self.parent.v.ligand_pdbqt), '-r', protein_TZ, '-e']
            self.prepare_dfp4zn = {'Prepare_dpf4': [self.ws.this_python, prepare_dpfzn_arg]}
            self.autodock_dlg = str(self.parent.v.ligand_pdbqt.split('.')[0] + '_' + protein_dlg)
            autodockzn_arg = ['-p', str(self.parent.v.ligand_pdbqt.split('.')[0] + '_' + protein_dpf),
                              '-l', os.path.join(self.parent.v.result_dir, self.parent.v.ligand_name + '_score.log')]
            self.autodockzn = {'AutoDock4ZN': [self.ws.autodock, autodockzn_arg]}
            self.list_process = [self.pseudozn, self.prepare_gpf4zn, self.autogrid4, self.prepare_dfp4zn,
                                 self.autodockzn]
            for process in self.list_process:
                self.queue.put(process)
        self.worker.init(self.queue, 'Scoring Process')
        self.worker.start_process()

    def bind_site_by_user(self):
        self.progressBar.setValue(50)

    def stop_docking(self):
        self.stop_opt = stop_warning(self)
        if self.stop_opt == QtGui.QMessageBox.Yes:
            self.worker.__del__()
            self.stop_button.setEnabled(False)
            self.run_button.setEnabled(True)
            self.reset_button.setEnabled(True)

    def prepare_receptor(self):
        self.reset_button.setEnabled(False)
        self.parent.configuration_tab.log_wdw.textedit.append(
            'AMDOCK: IP DOCKING_PROGRAM: %s' % self.parent.v.docking_program)
        self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IP MODE: %s' % self.parent.v.program_mode)
        self.parent.configuration_tab.log_wdw.textedit.append(
            'AMDOCK: IP TARGET_PROTEIN: %s' % self.parent.v.protein_name)
        self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IP    Ligands: %s' % self.parent.v.ligands)
        self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IP    Metals(Zn): %s' % self.parent.v.metals)
        self.parent.configuration_tab.log_wdw.textedit.append(
            'AMDOCK: IP OFF-TARGET_PROTEIN: %s' % self.parent.v.analog_protein_name)
        self.parent.configuration_tab.log_wdw.textedit.append(
            'AMDOCK: IP    Ligands: %s' % self.parent.v.analog_ligands)
        self.parent.configuration_tab.log_wdw.textedit.append(
            'AMDOCK: IP    Metals(Zn): %s' % self.parent.v.analog_metals)
        self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IP LIGAND: %s' % self.parent.v.ligand_name)
        self.parent.configuration_tab.log_wdw.textedit.append(
            'AMDOCK: IP    heavy_atoms: %s' % self.parent.v.heavy_atoms)
        self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IP Defining Initial Parameters... Done\n')
        self.parent.configuration_tab.log_wdw.textedit.append('AMDOCK: IF Prepare Initial Files...')

        self.parent.output2file.out2file('>> DOCKING_PROGRAM: %s\n' % self.parent.v.docking_program)
        self.parent.output2file.out2file('>> MODE: %s\n' % self.parent.v.program_mode)
        self.parent.output2file.out2file('>> TARGET_PROTEIN: %s\n' % self.parent.v.protein_name)
        self.parent.output2file.out2file('>  Target_Ligands: %s\n' % self.parent.v.ligands)
        self.parent.output2file.out2file('>  Target_Metals(Zn): %s\n' % self.parent.v.metals)
        if self.parent.v.cr:
            self.parent.output2file.out2file('>> OFF-TARGET_PROTEIN: %s\n' % self.parent.v.analog_protein_name)
            self.parent.output2file.out2file('>  Off-Target_Ligands: %s\n' % self.parent.v.analog_ligands)
            self.parent.output2file.out2file('>  Off-Target_Metals(Zn): %s\n' % self.parent.v.analog_metals)
        self.parent.output2file.out2file('>> LIGAND: %s\n' % self.parent.v.ligand_name)
        self.parent.output2file.out2file('>  heavy_atoms: %s\n' % self.parent.v.heavy_atoms)

        progress(self, 0, 1, 10, mess='')
        os.chdir(self.parent.v.input_dir)
        self.input_box.setEnabled(False)

        if self.parent.v.target_prepare:
            self.parent.v.protein_pqr = self.parent.v.protein_name + '_h.pqr'
            self.parent.v.protein_h = self.parent.v.protein_name + '_h.pdb'
            self.parent.v.protein_pdbqt = self.parent.v.protein_name + '_h.pdbqt'
        if self.parent.v.ligand_prepare:
            self.parent.v.ligand_h = self.parent.v.ligand_name + "_h.pdb"
            self.parent.v.ligand_pdbqt = self.parent.v.ligand_name + '_h.pdbqt'
        if self.parent.v.cr:
            if self.parent.v.offtarget_prepare:
                self.parent.v.analog_protein_pqr = self.parent.v.analog_protein_name + '_h.pqr'
                self.parent.v.analog_protein_h = self.parent.v.analog_protein_name + '_h.pdb'
                self.parent.v.analog_protein_pdbqt = self.parent.v.analog_protein_name + '_h.pdbqt'
        self.list_process = []
        if self.parent.v.target_prepare:
            self.pdb2pqr = {'PDB2PQR': [self.ws.this_python, [self.ws.pdb2pqr_py, '--ph-calc-method=propka',
                                                              '--verbose', '--noopt', '--drop-water', '--chain',
                                                              '--with-ph', str(self.parent.v.pH),
                                                              '--ff=%s' % self.parent.v.forcefield,
                                                              self.parent.v.protein_file,
                                                              self.parent.v.protein_pqr]]}
            if self.parent.v.metals is not None:
                fix_pqr_arg = [self.parent.v.protein_file, self.parent.v.protein_pqr, True]
            else:
                fix_pqr_arg = [self.parent.v.protein_file, self.parent.v.protein_pqr]
            self.fix_pqr = {'function Fix_PQR': [Fix_PQR, fix_pqr_arg]}

            prepare_receptor4_arg = [self.ws.prepare_receptor4_py, '-r', self.parent.v.protein_h, '-v', '-U',
                                     'nphs_lps_waters_nonstdres_deleteAltB']
            self.prepare_receptor4 = {'Prepare_Receptor4': [self.ws.this_python, prepare_receptor4_arg]}
        if self.parent.v.offtarget_prepare:
            self.pdb2pqrB = {'PDB2PQR B': [self.ws.this_python, [self.ws.pdb2pqr_py, '--ph-calc-method=propka',
                                                                 '--verbose', '--noopt', '--drop-water', '--chain',
                                                                 '--with-ph', str(self.parent.v.pH),
                                                                 '--ff=%s' % self.parent.v.forcefield,
                                                                 self.parent.v.analog_protein_file,
                                                                 self.parent.v.analog_protein_pqr]]}
            if self.parent.v.analog_metals:
                fix_pqr_argB = [self.parent.v.analog_protein_file, self.parent.v.analog_protein_pqr, True]
            else:
                fix_pqr_argB = [self.parent.v.analog_protein_file, self.parent.v.analog_protein_pqr]

            self.fix_pqrB = {'function Fix_PQR B': [Fix_PQR, fix_pqr_argB]}
            prepare_receptor4_argB = [self.ws.prepare_receptor4_py, '-r', self.parent.v.analog_protein_h, '-v', '-U',
                                      'nphs_lps_waters_nonstdres_deleteAltB']
            self.prepare_receptor4B = {'Prepare_Receptor4 B': [self.ws.this_python, prepare_receptor4_argB]}
        if self.parent.v.ligand_prepare:
            protonate_ligand_arg = ['-i', 'pdb', self.parent.v.ligand_pdb, '-opdb', '-O', self.parent.v.ligand_h, '-h',
                                    '-p', `self.parent.v.pH`]
            self.protonate_ligand = {'Protonate Ligand': [self.parent.ws.openbabel, protonate_ligand_arg]}

            prepare_ligand4_arg = [self.ws.prepare_ligand4_py, '-l', self.parent.v.ligand_h, '-v', '-o',
                                   self.parent.v.ligand_pdbqt]
            self.prepare_ligand4 = {'Prepare_Ligand4': [self.ws.this_python, prepare_ligand4_arg]}
        if self.parent.v.cr:
            if self.parent.v.target_prepare:
                self.list_process.append(self.pdb2pqr)
                self.list_process.append(self.fix_pqr)
                self.list_process.append(self.prepare_receptor4)
            if self.parent.v.offtarget_prepare:
                self.list_process.append(self.pdb2pqrB)
                self.list_process.append(self.fix_pqrB)
                self.list_process.append(self.prepare_receptor4B)
            if self.parent.v.ligand_prepare:
                self.list_process.append(self.protonate_ligand)
                self.list_process.append(self.prepare_ligand4)
        else:
            if self.parent.v.target_prepare:
                self.list_process.append(self.pdb2pqr)
                self.list_process.append(self.fix_pqr)
                self.list_process.append(self.prepare_receptor4)
            if self.parent.v.ligand_prepare:
                self.list_process.append(self.protonate_ligand)
                self.list_process.append(self.prepare_ligand4)
        if self.parent.v.scoring and self.parent.v.docking_program != 'AutoDock Vina':
            prev_ligand_arg = [self.parent.v.protein_file, None, None, self.parent.v.gd, False]
            self.previous_ligand = {'function GridDefinition: Previous Ligand Center': [GridDefinition,
                                                                                        prev_ligand_arg]}
            self.queue = Queue.Queue()
            self.queue.put(self.previous_ligand)
            self.worker.init(self.queue, 'Binding Site Determination')
            self.worker.start_process()
            self._size_x = self._size_y = self._size_z = self.parent.v.rg
        self.queue = Queue.Queue()
        for process in self.list_process:
            self.queue.put(process)
        self.worker.init(self.queue, 'Prepare Input Files')
        self.worker.start_process()
        self.need_grid = self.need_gridB = True

    def binding_site(self):
        """
        mide las dimensiones de la proteina
        prepare_gpf4
        ejecuta auto grid
        ejecuta autoligand
        determina el centro del objeto
        """
        self.reset_button.setEnabled(False)
        self.grid_box.setEnabled(False)
        self._size_x = self._size_y = self._size_z = self._size_xB = self._size_yB = self._size_zB = self.parent.v.rg
        self.parent.v.FILL = 'FILL_%dout1.pdb' % (6 * self.parent.v.heavy_atoms)
        self.parent.v.selected_residues = self.grid_predef_text.text()
        self.parent.v.analog_selected_residues = self.grid_predef_textB.text()
        process_list = []
        if self.parent.v.grid_def == 'auto':
            prot_dimension_arg = [self.parent.v.protein_pdbqt, None, None, self.parent.v.gd, False]
            self.prot_center = {'function GridDefinition: Protein Center': [GridDefinition, prot_dimension_arg]}
            prepare_gpf4_arg = [self.ws.prepare_gpf4_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                                str(self.parent.v.protein_pdbqt), '-f', self.parent.v.gd, '-p',
                                'spacing=%.3f' % self.parent.v.spacing_autoligand, '-o',
                                str(self.parent.v.protein_name + '_autolig.gpf')]
            self.prepare_gpf4 = {'Prepare_gpf4': [self.ws.this_python, prepare_gpf4_arg]}
            autogrid_arg = ['-p', str(self.parent.v.protein_name + '_autolig.gpf')]
            self.autogrid4 = {'AutoGrid4': [self.ws.autogrid, autogrid_arg]}
            autoligand_arg = [str(self.ws.autoligand_py), '-r', str(self.parent.v.protein_pdbqt[:-6]), '-a',
                              str(self.parent.v.heavy_atoms)]
            self.autoligand = {'AutoLigand': [self.ws.this_python, autoligand_arg]}
            # dimension_FILL = [self.parent.v.FILL, None, None, self.parent.v.obj_center, False]
            # TODO: realizar el paso de la info del autoligand a la tabla
            # self.FILL_center = {'function GridDefinition: FILL Center': [GridDefinition, dimension_FILL]}
            self.list_process = [self.prot_center, self.prepare_gpf4, self.autogrid4, self.autoligand]#,self.FILL_center]
            if self.need_grid:
                process_list.extend(self.list_process)
        elif self.parent.v.grid_def == "by_residues":
            res_center_arg = [self.parent.v.protein_pdbqt, str(self.parent.v.selected_residues), None,
                              self.parent.v.res_center, False]
            self.res_center = {'function GridDefinition: Selected Residues Center': [GridDefinition, res_center_arg]}
            prot_dimension_arg = [self.parent.v.protein_pdbqt, None, None, self.parent.v.gd, False]
            self.prot_center = {'function GridDefinition: Protein Center': [GridDefinition, prot_dimension_arg]}
            prepare_gpf4_arg = [self.ws.prepare_gpf4_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                                str(self.parent.v.protein_pdbqt), '-f', self.parent.v.gd, '-p',
                                'spacing=%.3f' % self.parent.v.spacing_autoligand, '-o',
                                str(self.parent.v.protein_name + '_autolig.gpf')]
            self.prepare_gpf4 = {'Prepare_gpf4': [self.ws.this_python, prepare_gpf4_arg]}
            autogrid_arg = ['-p', str(self.parent.v.protein_name + '_autolig.gpf')]
            self.autogrid4 = {'AutoGrid4': [self.ws.autogrid, autogrid_arg]}
            autoligand_arg = [str(self.ws.autoligand_py), '-r', str(self.parent.v.protein_pdbqt[:-6]), '-a',
                              str(self.parent.v.heavy_atoms), '-h', self.parent.v.res_center]
            self.autoligand = {'AutoLigand': [self.ws.this_python, autoligand_arg]}
            # TODO: realizar el paso de la info del autoligand a la tabla
            # dimension_FILL = [self.parent.v.FILL, None, None, self.parent.v.obj_center, False]
            # self.FILL_center = {'function GridDefinition: FILL Center': [GridDefinition, dimension_FILL]}
            self.list_process = [self.res_center, self.prot_center, self.prepare_gpf4, self.autogrid4, self.autoligand]
                #,self.FILL_center]
            if self.need_grid:
                process_list.extend(self.list_process)
        elif self.parent.v.grid_def == "by_ligand":
            prev_ligand_arg = [self.parent.v.input_target, None, str(self.parent.v.selected_ligand),
                               self.parent.v.obj_center, True]
            self.previous_ligand = {
                'function GridDefinition: Previous Ligand Center': [GridDefinition, prev_ligand_arg]}
            self.list_process = [self.previous_ligand]
            if self.need_grid:
                process_list.extend(self.list_process)
        elif self.parent.v.grid_def == 'by_user':
            if self.need_grid:
                obj = open(self.parent.v.obj_center, 'w')
                obj.write('center_x = ' + self.coor_x.text() + '\n')
                obj.write('center_y = ' + self.coor_y.text() + '\n')
                obj.write('center_z = ' + self.coor_z.text() + '\n')
                obj.close()
                self.siz_x = int(self.size_x.text())
                self.siz_y = int(self.size_y.text())
                self.siz_z = int(self.size_z.text())
                if self.siz_x < self.parent.v.rg or self.siz_y < self.parent.v.rg or self.siz_z < self.parent.v.rg:
                    self.grid_opt, self.dim_list = smallbox_warning(self, {'x': self.siz_x, 'y': self.siz_y,
                                                                           'z': self.siz_z}, self.parent.v.rg,
                                                                    self.parent.v.protein_name)
                    if self.grid_opt == QtGui.QMessageBox.Yes:
                        if 'x' in self.dim_list:
                            self.siz_x = self.parent.v.rg
                            self.size_x.setText(str(self.parent.v.rg))
                        if 'y' in self.dim_list:
                            self.siz_y = self.parent.v.rg
                            self.size_y.setText(str(self.parent.v.rg))
                        if 'z' in self.dim_list:
                            self.siz_z = self.parent.v.rg
                            self.size_z.setText(str(self.parent.v.rg))
                self._size_x = self.siz_x
                self._size_y = self.siz_y
                self._size_z = self.siz_z

                if self.parent.v.cr:
                    if self.need_gridB:
                        self.progressBar.setValue(37)
                    else:
                        self.progressBar.setValue(50)
                else:
                    self.progressBar.setValue(50)
        if self.parent.v.cr:
            if self.parent.v.analog_grid_def == 'auto':
                prot_dimension_argB = [self.parent.v.analog_protein_pdbqt, None, None, self.parent.v.gd1, False]
                self.prot_centerB = {'function GridDefinition: Protein Center B': [GridDefinition, prot_dimension_argB]}
                prepare_gpf4_argB = [self.ws.prepare_gpf4_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                                     str(self.parent.v.analog_protein_pdbqt), '-f', self.parent.v.gd1, '-p',
                                     'spacing=%.3f' % self.parent.v.spacing_autoligand, '-o',
                                     str(self.parent.v.analog_protein_name + '_autolig.gpf')]
                self.prepare_gpf4B = {'Prepare_gpf4 B': [self.ws.this_python, prepare_gpf4_argB]}

                autogrid_argB = ['-p', str(self.parent.v.analog_protein_name + '_autolig.gpf')]
                self.autogrid4B = {'AutoGrid4 B': [self.ws.autogrid, autogrid_argB]}

                autoligand_argB = [str(self.ws.autoligand_py), '-r', str(self.parent.v.analog_protein_pdbqt[:-6]), '-a',
                                   str(self.parent.v.heavy_atoms)]
                self.autoligandB = {'AutoLigand B': [self.ws.this_python, autoligand_argB]}
                # TODO: realizar el paso de la info del autoligand a la tabla
                # dimension_FILLB = [self.parent.v.FILL, None, None, self.parent.v.obj_center1, False]
                # self.FILL_centerB = {'function GridDefinition: FILL Center B': [GridDefinition, dimension_FILLB]}
                self.list_process = [self.prot_centerB, self.prepare_gpf4B, self.autogrid4B, self.autoligandB]
                #self.FILL_centerB]
                if self.need_gridB:
                    process_list.extend(self.list_process)
            elif self.parent.v.analog_grid_def == "by_residues":
                res_center_arg = [self.parent.v.analog_protein_pdbqt, str(self.parent.v.analog_selected_residues), None,
                                  self.parent.v.res_center1, None]
                self.res_center = {
                    'function GridDefinition: Selected Residues Center B': [GridDefinition, res_center_arg]}
                prot_dimension_arg = [self.parent.v.analog_protein_pdbqt, None, None, self.parent.v.gd1, False]
                self.prot_center = {'function GridDefinition: Protein Center B': [GridDefinition, prot_dimension_arg]}
                prepare_gpf4_arg = [self.ws.prepare_gpf4_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                                    str(self.parent.v.analog_protein_pdbqt), '-f', self.parent.v.gd1, '-p',
                                    'spacing=%.3f' % self.parent.v.spacing_autoligand, '-o',
                                    str(self.parent.v.analog_protein_name + '_autolig.gpf')]
                self.prepare_gpf4 = {'Prepare_gpf4 B': [self.ws.this_python, prepare_gpf4_arg]}
                autogrid_arg = ['-p', str(self.parent.v.analog_protein_name + '_autolig.gpf')]
                self.autogrid4 = {'AutoGrid4 B': [self.ws.autogrid, autogrid_arg]}
                autoligand_arg = [str(self.ws.autoligand_py), '-r', str(self.parent.v.analog_protein_pdbqt[:-6]), '-a',
                                  str(self.parent.v.heavy_atoms), '-h', self.parent.v.res_center1]

                self.autoligand = {'AutoLigand B': [self.ws.this_python, autoligand_arg]}
                # TODO: realizar el paso de la info del autoligand a la tabla
                # dimension_FILL = [self.parent.v.FILL, None, None, self.parent.v.obj_center1, False]
                # self.FILL_center = {'function GridDefinition: FILL Center B': [GridDefinition, dimension_FILL]}
                self.list_process = [self.res_center, self.prot_center, self.prepare_gpf4, self.autogrid4,
                                     self.autoligand]#, self.FILL_center]
                if self.need_gridB:
                    process_list.extend(self.list_process)
            elif self.parent.v.analog_grid_def == "by_ligand":
                prev_ligand_arg = [self.parent.v.input_offtarget, None, str(self.parent.v.analog_selected_ligand),
                                   self.parent.v.obj_center1, True]
                self.previous_ligandB = {
                    'function GridDefinition: Previous Ligand Center B': [GridDefinition, prev_ligand_arg]}
                self.list_process = [self.previous_ligandB]
                if self.need_gridB:
                    process_list.extend(self.list_process)
            elif self.parent.v.analog_grid_def == 'by_user':
                if self.need_gridB:
                    obj = open(self.parent.v.obj_center1, 'w')
                    obj.write('center_x = ' + self.coor_xB.text() + '\n')
                    obj.write('center_y = ' + self.coor_yB.text() + '\n')
                    obj.write('center_z = ' + self.coor_zB.text() + '\n')
                    obj.close()
                    self.siz_xB = int(self.size_xB.text())
                    self.siz_yB = int(self.size_yB.text())
                    self.siz_zB = int(self.size_zB.text())
                    if self.siz_xB < self.parent.v.rg or self.siz_yB < self.parent.v.rg or self.siz_zB < self.parent.v.rg:
                        self.grid_optB, self.dim_listB = smallbox_warning(self, {'x': self.siz_xB, 'y': self.siz_yB,
                                                                                 'z': self.siz_zB}, self.parent.v.rg,
                                                                          self.parent.v.analog_protein_name)
                        if self.grid_optB == QtGui.QMessageBox.Yes:
                            if 'x' in self.dim_listB:
                                self.siz_xB = self.parent.v.rg
                                self.size_xB.setText(str(self.parent.v.rg))
                            if 'y' in self.dim_listB:
                                self.siz_yB = self.parent.v.rg
                                self.size_yB.setText(str(self.parent.v.rg))
                            if 'z' in self.dim_listB:
                                self.siz_zB = self.parent.v.rg
                                self.size_zB.setText(str(self.parent.v.rg))
                    self.progressBar.setValue(50)
                    self._size_xB = self.siz_xB
                    self._size_yB = self.siz_yB
                    self._size_zB = self.siz_zB
        self.queue = Queue.Queue()
        for process in process_list:
            self.queue.put(process)
        self.worker.init(self.queue, 'Binding Site Determination')
        self.worker.start_process()

    def start_docking_prog(self):
        try:
            self.b_pymol.__del__()
        except:
            pass
        try:
            self.b_pymolB.__del__()
        except:
            pass
        try:
            self.b_pymol_timerB.stop()
        except:
            pass
        try:
            self.b_pymol_timer.stop()
        except:
            pass
        self.need_grid = self.need_gridB = True

        self.reset_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.run_button.setEnabled(False)
        self.grid_box.setEnabled(False)

        if self.parent.v.docking_program == 'AutoDock Vina':
            vina_arg = ['--receptor', self.parent.v.protein_pdbqt, '--ligand', self.parent.v.ligand_pdbqt,
                        '--config', `self.parent.v.obj_center`, '--size_x', '%d' % self._size_x, '--size_y',
                        '%d' % self._size_y, '--size_z', '%d' % self._size_z, '--cpu', `self.parent.v.ncpu`,
                        '--num_modes', `self.parent.v.poses_vina`, '--exhaustiveness',
                        `self.parent.v.exhaustiveness`, "--out", os.path.join(self.parent.v.result_dir,
                                                                              self.parent.v.ligand_name + '_h_out.pdbqt'),
                        "--log", os.path.join(self.parent.v.result_dir, self.parent.v.ligand_name + '_h_out.log')]
            vina_argB = ['--receptor', self.parent.v.analog_protein_pdbqt, '--ligand', self.parent.v.ligand_pdbqt,
                         '--config', `self.parent.v.obj_center1`, '--size_x', '%d' % self._size_xB, '--size_y',
                         '%d' % self._size_yB, '--size_z', '%d' % self._size_zB, '--cpu', `self.parent.v.ncpu`,
                         '--num_modes', `self.parent.v.poses_vina`, '--exhaustiveness', `self.parent.v.exhaustiveness`,
                         "--out", os.path.join(self.parent.v.result_dir, self.parent.v.ligand_name + '_h_out2.pdbqt'),
                         "--log", os.path.join(self.parent.v.result_dir, self.parent.v.ligand_name + '_h_out2.log')]

            self.vina = {'AutoDock Vina': [self.ws.vina_exec, vina_arg]}
            self.vinaB = {'AutoDock Vina B': [self.ws.vina_exec, vina_argB]}
            self.queue = Queue.Queue()
            self.queue.put(self.vina)
            if self.parent.v.cr:
                self.queue.put(self.vinaB)
            self.worker.init(self.queue, 'Molecular Docking Simulation')
            self.worker.start_process()
        elif self.parent.v.docking_program == 'AutoDock4':
            protein_gpf = str(self.parent.v.protein_pdbqt.split('.')[0] + '.gpf')
            protein_dlg = str(self.parent.v.protein_pdbqt.split('.')[0] + '.dlg')
            protein_dpf = str(self.parent.v.protein_pdbqt.split('.')[0] + '.dpf')
            prepare_gpf4_arg = [self.ws.prepare_gpf4_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                                str(self.parent.v.protein_pdbqt), '-f', self.parent.v.obj_center, '-p', 'spacing=%.3f' %
                                self.parent.v.spacing_autodock, '-p', 'npts=%d,%d,%d' % (
                                    self._size_x / self.parent.v.spacing_autodock,
                                    self._size_y / self.parent.v.spacing_autodock,
                                    self._size_z / self.parent.v.spacing_autodock)]
            self.prepare_gpf4 = {'Prepare_gpf4': [self.ws.this_python, prepare_gpf4_arg]}
            autogrid_arg = ['-p', protein_gpf]
            self.autogrid4 = {'AutoGrid4': [self.ws.autogrid, autogrid_arg]}
            prepare_dpf_arg = [self.ws.prepare_dpf_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                               str(self.parent.v.protein_pdbqt), '-p', 'rmstol=%s' % self.parent.v.rmsd, '-p',
                               'ga_num_evals=%s' % self.parent.v.eval, '-p', 'ga_run=%s' % self.parent.v.runs]
            self.prepare_dpf4 = {'Prepare_dpf4': [self.ws.this_python, prepare_dpf_arg]}

            self.autodock_dlg = str(self.parent.v.ligand_pdbqt.split('.')[0] + '_' + protein_dlg)
            autodock_arg = ['-p', str(self.parent.v.ligand_pdbqt.split('.')[0] + '_' + protein_dpf), '-l',
                            os.path.join(self.parent.v.result_dir, self.autodock_dlg)]
            self.autodock = {'AutoDock4': [self.ws.autodock, autodock_arg]}
            self.list_process = [self.prepare_gpf4, self.autogrid4, self.prepare_dpf4, self.autodock]
            if self.parent.v.cr:
                proteinB_gpf = str(self.parent.v.analog_protein_pdbqt.split('.')[0] + '.gpf')
                proteinB_dlg = str(self.parent.v.analog_protein_pdbqt.split('.')[0] + '.dlg')
                proteinB_dpf = str(self.parent.v.analog_protein_pdbqt.split('.')[0] + '.dpf')

                prepare_gpf4_argB = [self.ws.prepare_gpf4_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                                     str(self.parent.v.analog_protein_pdbqt), '-f', self.parent.v.obj_center1, '-p',
                                     'spacing=%.3f' % self.parent.v.spacing_autodock, '-p', 'npts=%d,%d,%d' % (
                                         self._size_xB / self.parent.v.spacing_autodock,
                                         self._size_yB / self.parent.v.spacing_autodock,
                                         self._size_zB / self.parent.v.spacing_autodock)]
                self.prepare_gpf4B = {'Prepare_gpf4 B': [self.ws.this_python, prepare_gpf4_argB]}

                autogrid_argB = ['-p', proteinB_gpf]
                self.autogrid4B = {'AutoGrid4 B': [self.ws.autogrid, autogrid_argB]}

                prepare_dpf_argB = [self.ws.prepare_dpf_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                                    str(self.parent.v.analog_protein_pdbqt), '-p', 'rmstol=%s' % self.parent.v.rmsd,
                                    '-p', 'ga_num_evals=%s' % self.parent.v.eval, '-p',
                                    'ga_run=%s' % self.parent.v.runs]
                self.prepare_dpf4B = {'Prepare_dpf4 B': [self.ws.this_python, prepare_dpf_argB]}

                self.autodock_dlgB = str(self.parent.v.ligand_pdbqt.split('.')[0] + '_' + proteinB_dlg)
                autodock_argB = ['-p', str(self.parent.v.ligand_pdbqt.split('.')[0] + '_' + proteinB_dpf),
                                 '-l', os.path.join(self.parent.v.result_dir, self.autodock_dlgB)]
                self.autodockB = {'AutoDock4 B': [self.ws.autodock, autodock_argB]}

                self.list_processB = [self.prepare_gpf4B, self.autogrid4B, self.prepare_dpf4B, self.autodockB]
                self.list_process.extend(self.list_processB)

            self.queue = Queue.Queue()
            for process in self.list_process:
                self.queue.put(process)
            self.worker.init(self.queue, 'Molecular Docking Simulation')
            self.worker.start_process()
        elif self.parent.v.docking_program == 'AutoDockZn':
            shutil.copy(self.ws.zn_ff, os.getcwd())

            protein_TZ = str(self.parent.v.protein_pdbqt.split('.')[0] + '_TZ.pdbqt')
            protein_gpf = str(self.parent.v.protein_pdbqt.split('.')[0] + '_TZ.gpf')
            protein_dlg = str(self.parent.v.protein_pdbqt.split('.')[0] + '_TZ.dlg')
            protein_dpf = str(self.parent.v.protein_pdbqt.split('.')[0] + '_TZ.dpf')

            pseudozn_arg = [self.ws.zinc_pseudo_py, '-r', str(self.parent.v.protein_pdbqt)]
            self.pseudozn = {'PseudoZn': [self.ws.this_python, pseudozn_arg]}

            prepare_gpf4zn_arg = [self.ws.prepare_gpf4zn_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                                  protein_TZ, '-f', self.parent.v.obj_center, '-p',
                                  'spacing=%.3f' % self.parent.v.spacing_autodock, '-p', 'npts=%d,%d,%d' %
                                  (self._size_x / self.parent.v.spacing_autodock,
                                   self._size_y / self.parent.v.spacing_autodock,
                                   self._size_z / self.parent.v.spacing_autodock), '-p',
                                  'parameter_file=AD4Zn.dat']
            self.prepare_gpf4zn = {'Prepare_gpf4zn': [self.ws.this_python, prepare_gpf4zn_arg]}

            autogridzn_arg = ['-p', protein_gpf]
            self.autogrid4 = {'AutoGrid4': [self.ws.autogrid, autogridzn_arg]}

            prepare_dpfzn_arg = [self.ws.prepare_dpf_py, '-l', str(self.parent.v.ligand_pdbqt), '-r', protein_TZ, '-p',
                                 'rmstol=%s' % self.parent.v.rmsd,
                                 '-p', 'ga_num_evals=%s' % self.parent.v.eval, '-p', 'ga_run=%s' % self.parent.v.runs]
            self.prepare_dfp4zn = {'Prepare_dpf4': [self.ws.this_python, prepare_dpfzn_arg]}

            self.autodock_dlg = str(self.parent.v.ligand_pdbqt.split('.')[0] + '_' + protein_dlg)
            autodockzn_arg = ['-p', str(self.parent.v.ligand_pdbqt.split('.')[0] + '_' + protein_dpf),
                              '-l', os.path.join(self.parent.v.result_dir, self.autodock_dlg)]
            self.autodockzn = {'AutoDock4ZN': [self.ws.autodock, autodockzn_arg]}
            self.list_process = [self.pseudozn, self.prepare_gpf4zn, self.autogrid4, self.prepare_dfp4zn,
                                 self.autodockzn]
            if self.parent.v.cr:
                proteinB_TZ = str(self.parent.v.analog_protein_pdbqt.split('.')[0] + '_TZ.pdbqt')
                proteinB_gpf = str(self.parent.v.analog_protein_pdbqt.split('.')[0] + '_TZ.gpf')
                proteinB_dlg = str(self.parent.v.analog_protein_pdbqt.split('.')[0] + '_TZ.dlg')
                proteinB_dpf = str(self.parent.v.analog_protein_pdbqt.split('.')[0] + '_TZ.dpf')

                pseudozn_argB = [self.ws.zinc_pseudo_py, '-r', str(self.parent.v.analog_protein_pdbqt)]
                self.pseudoznB = {'PseudoZn B': [self.ws.this_python, pseudozn_argB]}

                prepare_gpf4zn_argB = [self.ws.prepare_gpf4zn_py, '-l', str(self.parent.v.ligand_pdbqt), '-r',
                                       proteinB_TZ, '-f', self.parent.v.obj_center1, '-p',
                                       'spacing=%.3f' % self.parent.v.spacing_autodock, '-p', 'npts=%d,%d,%d' %
                                       (self._size_xB / self.parent.v.spacing_autodock,
                                        self._size_yB / self.parent.v.spacing_autodock,
                                        self._size_zB / self.parent.v.spacing_autodock), '-p',
                                       'parameter_file=AD4Zn.dat']
                self.prepare_gpf4znB = {'Prepare_gpf4zn B': [self.ws.this_python, prepare_gpf4zn_argB]}

                autogridzn_argB = ['-p', proteinB_gpf]
                self.autogrid4B = {'AutoGrid4 B': [self.ws.autogrid, autogridzn_argB]}

                prepare_dpfzn_argB = [self.ws.prepare_dpf_py, '-l', str(self.parent.v.ligand_pdbqt), '-r', proteinB_TZ,
                                      '-p', 'rmstol=%s' % self.parent.v.rmsd,
                                      '-p', 'ga_num_evals=%s' % self.parent.v.eval, '-p',
                                      'ga_run=%s' % self.parent.v.runs]
                self.prepare_dfp4znB = {'Prepare_dpf4 B': [self.ws.this_python, prepare_dpfzn_argB]}

                self.autodock_dlgB = str(self.parent.v.ligand_pdbqt.split('.')[0] + '_' + proteinB_dlg)
                autodockzn_argB = ['-p', str(self.parent.v.ligand_pdbqt.split('.')[0] + '_' + proteinB_dpf),
                                   '-l', os.path.join(self.parent.v.result_dir, self.autodock_dlgB)]
                self.autodockznB = {'AutoDock4ZN B': [self.ws.autodock, autodockzn_argB]}

                self.list_processB = [self.pseudoznB, self.prepare_gpf4znB, self.autogrid4B, self.prepare_dfp4znB,
                                      self.autodockznB]
                self.list_process.extend(self.list_processB)

            self.queue = Queue.Queue()
            for process in self.list_process:
                self.queue.put(process)
            self.worker.init(self.queue, 'Molecular Docking Simulation')
            self.worker.start_process()
