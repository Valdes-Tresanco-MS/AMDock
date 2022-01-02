import math
import os
import re
import shutil

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from queue import Queue
from AMDock.command_runner import PROCESS, THREAD
from AMDock.result2tab import Result_Analysis
from AMDock.qradialbar import QRadialBar
from AMDock.tools import Fix_PQR, PDBINFO, BASE, PROJECT, Convert, FormatedText as Ft
from AMDock.warning import (wdir2_warning, prot_warning, lig_warning, stop_warning, smallbox_warning,
                     reset_warning, define_wdir_loc, error_message)


class Program_body(QWidget):
    def __init__(self, parent=None):
        super(Program_body, self).__init__(parent)
        self.setObjectName("program_body")
        self.AMDock = parent
        with open(self.AMDock.style_file) as f:
            self.setStyleSheet(f.read())

        self.part = 0
        self.total = 0
        self.grid = 0
        self.size = [30, 30, 30]
        self.sizeB = [30, 30, 30]
        self.grid_center = ['', '', '']
        self.grid_centerB = ['', '', '']
        self.lig_size = 0
        self.need_grid = True
        self.need_gridB = True
        self.build = self.buildB = False
        self.process_list = []

        self.sc_area = QScrollArea(self)
        self.sc_area_widget = QWidget()

        # **project_box
        self.project_box = QGroupBox(self.sc_area_widget)
        self.project_box.setObjectName("project_box")
        self.project_box.setTitle("Project")
        self.project_box.setToolTip(self.AMDock.project_tt)

        self.project_label = QLabel(self.project_box)
        self.project_label.setText("Project Name:")

        self.project_text = QLineEdit(self.project_box)
        self.project_text.setObjectName("project_text")
        self.project_text.setPlaceholderText(self.AMDock.project_name)
        self.proj_name_validator = QRegExpValidator(QRegExp("\\S+"))
        self.project_text.setValidator(self.proj_name_validator)

        self.wdir_button = QPushButton(self.project_box)
        self.wdir_button.setObjectName("wdir_button")
        self.wdir_button.setText("Project Folder")
        self.wdir_button.clicked.connect(lambda: self.load_file(self.wdir_button))

        self.wdir_text = QLineEdit(self.project_box)
        self.wdir_text.setReadOnly(True)
        self.wdir_text.setObjectName("wdir_text")
        self.wdir_text.setPlaceholderText("Location for the project")

        self.proj_loc_label = QLabel()
        self.proj_loc_label.hide()

        self.project_layout = QGridLayout()
        self.project_layout.addWidget(self.project_label, 0, 0)
        self.project_layout.addWidget(self.project_text, 0, 1, 1, 1)
        self.project_layout.addWidget(self.wdir_button, 1, 0)
        self.project_layout.addWidget(self.wdir_text, 1, 1, 1, 1)
        self.project_layout.addWidget(self.proj_loc_label, 2, 0, 1, 3)

        self.create_project = QPushButton('Create \nProject')
        self.create_project.setObjectName('create_project')
        self.create_project.clicked.connect(lambda: self.load_file(self.create_project))

        self.project_box_layout = QHBoxLayout(self.project_box)
        self.project_box_layout.addLayout(self.project_layout, 10)
        self.project_box_layout.addWidget(self.create_project)

        # **Input_box
        self.input_box = QGroupBox(self.sc_area_widget)
        self.input_box.setObjectName("input_box")
        self.input_box.setTitle("Input")
        self.input_box.setToolTip(self.AMDock.input_tt)

        self.pH_label = QLabel(self.input_box)
        self.pH_label.setObjectName("ph_button")
        self.pH_label.setText("Set pH:")

        self.pH_value = QDoubleSpinBox(self.input_box)
        self.pH_value.setAlignment(Qt.AlignCenter)
        self.pH_value.setDecimals(1)
        self.pH_value.setMinimum(0)
        self.pH_value.setMaximum(14)
        self.pH_value.setSingleStep(0.1)
        self.pH_value.setValue(self.AMDock.pH)
        self.pH_value.setObjectName("pH_value")

        self.docking_mode = QButtonGroup(self.input_box)

        self.simple_docking = QRadioButton('Simple Docking', self.input_box)
        self.simple_docking.setObjectName("simple_docking")
        self.simple_docking.setChecked(True)
        self.docking_mode.addButton(self.simple_docking, 1)

        self.offtarget_docking = QRadioButton('Off-Target Docking', self.input_box)
        self.offtarget_docking.setObjectName("offtarget_docking")
        self.docking_mode.addButton(self.offtarget_docking, 2)

        self.rescoring = QRadioButton('Scoring', self.input_box)
        self.rescoring.setObjectName("rescoring")
        self.docking_mode.addButton(self.rescoring, 3)

        self.target_button = QPushButton(self.input_box)
        self.target_button.setObjectName("target_button")
        self.target_button.setText("Target")
        self.target_button.clicked.connect(lambda: self.load_file(self.target_button))

        self.target_text = QLineEdit(self.input_box)
        self.target_text.setObjectName("target_text")
        self.target_text.setReadOnly(True)
        self.target_text.setPlaceholderText('Target protein')

        self.target_label = QLabel(self.input_box)
        self.target_label.hide()

        self.offtarget_button = QPushButton(self.input_box)
        self.offtarget_button.setObjectName("offtarget_button")
        self.offtarget_button.setText("Off-Target")
        self.offtarget_button.hide()
        self.offtarget_button.clicked.connect(lambda: self.load_file(self.offtarget_button))

        self.offtarget_text = QLineEdit(self.input_box)
        self.offtarget_text.setObjectName("offtarget_text")
        self.offtarget_text.setReadOnly(True)
        self.offtarget_text.setPlaceholderText('off-target protein')
        self.offtarget_text.hide()

        self.offtarget_label = QLabel(self.input_box)
        self.offtarget_label.hide()

        self.ligand_button = QPushButton(self.input_box)
        self.ligand_button.setObjectName("ligand_button")
        self.ligand_button.setText("Ligand")
        self.ligand_button.clicked.connect(lambda: self.load_file(self.ligand_button))

        self.ligand_text = QLineEdit(self.input_box)
        self.ligand_text.setObjectName("ligand_text")
        self.ligand_text.setReadOnly(True)
        self.ligand_text.setPlaceholderText('ligand')

        self.ligand_label = QLabel(self.input_box)
        self.ligand_label.hide()

        self.prep_rec_lig_button = QPushButton(self.input_box)
        self.prep_rec_lig_button.setObjectName("prep_rec_lig_button")
        self.prep_rec_lig_button.setText("Prepare\nInput")
        #         # self.prep_rec_lig_button.setEnabled(False)

        self.align_prot = QPushButton(self.input_box)
        self.align_prot.setObjectName("align_prot")
        self.align_prot.setText("Align Proteins")
        self.align_prot.clicked.connect(self.align_proteins)
        self.align_prot.hide()

        self.new_para_btn = QPushButton('+')
        self.new_para_btn.setFixedSize(25, 25)
        self.new_para_btn.clicked.connect(self.addNewParameters)
        self.new_para_btn.hide()
        self.new_para_text = QLineEdit()
        self.new_para_text.setReadOnly(True)
        self.new_para_text.setPlaceholderText('New AD4 Parameter file')
        self.new_para_text.hide()
        self.new_para_layout = QHBoxLayout()
        self.new_para_layout.addWidget(self.new_para_btn)
        self.new_para_layout.addWidget(self.new_para_text)

        self.flags_layout = QHBoxLayout()
        self.flags_layout.addWidget(self.pH_label)
        self.flags_layout.addWidget(self.pH_value)
        self.flags_layout.addWidget(self.simple_docking)
        self.flags_layout.addWidget(self.offtarget_docking)
        self.flags_layout.addWidget(self.rescoring)
        self.flags_layout.addStretch(1)
        self.flags_layout.addLayout(self.new_para_layout)
        self.flags_layout.addStretch(1)
        # self.flags_layout.addWidget(self.align_prot)
        # self.flags_layout.addStretch(1)/

        self.keep_ions_btn = QCheckBox('Keep Metals in Receptors:')
        self.keep_ions_btn.stateChanged.connect(self.enableMetals)

        r = QRegExp("([A-Z][a-z]{0,1}:(\+|\-){0,1}[0-9](\.[0-9]){0,1},)*")
        v = QRegExpValidator(r)

        self.ions_text = QLineEdit()
        self.ions_text.setEnabled(False)
        self.ions_text.setPlaceholderText('Comma separated values, ie metal:charge (Fe:2, Ca:2). Default: Mg, Ca, Fe, '
                                          'Mn with charge = 0.0')
        self.ions_text.setValidator(v)
        self.ions_layout = QHBoxLayout()
        self.ions_layout.addWidget(self.keep_ions_btn)
        self.ions_layout.addWidget(self.ions_text)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)

        self.input_layout = QGridLayout()
        self.input_layout.setSizeConstraint(QLayout.SetFixedSize)
        self.input_layout.addWidget(self.target_button, 0, 0)
        self.input_layout.addWidget(self.target_text, 0, 1)
        self.input_layout.addWidget(self.target_label, 1, 1)

        self.input_layout.addWidget(self.offtarget_button, 2, 0)
        self.input_layout.addWidget(self.offtarget_text, 2, 1)
        self.input_layout.addWidget(self.offtarget_label, 3, 1)
        self.input_layout.addWidget(self.ligand_button, 4, 0)
        self.input_layout.addWidget(self.ligand_text, 4, 1)
        self.input_layout.addWidget(self.ligand_label, 5, 1)

        self.input_btn_layout = QVBoxLayout()
        self.input_btn_layout.addWidget(self.align_prot)
        self.input_btn_layout.addStretch(1)
        self.input_btn_layout.addWidget(self.prep_rec_lig_button)

        self.content_layout = QHBoxLayout()
        self.content_layout.addLayout(self.input_layout)
        self.content_layout.addLayout(self.input_btn_layout)

        self.input_box_layout = QVBoxLayout(self.input_box)
        self.input_box_layout.addLayout(self.flags_layout)
        self.input_box_layout.addLayout(self.ions_layout)
        self.input_box_layout.addWidget(line)
        self.input_box_layout.addLayout(self.content_layout)

        # **Grid_box
        self.grid_box = QGroupBox(self.sc_area_widget)
        self.grid_box.setObjectName("grid_box")
        self.grid_box.setTitle("Search Space")
        self.grid_box.setToolTip(self.AMDock.grid_tt)

        self.target_column_label = QLabel('Target', self.grid_box)
        self.target_column_label.setAlignment(Qt.AlignCenter)

        self.target_column_group_btnA = QButtonGroup(self.grid_box)
        self.target_column_group_btnA.buttonPressed.connect(self.grid_sel_protection)

        self.btnA_auto = QRadioButton(self.grid_box)
        self.btnA_auto.setObjectName('btnA_auto')
        self.btnA_auto.setChecked(True)
        self.target_column_group_btnA.addButton(self.btnA_auto, 1)
        self.btnA_auto.toggled.connect(lambda: self.grid_prot(self.btnA_auto))

        self.btnA_res = QRadioButton(self.grid_box)
        self.target_column_group_btnA.addButton(self.btnA_res, 2)
        self.btnA_res.setObjectName('btnA_res')
        self.btnA_res.toggled.connect(lambda: self.grid_prot(self.btnA_res))

        self.btnA_lig = QRadioButton(self.grid_box)
        self.btnA_lig.setObjectName('btnA_lig')
        self.target_column_group_btnA.addButton(self.btnA_lig, 3)
        self.btnA_lig.toggled.connect(lambda: self.grid_prot(self.btnA_lig))

        self.btnA_user = QRadioButton(self.grid_box)
        self.target_column_group_btnA.addButton(self.btnA_user, 4)
        self.btnA_user.setObjectName('btnA_user')
        self.btnA_user.toggled.connect(lambda: self.grid_prot(self.btnA_user))

        self.offtarget_column_label = QLabel('Off-Target', self.grid_box)
        self.offtarget_column_label.hide()
        self.offtarget_column_label.setAlignment(Qt.AlignCenter)

        self.offtarget_column_group_btnB = QButtonGroup(self.grid_box)
        self.offtarget_column_group_btnB.buttonPressed.connect(self.grid_sel_protection)

        self.btnB_auto = QRadioButton(self.grid_box)
        self.btnB_auto.setChecked(True)
        self.offtarget_column_group_btnB.addButton(self.btnB_auto, 1)
        self.btnB_auto.hide()
        self.btnB_auto.toggled.connect(lambda: self.grid_prot(self.btnB_auto))

        self.btnB_res = QRadioButton(self.grid_box)
        self.btnB_res.toggled.connect(lambda: self.grid_prot(self.btnB_res))

        self.offtarget_column_group_btnB.addButton(self.btnB_res, 2)
        self.btnB_res.hide()

        self.btnB_lig = QRadioButton(self.grid_box)
        self.offtarget_column_group_btnB.addButton(self.btnB_lig, 3)
        self.btnB_lig.hide()
        self.btnB_lig.toggled.connect(lambda: self.grid_prot(self.btnB_lig))

        self.btnB_user = QRadioButton(self.grid_box)
        self.offtarget_column_group_btnB.addButton(self.btnB_user, 4)
        self.btnB_user.hide()
        self.btnB_user.toggled.connect(lambda: self.grid_prot(self.btnB_user))

        self.grid_auto_cr = QLabel(self.grid_box)
        self.grid_auto_cr.setText("Automatic")

        self.grid_predef_cr = QLabel(self.grid_box)
        self.grid_predef_cr.setText("Center on Residue(s)")

        regex = QRegExp("([A-Z-a-z]:[A-Z-a-z]{3}:[0-9]{1,5}; )*")
        validator = QRegExpValidator(regex)

        self.grid_predef_text = QLineEdit(self.grid_box)
        self.grid_predef_text.setObjectName("grid_predef_text")
        self.grid_predef_text.setPlaceholderText('CHN:RES:NUM,...,CHN:RES:NUM (chain:residue:number of residue)')
        self.grid_predef_text.hide()
        self.grid_predef_text.textChanged.connect(lambda: self.check_res(self.grid_predef_text))
        self.grid_predef_text.setValidator(validator)

        self.grid_predef_textB = QLineEdit(self.grid_box)
        self.grid_predef_textB.setObjectName("grid_predef_textB")
        self.grid_predef_textB.setPlaceholderText('CHN:RES:NUM,...,CHN:RES:NUM (chain:residue:number of residue)')
        self.grid_predef_textB.hide()
        self.grid_predef_textB.textChanged.connect(lambda: self.check_res(self.grid_predef_textB))
        self.grid_predef_textB.setValidator(validator)

        self.grid_by_lig_cr = QLabel(self.grid_box)
        self.grid_by_lig_cr.setText("Center on Hetero")

        self.lig_list = QComboBox(self.grid_box)
        self.lig_list.setObjectName("lig_list")
        self.lig_list.hide()
        self.lig_list.currentIndexChanged.connect(lambda: self.lig_select(self.lig_list))

        self.lig_listB = QComboBox(self.grid_box)
        self.lig_listB.setObjectName("lig_listB")
        self.lig_listB.hide()
        self.lig_listB.currentIndexChanged.connect(lambda: self.lig_select(self.lig_listB))

        self.grid_user_cr = QLabel(self.grid_box)
        self.grid_user_cr.setText('Box')

        self.coor_box = QGroupBox(self.grid_box)
        self.coor_box.setTitle("Center")
        self.coor_box.setAlignment(Qt.AlignCenter)
        self.coor_box.hide()

        self.coor_x_label = QLabel(self.coor_box)
        self.coor_x_label.setText('X:')
        self.coor_x = QDoubleSpinBox(self.coor_box)
        self.coor_x.setDecimals(1)
        self.coor_x.setRange(-999, 999)
        self.coor_x.setSingleStep(0.1)
        self.coor_x.setAccelerated(True)
        self.coor_x.setObjectName('coor_x')

        self.coor_y_label = QLabel(self.coor_box)
        self.coor_y_label.setText('Y:')
        self.coor_y = QDoubleSpinBox(self.coor_box)
        self.coor_y.setDecimals(1)
        self.coor_y.setRange(-999, 999)
        self.coor_y.setSingleStep(0.1)
        self.coor_y.setAccelerated(True)
        self.coor_y.setObjectName('coor_y')

        self.coor_z_label = QLabel(self.coor_box)
        self.coor_z_label.setText('Z:')
        self.coor_z = QDoubleSpinBox(self.coor_box)
        self.coor_z.setDecimals(1)
        self.coor_z.setRange(-999, 999)
        self.coor_z.setSingleStep(0.1)
        self.coor_z.setAccelerated(True)
        self.coor_z.setObjectName('coor_z')

        self.size_box = QGroupBox(self.grid_box)
        self.size_box.setTitle("Size")
        self.size_box.setAlignment(Qt.AlignCenter)
        self.size_box.hide()

        self.size_x_label = QLabel(self.size_box)
        self.size_x_label.setText('X:')
        self.size_x = QSpinBox(self.coor_box)
        self.size_x.setAccelerated(True)
        self.size_x.setObjectName('size_x')

        self.size_y_label = QLabel(self.size_box)
        self.size_y_label.setText('Y:')
        self.size_y = QSpinBox(self.coor_box)
        self.size_y.setAccelerated(True)
        self.size_y.setObjectName('size_y')

        self.size_z_label = QLabel(self.size_box)
        self.size_z_label.setText('Z:')
        self.size_z = QSpinBox(self.coor_box)
        self.size_z.setAccelerated(True)
        self.size_z.setObjectName('size_z')

        self.coor_boxB = QGroupBox(self.grid_box)
        self.coor_boxB.setTitle("Center")
        self.coor_boxB.setAlignment(Qt.AlignCenter)
        self.coor_boxB.hide()

        self.coor_x_labelB = QLabel(self.coor_boxB)
        self.coor_x_labelB.setText('X:')
        self.coor_xB = QDoubleSpinBox(self.coor_boxB)
        self.coor_xB.setDecimals(1)
        self.coor_xB.setRange(-999, 999)
        self.coor_xB.setSingleStep(0.1)
        self.coor_xB.setAccelerated(True)
        self.coor_xB.setObjectName('coor_xB')

        self.coor_y_labelB = QLabel(self.coor_boxB)
        self.coor_y_labelB.setText('Y:')
        self.coor_yB = QDoubleSpinBox(self.coor_boxB)
        self.coor_yB.setDecimals(1)
        self.coor_yB.setRange(-999, 999)
        self.coor_yB.setSingleStep(0.1)
        self.coor_yB.setAccelerated(True)
        self.coor_yB.setObjectName('coor_yB')

        self.coor_z_labelB = QLabel(self.coor_boxB)
        self.coor_z_labelB.setText('Z:')
        self.coor_zB = QDoubleSpinBox(self.coor_boxB)
        self.coor_zB.setDecimals(1)
        self.coor_zB.setRange(-999, 999)
        self.coor_zB.setSingleStep(0.1)
        self.coor_zB.setAccelerated(True)
        self.coor_zB.setObjectName('coor_zB')

        self.size_boxB = QGroupBox(self.grid_box)
        self.size_boxB.setTitle("Size")
        self.size_boxB.setAlignment(Qt.AlignCenter)
        self.size_boxB.hide()

        self.size_x_labelB = QLabel(self.size_boxB)
        self.size_x_labelB.setText('X:')
        self.size_xB = QSpinBox(self.size_boxB)
        self.size_xB.setAccelerated(True)
        self.size_xB.setObjectName('size_xB')

        self.size_y_labelB = QLabel(self.size_boxB)
        self.size_y_labelB.setText('Y:')
        self.size_yB = QSpinBox(self.size_boxB)
        self.size_yB.setAccelerated(True)
        self.size_yB.setObjectName('size_yB')

        self.size_z_labelB = QLabel(self.size_boxB)
        self.size_z_labelB.setText('Z:')
        self.size_zB = QSpinBox(self.size_boxB)
        self.size_zB.setAccelerated(True)
        self.size_zB.setObjectName('size_zB')

        self.spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.center_layout = QGridLayout(self.coor_box)
        self.center_layout.addWidget(self.coor_x_label, 0, 0, Qt.AlignCenter)
        self.center_layout.addWidget(self.coor_x, 1, 0, Qt.AlignCenter)
        self.center_layout.addWidget(self.coor_y_label, 0, 1, Qt.AlignCenter)
        self.center_layout.addWidget(self.coor_y, 1, 1, Qt.AlignCenter)
        self.center_layout.addWidget(self.coor_z_label, 0, 2, Qt.AlignCenter)
        self.center_layout.addWidget(self.coor_z, 1, 2, Qt.AlignCenter)

        self.center_layoutB = QGridLayout(self.coor_boxB)
        self.center_layoutB.addWidget(self.coor_x_labelB, 0, 0, Qt.AlignCenter)
        self.center_layoutB.addWidget(self.coor_xB, 1, 0, Qt.AlignCenter)
        self.center_layoutB.addWidget(self.coor_y_labelB, 0, 1, Qt.AlignCenter)
        self.center_layoutB.addWidget(self.coor_yB, 1, 1, Qt.AlignCenter)
        self.center_layoutB.addWidget(self.coor_z_labelB, 0, 2, Qt.AlignCenter)
        self.center_layoutB.addWidget(self.coor_zB, 1, 2, Qt.AlignCenter)

        self.size_layout = QGridLayout(self.size_box)
        self.size_layout.addWidget(self.size_x_label, 0, 0, Qt.AlignCenter)
        self.size_layout.addWidget(self.size_x, 1, 0, Qt.AlignCenter)
        self.size_layout.addWidget(self.size_y_label, 0, 1, Qt.AlignCenter)
        self.size_layout.addWidget(self.size_y, 1, 1, Qt.AlignCenter)
        self.size_layout.addWidget(self.size_z_label, 0, 2, Qt.AlignCenter)
        self.size_layout.addWidget(self.size_z, 1, 2, Qt.AlignCenter)

        self.size_layoutB = QGridLayout(self.size_boxB)
        self.size_layoutB.addWidget(self.size_x_labelB, 0, 0, Qt.AlignCenter)
        self.size_layoutB.addWidget(self.size_xB, 1, 0, Qt.AlignCenter)
        self.size_layoutB.addWidget(self.size_y_labelB, 0, 1, Qt.AlignCenter)
        self.size_layoutB.addWidget(self.size_yB, 1, 1, Qt.AlignCenter)
        self.size_layoutB.addWidget(self.size_z_labelB, 0, 2, Qt.AlignCenter)
        self.size_layoutB.addWidget(self.size_zB, 1, 2, Qt.AlignCenter)

        self.bind_site_button = QPushButton(self.grid_box)
        self.bind_site_button.setObjectName("bind_site_button")
        self.bind_site_button.setText("Define\nSearch Space")
        self.bind_site_button.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))

        self.grid_pymol_button = QPushButton(self.grid_box)
        self.grid_pymol_button.setObjectName("grid_pymol_button")
        self.grid_pymol_button.setText('Show in PyMol')
        self.grid_pymol_button.clicked.connect(lambda: self.grid_actions(self.grid_pymol_button))

        self.checker_icon = QLabel(self.grid_box)
        self.checker_icon.setPixmap(QPixmap(self.AMDock.error_checker))
        self.checker_icon.hide()

        self.checker_icon_ok = QLabel(self.grid_box)
        self.checker_icon_ok.setPixmap(QPixmap(self.AMDock.error_checker_ok))
        self.checker_icon_ok.hide()

        self.run_button = QPushButton(self)
        self.run_button.setObjectName("run_button")
        self.run_button.setText("Run")
        self.run_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.stop_button = QPushButton(self)
        self.stop_button.setObjectName("stop_button")
        self.stop_button.setText("Stop")
        self.stop_button.clicked.connect(self.stop_function)

        self.process_state_label = QLabel('STATE:')
        self.process_state_label.setStyleSheet("QLabel {font-weight: bold;}")

        self.process_state = QLabel('NOT RUNNING')
        self.process_state.setStyleSheet("QLabel {font-weight: bold; color: green;}")

        self.section_name = QLabel('SECTION:')
        self.section_name.setStyleSheet("QLabel {font-weight: bold;}")

        self.section_state = QLabel('PROJECT')
        self.section_state.setStyleSheet("QLabel {font-weight: bold; color: green;}")

        self.reset_button = QPushButton(self)
        self.reset_button.setObjectName("reset_button")
        self.reset_button.setText("  Reset")
        self.reset_button.setIcon(QIcon(self.AMDock.reset_icon))
        self.reset_button.clicked.connect(self.reset_function)

        self.progress_project_label = QLabel('Project Progress')

        self.progressBar_global = QRadialBar(self)
        self.progressBar_global.setValue(0)
        self.progressBar_global.setObjectName("progressBar_global")
        # self.progressBar_global.setMinimumSize(120, 120)
        self.progressBar_global.setFixedSize(120, 120)

        self.progress_section_label = QLabel('Section Progress')

        self.progressBar_section = QRadialBar(self)
        # self.progressBar_section.setAutoFillBackground(True)
        self.progressBar_section.setValue(0)
        self.progressBar_section.setObjectName("progressBar_section")
        self.progressBar_section.setMinimumSize(120, 120)

        self.log_button = QPushButton('Log:')
        self.log_button.clicked.connect(self.log_toggle)
        self.program_label = QLabel('')

        self.checker_icon = QLabel(self.grid_box)
        self.checker_icon.setPixmap(QPixmap(self.AMDock.error_checker))
        self.checker_icon.hide()

        self.checker_iconB = QLabel(self.grid_box)
        self.checker_iconB.setPixmap(QPixmap(self.AMDock.error_checker))
        self.checker_iconB.hide()

        self.checker_icon_ok = QLabel(self.grid_box)
        self.checker_icon_ok.setPixmap(QPixmap(self.AMDock.error_checker_ok))
        self.checker_icon_ok.hide()

        self.checker_icon_okB = QLabel(self.grid_box)
        self.checker_icon_okB.setPixmap(QPixmap(self.AMDock.error_checker_ok))
        self.checker_icon_okB.hide()

        self.res_text = QHBoxLayout()
        self.res_text.addWidget(self.grid_predef_text, 1)
        self.res_text.addWidget(self.checker_icon_ok)
        self.res_text.addWidget(self.checker_icon)

        self.res_textB = QHBoxLayout()
        self.res_textB.addWidget(self.grid_predef_textB, 1)
        self.res_textB.addWidget(self.checker_icon_okB, 0)
        self.res_textB.addWidget(self.checker_iconB, 0)

        self.coor_box_layout = QHBoxLayout()
        self.coor_box_layout.addWidget(self.coor_box)
        self.coor_box_layout.addWidget(self.size_box)

        self.coor_boxB_layout = QHBoxLayout()
        self.coor_boxB_layout.addWidget(self.coor_boxB)
        self.coor_boxB_layout.addWidget(self.size_boxB)

        self.autoligand_target = QTableWidget()
        self.autoligand_target.setObjectName('autoligand_target')
        self.autoligand_target.setColumnCount(2)
        self.autoligand_target.setHorizontalHeaderLabels(["Total Volume (A**3)", "EPV (Kcal/mol A**3)"])
        self.autoligand_target.setMinimumHeight(150)
        self.autoligand_target.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.autoligand_target.hide()
        self.autoligand_target.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.autoligand_target.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.autoligand_target.setSelectionMode(QAbstractItemView.SingleSelection)
        self.autoligand_target.itemSelectionChanged.connect(lambda: self.fill_selection(self.autoligand_target))

        self.autolig_layout = QHBoxLayout()
        self.autolig_layout.addWidget(self.autoligand_target, 1)

        self.autoligand_offtarget = QTableWidget()
        self.autoligand_offtarget.setObjectName('autoligand_offtarget')
        self.autoligand_offtarget.setColumnCount(2)
        self.autoligand_offtarget.setHorizontalHeaderLabels(["Total Volume (A**3)", "EPV (Kcal/mol A**3)"])
        self.autoligand_offtarget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.autoligand_offtarget.hide()
        self.autoligand_offtarget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.autoligand_offtarget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.autoligand_offtarget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.autoligand_offtarget.itemSelectionChanged.connect(lambda: self.fill_selection(self.autoligand_offtarget))

        self.autolig_layoutB = QHBoxLayout()
        self.autolig_layoutB.addWidget(self.autoligand_offtarget, 1)

        self.all_options = QGridLayout()
        self.all_options.setSizeConstraint(QLayout.SetFixedSize)

        self.all_options.setColumnStretch(1, 1)  # make column 1 and 2 regular width
        self.all_options.addWidget(self.target_column_label, 0, 1, 1, 1, Qt.AlignCenter)
        self.all_options.addWidget(self.offtarget_column_label, 0, 2, 1, 1, Qt.AlignCenter)

        self.all_options.addWidget(self.grid_auto_cr, 1, 0)
        self.all_options.addWidget(self.btnA_auto, 1, 1, 1, 1, Qt.AlignCenter)
        self.all_options.addWidget(self.btnB_auto, 1, 2, 1, 1, Qt.AlignCenter)
        self.all_options.addLayout(self.autolig_layout, 2, 1, 1, 1, Qt.AlignCenter)
        self.all_options.addLayout(self.autolig_layoutB, 2, 2, 1, 1, Qt.AlignCenter)

        self.all_options.addWidget(self.grid_predef_cr, 3, 0)
        self.all_options.addWidget(self.btnA_res, 3, 1, 1, 1, Qt.AlignCenter)
        self.all_options.addLayout(self.res_text, 4, 1, 1, 1, Qt.AlignCenter)
        self.all_options.addWidget(self.btnB_res, 3, 2, 1, 1, Qt.AlignCenter)
        self.all_options.addLayout(self.res_textB, 4, 2, 1, 1, Qt.AlignCenter)

        self.all_options.addWidget(self.grid_by_lig_cr, 5, 0)
        self.all_options.addWidget(self.btnA_lig, 5, 1, 1, 1, Qt.AlignCenter)
        self.all_options.addWidget(self.lig_list, 6, 1, 1, 1, Qt.AlignCenter)
        self.all_options.addWidget(self.btnB_lig, 5, 2, 1, 1, Qt.AlignCenter)
        self.all_options.addWidget(self.lig_listB, 6, 2, 1, 1, Qt.AlignCenter)

        self.all_options.addWidget(self.grid_user_cr, 7, 0)
        self.all_options.addWidget(self.btnA_user, 7, 1, 1, 1, Qt.AlignCenter)
        self.all_options.addLayout(self.coor_box_layout, 8, 1, 1, 1, Qt.AlignCenter)
        self.all_options.addWidget(self.btnB_user, 7, 2, 1, 1, Qt.AlignCenter)
        self.all_options.addLayout(self.coor_boxB_layout, 8, 2, 1, 1, Qt.AlignCenter)

        self.pymol_button_layout = QHBoxLayout()
        self.pymol_button_layout.addStretch(50)
        self.pymol_button_layout.addWidget(self.grid_pymol_button)
        self.pymol_button_layout.addStretch(48)

        self.binding_layout = QVBoxLayout()
        self.binding_layout.addStretch(1)
        self.binding_layout.addWidget(self.bind_site_button)
        self.binding_layout.addStretch(1)

        self.grid_subcontent = QHBoxLayout()
        self.grid_subcontent.addLayout(self.all_options, 1)
        self.grid_subcontent.addLayout(self.binding_layout)

        self.grid_content = QVBoxLayout(self.grid_box)
        self.grid_content.addLayout(self.grid_subcontent, 1)
        self.grid_content.addLayout(self.pymol_button_layout)

        self.W = PROCESS()
        # signals for programs
        self.W.stoped.connect(self.process_stoped)
        self.W.prog_finished.connect(self.for_finished)
        # self.W.process.error.connect(self.output_error)
        self.W.worker.signals.finished.connect(self.for_finished)
        self.W.state.connect(self.check_state)
        # self.W.worker.signals.result.connect(self.output_function)
        self.W.queue_finished.connect(self.check_section)
        self.W.process.readyReadStandardOutput.connect(self.readStdOutput)

        self.offtarget_docking.pressed.connect(lambda: self.simulation_form(self.offtarget_docking))
        self.simple_docking.pressed.connect(lambda: self.simulation_form(self.simple_docking))
        self.rescoring.pressed.connect(lambda: self.simulation_form(self.rescoring))
        self.prep_rec_lig_button.clicked.connect(self.prepare_receptor)
        self.bind_site_button.clicked.connect(self.binding_site)
        self.run_button.clicked.connect(self.start_docking_prog)

        self.reset_button_layout = QHBoxLayout()
        self.reset_button_layout.addStretch(1)
        self.reset_button_layout.addWidget(self.reset_button)
        self.reset_button_layout.addStretch(1)

        self.progressbar_layout = QGridLayout()
        self.progressbar_layout.addWidget(self.log_button, 0, 0)
        self.progressbar_layout.addWidget(self.program_label, 0, 1, 1, -1)

        self.progressbar_layout.addWidget(self.progressBar_global, 1, 0, 3, 3, Qt.AlignCenter)
        self.progressbar_layout.addWidget(self.progress_project_label, 4, 0, 3, 3, Qt.AlignCenter)

        self.progressbar_layout.addWidget(self.section_name, 1, 3, 1, 1, Qt.AlignCenter)
        self.progressbar_layout.addWidget(self.section_state, 2, 3, 1, 1, Qt.AlignCenter)
        self.progressbar_layout.addWidget(self.reset_button, 3, 3, 1, 1)
        self.progressbar_layout.addItem(self.spacer, 1, 4, 3, 1)

        self.progressbar_layout.addWidget(self.progressBar_section, 1, 5, 3, 3, Qt.AlignCenter)
        self.progressbar_layout.addWidget(self.progress_section_label, 4, 5, 3, 3, Qt.AlignCenter)

        self.progressbar_layout.addWidget(self.process_state_label, 1, 8, 1, 1, Qt.AlignCenter)
        self.progressbar_layout.addWidget(self.process_state, 2, 8, 1, 1, Qt.AlignCenter)

        self.progressbar_layout.addWidget(self.stop_button, 3, 8, 1, 1)
        self.progressbar_layout.addItem(self.spacer, 1, 9, 3, 2)

        self.run_layout = QVBoxLayout()
        self.run_layout.addStretch(1)
        self.run_layout.addWidget(self.run_button, 2)
        self.run_layout.addStretch(1)

        self.progress_layout = QHBoxLayout()
        self.progress_layout.addLayout(self.progressbar_layout, 1)
        self.progress_layout.addLayout(self.run_layout)

        self.sc_area_widget_layout = QVBoxLayout(self.sc_area_widget)
        self.sc_area_widget_layout.addWidget(self.project_box)
        self.sc_area_widget_layout.addWidget(self.input_box)
        self.sc_area_widget_layout.addWidget(self.grid_box)
        self.sc_area_widget_layout.addStretch(1)

        self.sc_area_layout = QHBoxLayout(self.sc_area)
        self.sc_area_layout.addWidget(self.sc_area_widget)
        self.sc_area.setWidgetResizable(True)
        self.sc_area.setWidget(self.sc_area_widget)

        self.body_layout = QVBoxLayout(self)
        self.body_layout.addWidget(self.sc_area, 1)
        self.body_layout.addLayout(self.progress_layout)

    def enableMetals(self, state):
        if state:
            self.ions_text.setEnabled(True)
        else:
            self.ions_text.setEnabled(False)
            self.ions_text.clear()

    def load_file(self, _file):  # ok
        if _file.objectName() == 'create_project':
            # check if exist any process in background
            if self.AMDock.state == 2:
                QMessageBox.critical(self.AMDock, 'Error', 'Other processes are running in the background. '
                                                           'Please wait for these to end.',
                                     QMessageBox.Ok)
                return
            elif self.AMDock.section in [1, 2, 3]:
                msg = QMessageBox.warning(self.AMDock, 'Warning', 'This step was successfully completed '
                                                                  'previously. Do you want to repeat it?\n Keep '
                                                                  'in mind that this will eliminate all the '
                                                                  'information contained in this project !!!',
                                          QMessageBox.Yes | QMessageBox.No)
                if msg == QMessageBox.No:
                    return
                elif msg == QMessageBox.Yes:
                    self.reset_sections(0)

            if not self.AMDock.project.location:
                define_wdir_loc(self)
                return

            if self.AMDock.project.WDIR:
                options = wdir2_warning(self)
                if options == QMessageBox.Yes:
                    self.AMDock.output2file.conclude()
                    os.chdir(self.AMDock.project.location)
                    try:
                        shutil.rmtree(self.AMDock.project.WDIR)
                    except:
                        QMessageBox.critical(self.AMDock, 'Error',
                                             'The previous project directory could not be removed. Please '
                                             'remove it manually.', QMessageBox.Ok)
                    if not self.AMDock.loader.create_project_function():
                        self.AMDock.project.WDIR = None
                        self.project_text.clear()
                        self.wdir_text.clear()
                        self.AMDock.project.location = None
                        self.proj_loc_label.hide()
                    else:
                        self.proj_loc_label.setText('Project: %s' % self.AMDock.project.WDIR)
                        self.proj_loc_label.show()
            else:
                if not self.AMDock.loader.create_project_function():
                    self.AMDock.project.WDIR = None
                    self.project_text.clear()
                    self.wdir_text.clear()
                    self.AMDock.project.location = None
                    self.proj_loc_label.hide()
                    return
                else:
                    self.proj_loc_label.setText('Project: %s' % self.AMDock.project.WDIR)
                    self.proj_loc_label.show()
            self.AMDock.section = 0
            self.progressBar_global.setValue(25)
            self.highlight()
            self.program_label.setText('Create project... Done.')
            self.AMDock.log_widget.textedit.append(Ft('WDIR: %s' % self.AMDock.project.WDIR).definitions())

        if _file.objectName() == "wdir_button":
            loc_file = self.AMDock.loader.project_location()
            self.AMDock.project.get_loc(loc_file)
            if self.AMDock.project.location:
                self.wdir_text.setText("%s" % self.AMDock.project.location)

        if _file.objectName() == "target_button":
            if self.AMDock.state == 2:
                QMessageBox.critical(self.AMDock, 'Error', 'Other processes are running in the background. '
                                                           'Please wait for these to end.',
                                     QMessageBox.Ok)
                return
            elif self.AMDock.section == -1:
                QMessageBox.critical(self.AMDock, 'Error', 'It seems that not all previous steps have been '
                                                           'completed. Please do all the steps sequentially.',
                                     QMessageBox.Ok)
                return
            elif self.AMDock.section in [1, 2, 3]:
                msg = QMessageBox.warning(self.AMDock, 'Warning',
                                          'This step was successfully completed previously.'
                                          ' Do you want to repeat it?',
                                          QMessageBox.Yes | QMessageBox.No)
                if msg == QMessageBox.No:
                    return
                elif msg == QMessageBox.Yes:
                    self.reset_sections(1)

            if self.AMDock.target.input is None:
                self.AMDock.loader.load_protein()
            else:
                prot_opt = prot_warning(self)
                if prot_opt == QMessageBox.Yes:
                    os.remove(self.AMDock.target.input)
                    self.AMDock.target = BASE()
                    self.target_label.clear()
                    self.target_text.clear()
                    self.target_label.hide()
                    self.AMDock.loader.load_protein()
            if self.AMDock.target.name:
                self.target_label.show()

        if _file.objectName() == "offtarget_button":
            if self.AMDock.state == 2:
                msg = QMessageBox.critical(self.AMDock, 'Error', 'Other processes are running in the background. '
                                                                 'Please wait for these to end.',
                                           QMessageBox.Ok)
                return
            elif self.AMDock.section == -1:
                msg = QMessageBox.critical(self.AMDock, 'Error', 'It seems that not all previous steps have been '
                                                                 'completed. Please do all the steps sequentially.',
                                           QMessageBox.Ok)
                return
            if self.AMDock.offtarget.input is None:
                self.AMDock.loader.load_proteinB()
            else:
                prot_opt = prot_warning(self)
                if prot_opt == QMessageBox.Yes:
                    os.remove(self.AMDock.offtarget.input)
                    self.AMDock.offtarget = BASE()
                    self.offtarget_label.clear()
                    self.offtarget_text.clear()
                    self.offtarget_label.hide()
                    self.AMDock.loader.load_proteinB()
            if self.AMDock.offtarget.name:
                self.offtarget_label.show()

        if _file.objectName() == "ligand_button":
            if self.AMDock.state == 2:
                msg = QMessageBox.critical(self.AMDock, 'Error', 'Other processes are running in the background. '
                                                                 'Please wait for these to end.',
                                           QMessageBox.Ok)
                return
            elif self.AMDock.section == -1:
                msg = QMessageBox.critical(self.AMDock, 'Error', 'It seems that not all previous steps have been '
                                                                 'completed. Please do all the steps sequentially.',
                                           QMessageBox.Ok)
                return
            if self.AMDock.ligand.input is None:
                self.AMDock.loader.load_ligand()
            else:
                self.lig_opt = lig_warning(self)
                if self.lig_opt == QMessageBox.Yes:
                    os.remove(self.AMDock.ligand.input)
                    self.AMDock.ligand = BASE()
                    self.ligand_text.clear()
                    self.ligand_label.clear()
                    self.ligand_label.hide()
                    self.AMDock.loader.load_ligand()
            if self.AMDock.ligand.name:
                self.ligand_label.show()

    def simulation_form(self, btn, reset=False):
        if btn.isChecked():
            return
        else:
            if not reset:
                if self.AMDock.target.input or self.AMDock.offtarget.input or self.AMDock.ligand.input:
                    msg = QMessageBox.warning(self, 'Warning', "All data in this section and in Search Space will "
                                                               "be lost. Do you want to continue? ",
                                              QMessageBox.Yes | QMessageBox.No)
                    if msg == QMessageBox.No:
                        return
        btn.setChecked(True)
        target = offtarget = ligand = 0
        if self.AMDock.target.input:
            try:
                os.remove(self.AMDock.target.input)
            except:
                target = 1
        if self.AMDock.offtarget.input:
            try:
                os.remove(self.AMDock.offtarget.input)
            except:
                offtarget = 1
        if self.AMDock.ligand.input:
            try:
                os.remove(self.AMDock.ligand.input)
            except:
                ligand = 1
        if target or offtarget or ligand:
            msg = QMessageBox.warning(self, 'Warning', "Some files could not be eliminated, this could generate "
                                                       "future problems. Please check that you have  writing "
                                                       "rights in the project directory. You can continue the "
                                                       "process without worrying.", QMessageBox.Ok)
        self.AMDock.target = BASE()
        self.AMDock.offtarget = BASE()
        self.AMDock.ligand = BASE()
        self.target_label.clear()
        self.target_label.hide()
        self.offtarget_label.clear()
        self.offtarget_label.hide()
        self.ligand_label.clear()
        self.ligand_label.hide()

        self.target_text.clear()
        self.offtarget_text.clear()
        self.ligand_text.clear()

        self.offtarget_button.hide()
        self.offtarget_text.hide()
        self.offtarget_column_label.hide()
        self.btnB_auto.hide()
        self.btnB_res.hide()
        self.btnB_lig.hide()
        self.btnB_user.hide()
        self.btnA_auto.setChecked(True)
        self.btnB_auto.setChecked(True)
        self.lig_list.clear()
        self.lig_listB.clear()

        if btn.objectName() == 'offtarget_docking':
            self.all_options.setColumnStretch(1, 1)
            self.all_options.setColumnStretch(2, 1)
            self.AMDock.scoring = False
            self.AMDock.project.mode = 1
            ## Input box
            self.offtarget_button.show()
            self.offtarget_text.show()
            ### Grid definition box
            self.offtarget_column_label.show()
            self.btnB_auto.show()
            self.btnB_res.show()
            self.btnB_lig.show()
            self.btnB_user.show()
            self.grid_box.setEnabled(True)
            self.align_prot.show()

        elif btn.text() == 'Scoring':
            self.all_options.setColumnStretch(2, 0)
            self.AMDock.scoring = True
            self.AMDock.project.mode = 2
            self.grid_box.setEnabled(False)
            self.align_prot.hide()
        else:
            self.all_options.setColumnStretch(2, 0)
            self.AMDock.scoring = False
            self.AMDock.project.mode = 0
            self.grid_box.setEnabled(True)
            self.align_prot.hide()

    def align_proteins(self):
        if self.AMDock.state == 2:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'Other processes are running in the background. '
                                                             'Please wait for these to end.',
                                       QMessageBox.Ok)
            return
        elif self.AMDock.section == -1:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'It seems that not all previous steps have been '
                                                             'completed. Please do all the steps sequentially.',
                                       QMessageBox.Ok)
            return
        elif self.AMDock.state in [1, 2, 3]:
            msg = QMessageBox.warning(self.AMDock, 'Warning', 'This step was successfully completed previously.'
                                                              ' Do you want to repeat it?',
                                      QMessageBox.Yes | QMessageBox.No)
            if msg == QMessageBox.No:
                return
        os.chdir(self.AMDock.project.input)
        # check if target, (offtarget) and ligand are defined
        if not self.AMDock.target.input or not self.AMDock.ligand.input or not self.AMDock.offtarget.input:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'Target, Ligand and Off-Target (if Off-target '
                                                             'Docking is selected) most be defined',
                                       QMessageBox.Ok)
            return
        # Align proteins
        if self.AMDock.target.ext == 'pdbqt' or self.AMDock.offtarget.ext == 'pdbqt':
            msg = QMessageBox.warning(self.AMDock, 'Warning', 'Some of the proteins are PDBQT format, '
                                                              'which means that to align them, it will be '
                                                              'converted to PDB format and then again to PDBQT. '
                                                              'This can introduce unexpected errors. Do you wish'
                                                              ' to continue?',
                                      QMessageBox.Yes, QMessageBox.No)
            if msg == QMessageBox.Yes:
                if self.AMDock.target.ext == 'pdbqt':
                    conv = Convert(self.AMDock.target.input)
                    if conv.get_path():
                        self.AMDock.target.input = conv.get_path()
                        self.AMDock.target.get_data(self.AMDock.target.input)
                if self.AMDock.offtarget.ext == 'pdbqt':
                    conv = Convert(self.AMDock.offtarget.input)
                    if conv.get_path():
                        self.AMDock.offtarget.input = conv.get_path()
                        self.AMDock.offtarget.get_data(self.AMDock.offtarget.input)
            else:
                return

        align = {'Align': [self.AMDock.this_python, [self.AMDock.pymol, '-c', self.AMDock.aln_pymol, '--', '-t',
                                                     self.AMDock.target.input, '-o', self.AMDock.offtarget.input]]}

        queue = Queue()
        queue.name = 5
        queue.put(align)
        self.W.set_queue(queue)
        self.W.start_process()

    def addNewParameters(self):
        if self.AMDock.section == -1:
            QMessageBox.critical(self.AMDock, 'Error', 'It seems that not all previous steps have been '
                                                       'completed. Please do all the steps sequentially.',
                                 QMessageBox.Ok)
            return
        if self.AMDock.para_file:
            msg = QMessageBox.warning(self.AMDock, 'Warning', 'A new parameter file has already been defined. '
                                                              'Do you want to delete it?',
                                      QMessageBox.Yes | QMessageBox.No)
            if msg == QMessageBox.No:
                return

            self.new_para_text.clear()
            self.new_para_btn.setText('+')
            self.AMDock.para_file = None
            self.AMDock.log_widget.textedit.append(
                Ft('PARAMETERS_FILE: %s' % 'Default').definitions())
            return

        if self.AMDock.loader.load_parameters():
            self.new_para_btn.setText('-')
            self.new_para_text.setText(str(self.AMDock.para_file))
            self.AMDock.log_widget.textedit.append(Ft('PARAMETERS_FILE: %s' % self.AMDock.para_file).definitions())

    def prepare_receptor(self):

        if self.AMDock.state == 2:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'Other processes are running in the background. '
                                                             'Please wait for these to end.',
                                       QMessageBox.Ok)
            return
        elif self.AMDock.section == -1:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'It seems that not all previous steps have been '
                                                             'completed. Please do all the steps sequentially.',
                                       QMessageBox.Ok)
            return
        elif self.AMDock.section in [1, 2, 3]:
            msg = QMessageBox.warning(self.AMDock, 'Warning', 'This step was successfully completed previously.'
                                                              ' Do you want to repeat it?',
                                      QMessageBox.Yes | QMessageBox.No)
            if msg == QMessageBox.No:
                return
        os.chdir(self.AMDock.project.input)
        # check if target, (offtarget) and ligand are defined
        if not self.AMDock.target.input or not self.AMDock.ligand.input:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'Target, Ligand and Off-Target (if Off-target '
                                                             'Docking is selected) most be defined',
                                       QMessageBox.Ok)
            return
        elif self.AMDock.project.mode == 1:
            if not self.AMDock.offtarget.input:
                msg = QMessageBox.critical(self.AMDock, 'Error', 'Target, Ligand and Off-Target (if Off-target '
                                                                 'Docking is selected) most be defined',
                                           QMessageBox.Ok)
                return
        self.list_process = []

        self.target_info = PDBINFO(self.AMDock.target.input)
        self.AMDock.target.zn_atoms = self.target_info.get_zn()
        self.AMDock.target.metals = self.target_info.get_metals()
        self.AMDock.target.het = self.target_info.get_het()
        self.offtarget_info = PDBINFO(self.AMDock.offtarget.input)
        self.AMDock.offtarget.zn_atoms = self.offtarget_info.get_zn()
        self.AMDock.offtarget.metals = self.offtarget_info.get_metals()
        self.AMDock.offtarget.het = self.offtarget_info.get_het()
        self.ligand_info = PDBINFO(self.AMDock.ligand.input)
        self.AMDock.ligand.ha = self.ligand_info.get_ha()
        self.lig_size = int(math.ceil(self.ligand_info.get_gyrate()))
        self.size = [self.lig_size, self.lig_size, self.lig_size]  # this avoid bug in pymol visualization
        self.sizeB = [self.lig_size, self.lig_size, self.lig_size]  # this avoid bug in pymol visualization

        if self.AMDock.ligand.ha > 100:
            wlig = QMessageBox.warning(self.AMDock, 'Warning', 'The input ligand has more than 100 heavy.\n Do '
                                                               'you want to continue?',
                                       QMessageBox.Yes | QMessageBox.No)
            if wlig == QMessageBox.No:
                self.reset_ligand()
                self.AMDock.project.mode = 0
                return
        if self.AMDock.docking_program == 'AutoDockZn':
            if self.AMDock.project.mode == 1:
                self.check_opt, pt1, pt2 = self.AMDock.checker.autodockzn_check(self.AMDock.target,
                                                                                self.AMDock.offtarget)
                if self.check_opt == QMessageBox.Ok:
                    self.AMDock.main_window.setCurrentIndex(0)
                    self.AMDock.main_window.setTabEnabled(1, False)
                    self.AMDock.main_window.setTabEnabled(0, True)
                    return
                else:
                    if not pt1:
                        os.remove(self.AMDock.target.input)
                        self.target_text.clear()
                        self.target_label.clear()
                        self.AMDock.target.input = None
                    if not pt2:
                        os.remove(self.AMDock.offtarget.input)
                        self.offtarget_text.clear()
                        self.offtarget_label.clear()
                        self.AMDock.offtarget.input = None
                    if self.AMDock.target.input == None and self.AMDock.offtarget.input == None:
                        self.progress(2, self.AMDock.project.mode, 'Define Target and Off-Target', 1)
                    elif not self.AMDock.target.input:
                        self.progress(5, self.AMDock.project.mode, 'Define Target', 1)
                    elif not self.AMDock.offtarget.input:
                        self.progress(5, self.AMDock.project.mode, 'Define Off-Target', 1)
                    return
            else:
                self.check_opt = self.AMDock.checker.autodockzn_check(self.AMDock.target)
                if self.check_opt == QMessageBox.Ok:
                    self.AMDock.main_window.setCurrentIndex(0)
                    self.AMDock.main_window.setTabEnabled(1, False)
                    self.AMDock.main_window.setTabEnabled(0, True)
                    return
                elif self.check_opt == QMessageBox.Cancel:
                    os.remove(self.AMDock.target.input)
                    self.target_text.clear()
                    self.target_label.clear()
                    self.AMDock.target.input = None
                    self.progress(4, self.AMDock.project.mode, 'Define Target', 1)
                    return
        else:
            if self.AMDock.project.mode == 1:
                self.check_opt, pt1, pt2 = self.AMDock.checker.check_correct_prog(self.AMDock.target,
                                                                                  self.AMDock.offtarget)
                if self.check_opt == QMessageBox.Yes:
                    self.AMDock.docking_program = "AutoDockZn"
                    self.AMDock.log_widget.textedit.append(Ft('DOCKING_PROGRAM: %s' %
                                                              self.AMDock.docking_program).definitions())
            else:
                self.check_opt = self.AMDock.checker.check_correct_prog(self.AMDock.target)
                if self.check_opt == QMessageBox.Yes:
                    self.AMDock.docking_program = "AutoDockZn"
                    self.AMDock.log_widget.textedit.append(Ft('DOCKING_PROGRAM: %s' %
                                                              self.AMDock.docking_program).definitions())
            self.AMDock.statusbar.removeWidget(self.AMDock.mess)
            self.AMDock.mess = QLabel(self.AMDock.docking_program + " is selected")
            self.AMDock.statusbar.addWidget(self.AMDock.mess)
        # added ligands (if exist) to list in binding site box
        if self.target_info.get_het():
            for res in self.target_info.get_het():
                self.lig_list.addItem('{}:{}:{}'.format(res[0], res[1][:3], res[1][3:]))
        if self.AMDock.project.mode == 1 and self.offtarget_info.get_het():
            for res in self.offtarget_info.get_het():
                self.lig_listB.addItem('{}:{}:{}'.format(res[0], res[1][:3], res[1][3:]))
        if self.AMDock.project.mode == 0:
            self.AMDock.log_widget.textedit.append(Ft('MODE: SIMPLE').definitions())
        elif self.AMDock.project.mode == 1:
            self.AMDock.log_widget.textedit.append(Ft('MODE: OFF-TARGET').definitions())
        else:
            self.AMDock.log_widget.textedit.append(Ft('MODE: SCORING').definitions())

        self.AMDock.log_widget.textedit.append(Ft('TARGET: %s' % self.AMDock.target.name).definitions())
        self.AMDock.log_widget.textedit.append(Ft('TARGET (Hetero): %s' % self.target_info.get_het()).definitions())
        self.AMDock.log_widget.textedit.append(Ft('TARGET (Zn atoms): %s' % self.target_info.get_zn()).definitions())
        if self.AMDock.project.mode == 1:
            self.AMDock.log_widget.textedit.append(Ft('OFF-TARGET: %s' % self.AMDock.offtarget.name).definitions())
            self.AMDock.log_widget.textedit.append(Ft('OFF-TARGET (Hetero): %s' %
                                                      self.offtarget_info.get_het()).definitions())
            self.AMDock.log_widget.textedit.append(Ft('OFF-TARGET (Zn atoms): %s' %
                                                      self.offtarget_info.get_zn()).definitions())
        self.AMDock.log_widget.textedit.append(Ft('LIGAND: %s' % self.AMDock.ligand.name).definitions())
        self.AMDock.log_widget.textedit.append(Ft('LIGAND (heavy_atoms): %s' %
                                                  self.AMDock.ligand.ha).definitions())
        self.AMDock.log_widget.textedit.append(Ft('Defining Initial Parameters... Done\n').section())
        self.AMDock.log_widget.textedit.append(Ft('Prepare Initial Files...').section())
        if self.AMDock.target.prepare:
            pdb2pqr = {'PDB2PQR': [self.AMDock.pdb2pqr_py, ['--titration-state-method=propka', '--noopt',
                                                            '--drop-water', '--keep-chain',
                                                            '--with-ph', str(self.pH_value.value()),
                                                            '--ff=%s' % self.AMDock.forcefield,
                                                            self.AMDock.target.input, self.AMDock.target.pqr]]}
            metals = []
            metals_text = None
            if self.keep_ions_btn.isChecked():
                if self.ions_text.text():
                    metals_text = str(self.ions_text.text())
                    metals = [['', '%s ' % x.split(':')[0], float(x.split(':')[1])] for x in metals_text.split(',')]
                else:
                    metals = self.AMDock.target.metals
            if self.AMDock.target.zn_atoms:
                metals = metals + self.AMDock.target.zn_atoms

            fix_pqr = {'Fix_PQR': [Fix_PQR, [self.AMDock.target.input, self.AMDock.target.pqr, metals]]}
            args = [self.AMDock.prepare_receptor4_py, '-r', self.AMDock.target.pdb, '-v', '-U',
                    'nphs_lps_waters_nonstdres_deleteAltB']
            if metals_text:
                args = args + ['-p', metals_text]

            prepare_receptor4 = {'Prepare_Receptor4': [self.AMDock.this_python, args]}
            self.list_process.append(pdb2pqr)
            self.list_process.append(fix_pqr)
            self.list_process.append(prepare_receptor4)
        else:
            self.AMDock.target.save_pdb(self.AMDock.target.input)
        if self.AMDock.project.mode == 1:
            if self.AMDock.offtarget.prepare:
                pdb2pqrB = {'PDB2PQR B': [self.AMDock.pdb2pqr_py, ['--titration-state-method=propka', '--noopt',
                                                                   '--drop-water', '--keep-chain',
                                                                   '--with-ph', str(self.pH_value.value()),
                                                                   '--ff=%s' % self.AMDock.forcefield,
                                                                   self.AMDock.offtarget.input,
                                                                   self.AMDock.offtarget.pqr]]}
                metals = []
                metals_text = None
                if self.keep_ions_btn.isChecked():
                    if self.ions_text.text():
                        metals_text = str(self.ions_text.text())
                        metals = [['', '%s ' % x.split(':')[0], float(x.split(':')[1])] for x in metals_text.split(',')]
                    else:
                        metals = self.AMDock.offtarget.metals
                if self.AMDock.offtarget.zn_atoms:
                    metals = metals + self.AMDock.offtarget.zn_atoms

                fix_pqrB = {'Fix_PQR B': [Fix_PQR, [self.AMDock.offtarget.input, self.AMDock.offtarget.pqr,
                                                    metals]]}

                args = [self.AMDock.prepare_receptor4_py, '-r', self.AMDock.offtarget.pdb, '-v', '-U',
                        'nphs_lps_waters_nonstdres_deleteAltB']
                if metals_text:
                    args = args + ['-p', metals_text]

                prepare_receptor4B = {'Prepare_Receptor4 B': [self.AMDock.this_python, args]}
                self.list_process.append(pdb2pqrB)
                self.list_process.append(fix_pqrB)
                self.list_process.append(prepare_receptor4B)
            else:
                self.AMDock.offtarget.save_pdb(self.AMDock.offtarget.input)
        if self.AMDock.ligand.prepare:
            prepare_lig_arg = [self.AMDock.prepare_ligand4_py, '-l']
            if self.AMDock.protonation:
                if self.AMDock.protonation_program == 'obabel':
                    protonate_ligand = {'Protonate Ligand': [self.AMDock.openbabel, ['-i', 'pdb',
                                                                                     self.AMDock.ligand.input, '-opdb',
                                                                                     '-O',
                                                                                     self.AMDock.ligand.pdb, '-h', '-p',
                                                                                     str(self.pH_value.value())]
                                                             ]}
                    prepare_lig_arg += [self.AMDock.ligand.pdb, '-v']
                    self.list_process.append(protonate_ligand)
                else:
                    prepare_lig_arg += [self.AMDock.ligand.input, '-A', 'hydrogens', '-v']
            else:
                prepare_lig_arg += [self.AMDock.ligand.input, '-v']
                self.AMDock.ligand.pdbqt = self.AMDock.ligand.name + '.pdbqt'
                self.AMDock.ligand.pdbqt_name = self.AMDock.ligand.name

            prepare_ligand4 = {'Prepare_Ligand4': [self.AMDock.this_python, prepare_lig_arg]}
            self.list_process.append(prepare_ligand4)
        else:
            self.AMDock.ligand.save_pdb(self.AMDock.ligand.input)

        queue = Queue()
        queue.name = 1
        for process in self.list_process:
            queue.put(process)
        self.W.set_queue(queue)  # , 'Prepare Input Files')
        self.W.start_process()

    def binding_site(self):
        queue = Queue()
        queue.name = 2
        if self.AMDock.state == 2:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'Other processes are running in the background. '
                                                             'Please wait for these to end.',
                                       QMessageBox.Ok)
            return
        elif self.AMDock.section in [-1, 0]:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'It seems that not all previous steps have been '
                                                             'completed. Please do all the steps sequentially.',
                                       QMessageBox.Ok)
            return
        elif self.AMDock.section in [2, 3]:
            msg = QMessageBox.warning(self.AMDock, 'Warning', 'This step was successfully completed previously.'
                                                              ' Do you want to repeat it?',
                                      QMessageBox.Yes | QMessageBox.No)
            if msg == QMessageBox.No:
                return

        if self.AMDock.project.bsd_mode_target == 0:
            self.target_info.get_box()
            args = [self.AMDock.prepare_gpf4_py, '-l', self.AMDock.ligand.pdbqt, '-r', self.AMDock.target.pdbqt, '-p',
                    'npts={0},{1},{2}'.format(*self.target_info.size), '-p', 'gridcenter={0},{1},{2}'.format(
                    *self.target_info.center), '-p', 'spacing=%.3f' % self.AMDock.spacing_autoligand, '-o',
                    self.AMDock.target.auto_lig]
            if self.AMDock.para_file:
                args = args + ['-p', 'parameter_file=%s' % self.AMDock.para_file]
            prepare_gpf4 = {'Prepare_gpf4': [self.AMDock.this_python, args]}
            queue.put(prepare_gpf4)
            autogrid4 = {'AutoGrid4': [self.AMDock.autogrid, ['-p', self.AMDock.target.auto_lig]]}
            queue.put(autogrid4)
            autoligand = {'AutoLigand': [self.AMDock.this_python, [self.AMDock.autoligand_py, '-r',
                                                                   self.AMDock.target.pdbqt_name, '-a',
                                                                   '{}'.format(self.AMDock.ligand.ha)]]}
            queue.put(autoligand)
        elif self.AMDock.project.bsd_mode_target == 1:
            self.AMDock.target.selected = str(self.grid_predef_text.text())
            self.target_info.get_box()
            self.target_info.get_center_selection(self.AMDock.target.selected)

            args = [self.AMDock.prepare_gpf4_py, '-l', self.AMDock.ligand.pdbqt, '-r', self.AMDock.target.pdbqt, '-p',
                    'npts={0},{1},{2}'.format(*self.target_info.size), '-p', 'gridcenter={0},{1},{2}'.format(
                    *self.grid_center), '-p', 'spacing=%.3f' % self.AMDock.spacing_autoligand, '-o',
                    self.AMDock.target.auto_lig]
            if self.AMDock.para_file:
                args = args + ['-p', 'parameter_file=%s' % self.AMDock.para_file]
            prepare_gpf4 = {'Prepare_gpf4': [self.AMDock.this_python, args]}
            queue.put(prepare_gpf4)
            autogrid4 = {'AutoGrid4': [self.AMDock.autogrid, ['-p', self.AMDock.target.auto_lig]]}
            queue.put(autogrid4)
            autoligand = {'AutoLigand_point': [self.AMDock.this_python, [self.AMDock.autoligand_py, '-r',
                                                                         self.AMDock.target.pdbqt_name, '-a',
                                                                         '{}'.format(self.AMDock.ligand.ha), '-x',
                                                                         self.target_info.selection_center[0], '-y',
                                                                         self.target_info.selection_center[1], '-z',
                                                                         self.target_info.selection_center[2], '-f',
                                                                         '1']]}
            queue.put(autoligand)
        elif self.AMDock.project.bsd_mode_target == 2:
            self.AMDock.target.selected = str(self.lig_list.currentText())
            self.target_info.get_center_selection(self.AMDock.target.selected)
            self.grid_center = self.target_info.selection_center
        elif self.AMDock.project.bsd_mode_target == 3:
            if self.need_grid:
                self.grid_center = [str(self.coor_x.value()), str(self.coor_y.value()), str(self.coor_z.value())]
                if self.size_x.value() < self.lig_size or self.size_y.value() < self.lig_size or self.size_z.value() < \
                        self.lig_size:
                    self.grid_opt, self.dim_list = smallbox_warning(self, {'x': self.size_x.value(),
                                                                           'y': self.size_y.value(),
                                                                           'z': self.size_z.value()}, self.lig_size,
                                                                    self.AMDock.target.name)
                    if self.grid_opt == QMessageBox.Yes:
                        if 'x' in self.dim_list:
                            self.size_x.setValue(self.lig_size)
                        if 'y' in self.dim_list:
                            self.size_y.setValue(self.lig_size)
                        if 'z' in self.dim_list:
                            self.size_z.setValue(self.lig_size)
                self.size = [int(self.size_x.value()), int(self.size_y.value()), int(self.size_z.value())]

        if self.AMDock.project.mode == 1:
            if self.AMDock.project.bsd_mode_offtarget == 0:
                self.offtarget_info.get_box()
                args = [self.AMDock.prepare_gpf4_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                        self.AMDock.offtarget.pdbqt, '-p', 'npts={0},{1},{2}'.format(*self.offtarget_info.size), '-p',
                        'gridcenter={0},{1},{2}'.format(*self.offtarget_info.center), '-p', 'spacing=%.3f' %
                        self.AMDock.spacing_autoligand, '-o', self.AMDock.offtarget.auto_lig]
                if self.AMDock.para_file:
                    args = args + ['-p', 'parameter_file=%s' % self.AMDock.para_file]

                prepare_gpf4B = {'Prepare_gpf4 B': [self.AMDock.this_python, args]}
                queue.put(prepare_gpf4B)
                autogrid4B = {'AutoGrid4 B': [self.AMDock.autogrid, ['-p', self.AMDock.offtarget.auto_lig]]}
                queue.put(autogrid4B)
                autoligandB = {'AutoLigand B': [self.AMDock.this_python, [self.AMDock.autoligand_py, '-r',
                                                                          self.AMDock.offtarget.pdbqt_name, '-a',
                                                                          '{}'.format(self.AMDock.ligand.ha)]]}
                queue.put(autoligandB)
            elif self.AMDock.project.bsd_mode_offtarget == 1:
                self.AMDock.offtarget.selected = str(self.grid_predef_textB.text())
                self.offtarget_info.get_box()
                self.offtarget_info.get_center_selection(self.AMDock.offtarget.selected)
                args = [self.AMDock.prepare_gpf4_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                        self.AMDock.offtarget.pdbqt, '-p', 'npts={0},{1},{2}'.format(*self.offtarget_info.size), '-p',
                        'gridcenter={0},{1},{2}'.format(*self.offtarget_info.center), '-p', 'spacing=%.3f' %
                        self.AMDock.spacing_autoligand, '-o', self.AMDock.offtarget.auto_lig]
                if self.AMDock.para_file:
                    args = args + ['-p', 'parameter_file=%s' % self.AMDock.para_file]

                prepare_gpf4B = {'Prepare_gpf4 B': [self.AMDock.this_python, args]}
                queue.put(prepare_gpf4B)
                autogrid4B = {'AutoGrid4 B': [self.AMDock.autogrid, ['-p', self.AMDock.offtarget.auto_lig]]}
                queue.put(autogrid4B)
                autoligandB = {'AutoLigand_point B': [self.AMDock.this_python, [self.AMDock.autoligand_py, '-r',
                                                                                self.AMDock.offtarget.pdbqt_name, '-a',
                                                                                '{}'.format(self.AMDock.ligand.ha),
                                                                                '-x',
                                                                                self.target_info.selection_center[0],
                                                                                '-y',
                                                                                self.target_info.selection_center[1],
                                                                                '-z',
                                                                                self.target_info.selection_center[2],
                                                                                '-f',
                                                                                '1']]}
                queue.put(autoligandB)

            elif self.AMDock.project.bsd_mode_offtarget == 2:
                self.AMDock.offtarget.selected = str(self.lig_listB.currentText())
                self.offtarget_info.get_center_selection(self.AMDock.offtarget.selected)
                self.grid_centerB = self.offtarget_info.selection_center

            elif self.AMDock.project.bsd_mode_offtarget == 3:
                if self.need_gridB:
                    self.grid_centerB = [str(self.coor_xB.value()), str(self.coor_yB.value()),
                                         str(self.coor_zB.value())]
                    if self.size_xB.value() < self.lig_size or self.size_yB.value() < self.lig_size or \
                            self.size_zB.value() < self.lig_size:
                        self.grid_optB, self.dim_listB = smallbox_warning(self, {'x': self.size_x.value(),
                                                                                 'y': self.size_y.value(),
                                                                                 'z': self.size_z.value()},
                                                                          self.lig_size, self.AMDock.offtarget.name)
                        if self.grid_optB == QMessageBox.Yes:
                            if 'x' in self.dim_listB:
                                self.size_xB.setValue(self.lig_size)
                            if 'y' in self.dim_listB:
                                self.size_yB.setValue(self.lig_size)
                            if 'z' in self.dim_listB:
                                self.size_zB.setValue(self.lig_size)
                        self.sizeB = [int(self.size_xB.value()), int(self.size_yB.value()), int(self.size_zB.value())]

        self.W.set_queue(queue)  # , 'Prepare Input Files')
        self.W.start_process()

    def check_res(self, qlineedit):
        inputtext = str(qlineedit.text()).upper()
        qlineedit.setText(inputtext)
        if qlineedit.objectName() == 'grid_predef_text':
            if self.target_info.check_select(inputtext):
                self.AMDock.target.bsd_ready = True
                self.checker_icon_ok.show()
                self.checker_icon.hide()
            else:
                self.AMDock.target.bsd_ready = False
                self.checker_icon.show()
                self.checker_icon_ok.hide()
        else:
            if self.offtarget_info.check_select(inputtext):
                self.AMDock.offtarget.bsd_ready = True
                self.checker_icon_okB.show()
                self.checker_iconB.hide()
            else:
                self.AMDock.offtarget.bsd_ready = False
                self.checker_iconB.show()
                self.checker_icon_okB.hide()

    def reset_input_section(self):
        self.reset_ligand()
        self.reset_target()
        self.reset_offtarget()
        # self.simulation_form()
        self.progressBar_section.setValue(0)
        self.progressBar_global.setValue(25)

    def reset_grid_section(self, all=False):
        self.grid_predef_text.clear()
        self.grid_predef_textB.clear()
        self.coor_x.setValue(0)
        self.coor_y.setValue(0)
        self.coor_z.setValue(0)
        self.coor_xB.setValue(0)
        self.coor_yB.setValue(0)
        self.coor_zB.setValue(0)
        self.size_x.setValue(30)
        self.size_y.setValue(30)
        self.size_z.setValue(30)
        self.size_xB.setValue(30)
        self.size_yB.setValue(30)
        self.size_zB.setValue(30)
        self.btnA_auto.setChecked(True)
        self.btnB_auto.setChecked(True)
        if all:
            self.lig_list.clear()
            self.lig_listB.clear()
            self.autoligand_target.clear()
            self.autoligand_target.setHorizontalHeaderLabels(["Total Volume (A**3)", "EPV (Kcal/mol A**3)"])
            self.autoligand_target.hide()
            self.autoligand_offtarget.clear()
            self.autoligand_offtarget.setHorizontalHeaderLabels(["Total Volume (A**3)", "EPV (Kcal/mol A**3)"])
            self.autoligand_offtarget.hide()
            self.grid_predef_text.clear()
            self.grid_predef_textB.clear()
        self.progressBar_global.setValue(50)

    def reset_sections(self, section):
        if self.AMDock.state == 2:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'Other processes are running in the background. '
                                                             'Please wait for these to end.',
                                       QMessageBox.Ok)
            return
        self.AMDock.section = section - 1
        self.highlight()
        if section == 0:
            self.wdir_text.clear()
            self.project_text.clear()
            self.proj_loc_label.clear()
            self.AMDock.project = PROJECT()
            self.reset_ligand()
            self.reset_target()
            self.reset_offtarget()
            self.reset_grid_section(True)
            self.pH_value.setValue(self.AMDock.pH)
            # self.progressBar_section.setValue(0)
            self.progressBar_global.setValue(0)
        elif section == 1:
            self.reset_ligand()
            self.reset_target()
            self.reset_offtarget()
            self.reset_grid_section(True)
            self.pH_value.setValue(self.AMDock.pH)
            # self.progressBar_section.setValue(0)
            self.progressBar_global.setValue(25)
        elif section == 2:
            self.reset_grid_section()
        elif section == 3:
            self.progressBar_global.setValue(75)

    def reset_function(self):
        if self.AMDock.state == 2:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'Other processes are running in the background. '
                                                             'Please wait for these to end.',
                                       QMessageBox.Ok)
            return

        if self.AMDock.section == -1:
            self.AMDock.main_window.setTabEnabled(0, True)
            self.AMDock.main_window.setCurrentIndex(0)
            self.AMDock.main_window.setTabEnabled(1, False)
            self.program_label.setText('Resetting...Done.')
            try:
                self.AMDock.statusbar.removeWidget(self.AMDock.mess)
            except:
                pass
            # return
        else:
            reset_opt = reset_warning(self)
            if reset_opt == QMessageBox.Yes:
                self.AMDock.section = -1
                self.AMDock.statusbar.removeWidget(self.AMDock.mess)
                self.program_label.setText('Resetting...Done.')
                self.highlight()
                self.AMDock.main_window.setTabEnabled(0, True)
                self.AMDock.main_window.setCurrentIndex(0)
                self.AMDock.main_window.setTabEnabled(1, False)

                self.wdir_text.clear()
                self.project_text.clear()
                self.proj_loc_label.clear()
                self.AMDock.project = PROJECT()
                self.AMDock.para_file = None
                self.new_para_text.clear()
                self.new_para_btn.setText('+')
                self.keep_ions_btn.setChecked(False)
                self.reset_ligand()
                self.reset_target()
                self.reset_offtarget()
                self.reset_grid_section(True)
                self.pH_value.setValue(self.AMDock.pH)
                self.progressBar_global.setValue(0)
                self.hide_all('all')
                # self.simple_docking.setChecked(True)
                self.simulation_form(self.simple_docking, True)
                if self.AMDock.project.WDIR:
                    rm_folder = QMessageBox.warning(self, 'Warning',
                                                    "Do you wish to delete the previous project's folder?.",
                                                    QMessageBox.Yes | QMessageBox.No)
                    if rm_folder == QMessageBox.Yes:
                        try:
                            self.AMDock.output2file.conclude()
                            os.chdir(self.AMDock.project.location)
                            shutil.rmtree(self.AMDock.project.WDIR)
                        except:
                            QMessageBox.warning(self, 'Error',
                                                "The directory cannot be deleted. Probably is being used by "
                                                "another program. Please check this and delete it ",
                                                QMessageBox.Ok)
                self.AMDock.configuration_tab.initial_config()
                self.AMDock.log_widget.textedit.append(Ft('\nRESETTING... Done.').resetting())
                self.AMDock.log_widget.textedit.append(Ft(80 * '-' + '\n\n').separator())
                return True

    def hide_all(self, l):
        if l == 'A':
            self.grid_predef_text.hide()
            self.checker_icon.hide()
            self.checker_icon_ok.hide()
            self.lig_list.hide()
            self.coor_box.hide()
            self.size_box.hide()
        elif l == 'B':
            self.grid_predef_textB.hide()
            self.checker_iconB.hide()
            self.checker_icon_okB.hide()
            self.lig_listB.hide()
            self.coor_boxB.hide()
            self.size_boxB.hide()
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

    def grid_sel_protection(self, id):
        if self.AMDock.state == 2:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'Other processes are running in the background. '
                                                             'Please wait for these to end.',
                                       QMessageBox.Ok)
            return
        elif self.AMDock.section in [-1, 0]:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'It seems that not all previous steps have been '
                                                             'completed. Please do all the steps sequentially.',
                                       QMessageBox.Ok)
            return
        elif self.AMDock.section in [2, 3]:
            msg = QMessageBox.warning(self.AMDock, 'Warning', 'This step was successfully completed previously.'
                                                              ' Do you want to repeat it?',
                                      QMessageBox.Yes | QMessageBox.No)
            if msg == QMessageBox.No:
                return
            elif msg == QMessageBox.Yes:
                self.reset_sections(2)
        self.AMDock.section = 1
        id.setChecked(True)
        self.grid_prot(id)

    def grid_prot(self, b):
        if self.target_column_group_btnA.id(b) == 1:
            self.hide_all('A')
            self.AMDock.project.bsd_mode_target = 0
        elif self.target_column_group_btnA.id(b) == 2:
            self.hide_all('A')
            self.grid_predef_text.clear()
            self.grid_predef_text.setReadOnly(False)
            self.grid_predef_text.show()
            self.checker_icon.show()
            self.AMDock.project.bsd_mode_target = 1
        elif self.target_column_group_btnA.id(b) == 3:
            if not self.lig_list.count():
                msg = QMessageBox.warning(self, 'Error', "There is no hetero to select this option",
                                          QMessageBox.Ok)
                self.btnA_auto.setChecked(True)
                return
            self.hide_all('A')
            self.lig_list.show()
            self.AMDock.project.bsd_mode_target = 2
        elif self.target_column_group_btnA.id(b) == 4:
            self.hide_all('A')
            self.AMDock.project.bsd_mode_target = 3
            self.coor_box.show()
            self.size_box.show()
        if self.offtarget_column_group_btnB.id(b) == 1:
            self.hide_all('B')
            self.AMDock.project.bsd_mode_offtarget = 0
        elif self.offtarget_column_group_btnB.id(b) == 2:
            self.hide_all('B')
            self.grid_predef_textB.clear()
            self.grid_predef_textB.setReadOnly(False)
            self.grid_predef_textB.show()
            self.checker_iconB.show()
            self.AMDock.project.bsd_mode_offtarget = 1
        elif self.offtarget_column_group_btnB.id(b) == 3:
            self.hide_all('B')
            self.lig_listB.show()
            self.AMDock.project.bsd_mode_offtarget = 2
        elif self.offtarget_column_group_btnB.id(b) == 4:
            self.hide_all('B')
            self.AMDock.project.bsd_mode_offtarget = 3
            self.coor_boxB.show()
            self.size_boxB.show()

    def grid_actions(self, btn):
        if self.AMDock.state == 2:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'Other processes are running in the background. '
                                                             'Please wait for these to end.',
                                       QMessageBox.Ok)
            return
        elif self.AMDock.section in [-1, 0, 1]:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'It seems that not all previous steps have been '
                                                             'completed. Please do all the steps sequentially.',
                                       QMessageBox.Ok)
            return
        elif self.AMDock.section in [3]:
            msg = QMessageBox.warning(self.AMDock, 'Warning', 'This step was successfully completed previously.'
                                                              ' Do you want to repeat it?',
                                      QMessageBox.Yes | QMessageBox.No)
            if msg == QMessageBox.No:
                return
        visual_arg = [self.AMDock.pymol, self.AMDock.grid_pymol, '--', '--f_prot',
                      os.path.join(self.AMDock.project.input, self.AMDock.target.pdb), '--f_prot_type', 'Target',
                      '--f_center', self.grid_center[0], self.grid_center[1], self.grid_center[2], '--f_size',
                      '%s' % self.size[0], '%s' % self.size[1], '%s' % self.size[2]]
        if self.AMDock.project.bsd_mode_target == 3:
            visual_arg.extend(['--f_rep_type', '3'])
        if self.AMDock.project.bsd_mode_target == 2:
            self.target_info.get_ligand(str(self.AMDock.target.selected), os.path.join(self.AMDock.project.input,
                                                                                       "target_sel_lig.pdb"))
            visual_arg.extend(['--f_rep_type', '2', '--f_ligands', os.path.join(self.AMDock.project.input,
                                                                                "target_sel_lig.pdb")])
        elif self.AMDock.project.bsd_mode_target == 1:
            visual_arg.extend(['--f_rep_type', '1', '--f_ligands', os.path.join(self.AMDock.project.input,
                                                                                "FILL_%s_%sout01.pdb" % (
                                                                                    self.AMDock.target.pdbqt_name,
                                                                                    self.AMDock.ligand.ha * 6)),
                               '--f_residues', self.AMDock.target.selected])
        elif self.AMDock.project.bsd_mode_target == 0:
            if not len(self.autoligand_target.selectedItems()):
                self.AMDock.target.selected = 1
                selection_model = self.autoligand_target.selectionModel()
                selection_model.select(self.autoligand_target.model().index(0, 0),
                                       QItemSelectionModel.ClearAndSelect)
            visual_arg.extend(['--f_rep_type', '0', '--f_ligands'])
            for fill in self.AMDock.target.fill_list:
                visual_arg.append('%s' % os.path.join(self.AMDock.project.input, "FILL_%s_%sout%02d.pdb" % (
                    self.AMDock.target.pdbqt_name, self.AMDock.ligand.ha * 6, int(fill))))

        if self.AMDock.project.mode == 1:
            visual_arg.extend(['--s_prot', os.path.join(self.AMDock.project.input, self.AMDock.offtarget.pdb),
                               '--s_prot_type', 'Off-Target', '--s_center', self.grid_centerB[0], self.grid_centerB[1],
                               self.grid_centerB[2], '--s_size', '%s' % self.sizeB[0], '%s' % self.sizeB[1],
                               '%s' % self.sizeB[2]])

            if self.AMDock.project.bsd_mode_offtarget == 3:
                visual_arg.extend(['--s_rep_type', '3'])
            if self.AMDock.project.bsd_mode_offtarget == 2:
                self.offtarget_info.get_ligand(str(self.AMDock.offtarget.selected), os.path.join(
                    self.AMDock.project.input, "offtarget_sel_lig.pdb"))
                visual_arg.extend(['--s_rep_type', '2', '--s_ligands', os.path.join(self.AMDock.project.input,
                                                                                    "offtarget_sel_lig.pdb")])
            elif self.AMDock.project.bsd_mode_offtarget == 1:
                visual_arg.extend(['--s_rep_type', '1', '--s_ligands', os.path.join(self.AMDock.project.input,
                                                                                    "FILL_%s_%sout01.pdb" % (
                                                                                        self.AMDock.offtarget.pdbqt_name,
                                                                                        self.AMDock.ligand.ha * 6)),
                                   '--s_residues', self.AMDock.offtarget.selected])
            elif self.AMDock.project.bsd_mode_offtarget == 0:
                if not len(self.autoligand_offtarget.selectedItems()):
                    self.AMDock.offtarget.selected = 1
                    selection_model = self.autoligand_offtarget.selectionModel()
                    selection_model.select(self.autoligand_offtarget.model().index(0, 0),
                                           QItemSelectionModel.ClearAndSelect)
                visual_arg.extend(['--s_rep_type', '0', '--s_ligands'])
                for fill in self.AMDock.offtarget.fill_list:
                    visual_arg.append('%s' % os.path.join(self.AMDock.project.input, "FILL_%s_%sout%02d.pdb" % (
                        self.AMDock.offtarget.pdbqt_name, self.AMDock.ligand.ha * 6, int(fill))))
        if visual_arg:
            self.box_pymol = {'PyMol_box_Target': [self.AMDock.this_python, visual_arg]}
            self.b_pymol = PROCESS()
            self.b_pymol.process.readyReadStandardOutput.connect(self.pymol_readStdOutput)
            self.b_pymol.process.readyReadStandardError.connect(self.readStdError)
            self.b_pymol.prog_finished.connect(self.for_finished)
            self.b_pymol.state.connect(self.check_state)
            b_pymolq = Queue()
            b_pymolq.name = -1
            b_pymolq.put(self.box_pymol)
            self.b_pymol.set_queue(b_pymolq)
            self.b_pymol.start_process()

    def autoligand_out(self, mol):
        ofile = open('{}_{}Results.txt'.format(mol.pdbqt_name, self.AMDock.ligand.ha * 6))
        fill = 1
        for line in ofile:
            line = line.strip('\n')
            fill_info = PDBINFO('FILL_{}_{}out{:02d}.pdb'.format(mol.pdbqt_name, self.AMDock.ligand.ha * 6, fill))
            if not fill_info.center:
                msg = QMessageBox.warning(self.AMDock, 'Warning', 'This FILL no exist or is not possible to open '
                                                                  'pdb file', QMessageBox.Ok)
                continue
            mol.fill_list[fill] = [int(float(line.split()[6].strip(','))), float(line.split()[13]), fill_info.center]
            fill += 1

    def fill_selection(self, autoligand_table):
        if autoligand_table.objectName() == 'autoligand_target':
            items = self.autoligand_target.selectedItems()
            row = self.autoligand_target.row(items[0]) + 1
            fill_info = PDBINFO(
                'FILL_{}_{}out{:02d}.pdb'.format(self.AMDock.target.pdbqt_name, self.AMDock.ligand.ha * 6, row))
            if fill_info.center:
                self.grid_center = [str(x) for x in fill_info.center]
            else:
                msg = QMessageBox.critical(self.AMDock, 'Error', 'This FILL no exist or is not possible to open '
                                                                 'pdb file. Please, select a new FILL',
                                           QMessageBox.Ok)
                for item in items:
                    item.setFlags(Qt.NoItemFlags)
                return
        else:
            items = self.autoligand_offtarget.selectedItems()
            row = self.autoligand_offtarget.row(items[0]) + 1
            fill_info = PDBINFO('FILL_{}_{}out{:02d}.pdb'.format(self.AMDock.offtarget.pdbqt_name, self.AMDock.ligand.ha
                                                                 * 6, row))
            if fill_info.center:
                self.grid_centerB = [str(x) for x in fill_info.center]
            else:
                msg = QMessageBox.critical(self.AMDock, 'Error', 'This FILL no exist or is not possible to open '
                                                                 'pdb file. Please, select a new FILL',
                                           QMessageBox.Ok)
                for item in items:
                    item.setFlags(Qt.NoItemFlags)
                return

    def for_finished(self, info):
        prog_name, exitcode, exitstatus = info
        self.AMDock.project.part = 0
        if exitcode:
            self.progressBar_section.setValue(0)
            error_message(self, prog_name, exitcode, exitstatus)
            return
        if prog_name == 'AutoLigand':
            fill_list = self.autoligand_out(self.AMDock.target)
            if self.AMDock.target.fill_list:
                self.autoligand_target.setRowCount(len(self.AMDock.target.fill_list))
                f = 0
                for fill in self.AMDock.target.fill_list:
                    c = 0
                    for ele in self.AMDock.target.fill_list[fill][:2]:
                        ele = str(ele)
                        self.autoligand_target.setItem(f, c, QTableWidgetItem(ele))
                        self.autoligand_target.item(f, c).setTextAlignment(
                            Qt.AlignHCenter | Qt.AlignVCenter)
                        c += 1
                    f += 1
                self.autoligand_target.selectRow(0)
                self.autoligand_target.show()
                self.grid_center = [str(x) for x in self.AMDock.target.fill_list[1][2]]
        elif prog_name == 'AutoLigand_point':
            fill_list = self.autoligand_out(self.AMDock.target)
            if self.AMDock.target.fill_list:
                self.grid_center = [str(x) for x in self.AMDock.target.fill_list[1][2]]
        elif prog_name == 'AutoLigand B':
            fill_list = self.autoligand_out(self.AMDock.offtarget)
            if self.AMDock.offtarget.fill_list:
                self.autoligand_offtarget.setRowCount(len(self.AMDock.offtarget.fill_list))
                f = 0
                for fill in self.AMDock.offtarget.fill_list:
                    c = 0
                    for ele in fill:
                        ele = str(ele)
                        self.autoligand_offtarget.setItem(f, c, QTableWidgetItem(ele))
                        self.autoligand_offtarget.item(f, c).setTextAlignment(
                            Qt.AlignHCenter | Qt.AlignVCenter)
                        c += 1
                    f += 1
                self.autoligand_offtarget.selectRow(0)
                self.autoligand_offtarget.show()
                self.grid_centerB = [str(x) for x in self.AMDock.offtarget.fill_list[1][2]]
        elif prog_name == 'AutoLigand_point B':
            fill_list = self.autoligand_out(self.AMDock.offtarget)
            if self.AMDock.offtarget.fill_list:
                self.grid_centerB = [str(x) for x in self.AMDock.offtarget.fill_list[1][2]]

        if prog_name == 'PDB2PQR':
            if not exitcode:
                self.progress(40, self.AMDock.project.mode, 'Running PDB2PQR for Target...Done.')
                self.AMDock.log_widget.textedit.append(Ft('Running PDB2PQR for Target...Done.').process())
        elif prog_name == 'PDB2PQR B':
            if not exitcode:
                self.progress(20, 0, 'Running PDB2PQR for Off-Target...Done')
                self.AMDock.log_widget.textedit.append(Ft('Running PDB2PQR for Off-Target...Done.').process())
        elif prog_name == 'Prepare_Receptor4':
            if not exitcode:
                self.progress(40, self.AMDock.project.mode, 'Prepare receptor (Target)...Done')
                self.AMDock.log_widget.textedit.append(Ft('Prepare Target...Done.').process())
        elif prog_name == 'Prepare_Receptor4 B':
            if not exitcode:
                self.progress(20, 0, 'Prepare receptor (Off-Target)...Done')
                self.AMDock.log_widget.textedit.append(Ft('Prepare Off-Target...Done.').process())
        elif prog_name == 'Prepare_Ligand4':
            if not exitcode:
                self.progress(20, 0, 'Prepare ligand...Done')
                self.AMDock.log_widget.textedit.append(Ft('Prepare Ligand...Done.').process())
        if self.AMDock.section == 1:
            if self.AMDock.project.bsd_mode_target in [0, 1]:
                if prog_name == 'Prepare_gpf4':
                    self.progress(10, self.AMDock.project.mode, 'Generate Target GPF file...', 1)
                    self.AMDock.log_widget.textedit.append(Ft('Generate Target GPF file...Done.').process())
                if prog_name == 'Prepare_gpf4zn':
                    self.progress(10, self.AMDock.project.mode, 'Generate Target GPF file...', 1)
                    self.AMDock.log_widget.textedit.append(Ft('Generate Target GPF file...Done.').process())
                if prog_name == 'AutoGrid4':
                    self.progress(50, self.AMDock.project.mode, 'Running AutoGrid4 for Target...', 1)
                    self.AMDock.log_widget.textedit.append(
                        Ft('Running AutoGrid4 for Target Protein... Done.').process())

                if prog_name in ['AutoLigand', 'AutoLigand_point']:
                    self.progress(100, self.AMDock.project.mode, 'Searching Ligand Binding Site in Target...', 1)

                    self.AMDock.log_widget.textedit.append(Ft('Searching Ligand Binding Site in Target '
                                                              'Protein... Done.').process())
            if self.AMDock.project.bsd_mode_offtarget in [0, 1]:
                if prog_name == 'Prepare_gpf4 B':
                    self.progress(55, 0, 'Generate Off-Target GPF file...', 1)
                    self.AMDock.log_widget.textedit.append(Ft('Generate GPF file for Off-Target Protein... '
                                                              'Done.').process())
                if prog_name == 'Prepare_gpf4zn B':
                    self.progress(55, 0, 'Generate Off-Target GPF file...', 1)
                    self.AMDock.log_widget.textedit.append(Ft('Generate GPF file for Off-Target Protein... '
                                                              'Done.').process())
                if prog_name == 'AutoGrid4 B':
                    self.part = 0
                    self.progress(75, 0, 'Running AutoGrid4 for Off-Target...', 1)
                    self.AMDock.log_widget.textedit.append(Ft('Running AutoGrid4 for Off-Target '
                                                              'Protein... Done.').process())
                if prog_name in ['AutoLigand B', 'AutoLigand_point B']:
                    self.progress(100, 0, 'Searching Ligand Binding Site in Off-Target...', 1)
                    self.AMDock.log_widget.textedit.append(Ft('Running AutoLigand in Off-Target Protein... '
                                                              'Done.').process())
        elif self.AMDock.section == 2:
            if prog_name == 'Prepare_gpf4':
                if self.AMDock.project.bsd_mode_target == 0:
                    self.progress(10 / len(self.AMDock.target.fill_list), self.AMDock.project.mode,
                                  'Generate GPF file...')
                else:
                    self.progress(10, self.AMDock.project.mode, 'Generate GPF file...', 1)
            if prog_name == 'Prepare_gpf4 B':
                if self.AMDock.project.bsd_mode_offtarget == 0:
                    self.progress(5 / len(self.AMDock.offtarget.fill_list), 0, 'Generate GPF file...')
                else:
                    self.progress(55, 0, 'Generate GPF file...', 1)
            if prog_name == 'AutoGrid4':
                if self.AMDock.project.bsd_mode_target == 0:
                    self.progress(40 / len(self.AMDock.target.fill_list), self.AMDock.project.mode, 'Running AutoGrid4 '
                                                                                                    'for Target...')
                else:
                    self.progress(50, self.AMDock.project.mode, 'Running AutoGrid4 for Target...', 1)
            if prog_name == 'AutoGrid4 B':
                if self.AMDock.project.bsd_mode_offtarget == 0:
                    self.progress(40 / len(self.AMDock.offtarget.fill_list), 0, 'Running AutoGrid4 for Off-Target...')
                else:
                    self.progress(75, 0, 'Running AutoGrid4 for Off-Target...', 1)
            if prog_name == 'Prepare_dpf4':
                if self.AMDock.project.bsd_mode_target == 0:
                    self.progress(10 / len(self.AMDock.target.fill_list), self.AMDock.project.mode,
                                  'Generate DPF file...')
                else:
                    self.progress(60, self.AMDock.project.mode, 'Generate DPF file...', 1)
            if prog_name == 'Prepare_dpf4 B':
                if self.AMDock.project.bsd_mode_offtarget == 0:
                    self.progress(5 / len(self.AMDock.offtarget.fill_list), 0, 'Generate DPF file...')
                else:
                    self.progress(80, 0, 'Generate DPF file...', 1)

        if prog_name == 'AutoDock Vina':
            if self.AMDock.project.bsd_mode_target == 0 and self.AMDock.project.mode != 2:
                self.progress(100 / len(self.AMDock.target.fill_list), self.AMDock.project.mode,
                              'Determining better poses for Target...')
            else:
                self.progress(100, self.AMDock.project.mode, 'Determining better poses for Target...', 1)
        if prog_name == 'AutoDock Vina B':
            if self.AMDock.project.bsd_mode_target == 0:
                self.progress(100 / len(self.AMDock.target.fill_list), 0,
                              'Determining better poses for Target...')
            else:
                self.progress(100, 0, 'Determining better poses for Target...', 1)
        if prog_name == 'AutoDock4':
            self.timerAD.stop()
            self.autodock_output()
            if self.AMDock.project.bsd_mode_target == 0 and self.AMDock.project.mode != 2:
                self.progress(100 / len(self.AMDock.target.fill_list), self.AMDock.project.mode, 'Determining better '
                                                                                                 'poses for Target...')
            else:
                self.progress(100, self.AMDock.project.mode, 'Determining better poses for Target...', 1)

            self.AMDock.log_widget.textedit.append(Ft('Running AutoDock4... Done.').process())
        if prog_name == 'AutoDock4 B':
            self.timerAD.stop()
            self.autodock_output()
            if self.AMDock.project.bsd_mode_offtarget == 0:
                self.progress(100 / len(self.AMDock.offtarget.fill_list), 0, 'Determining better poses for '
                                                                             'Off-Target...')
            else:
                self.progress(100, 0, 'Determining better poses for Target...', 1)
        if prog_name == 'AutoDock4ZN':
            self.timerAD.stop()
            self.autodock_output()
            if self.AMDock.project.bsd_mode_target == 0 and self.AMDock.project.mode != 2:
                self.progress(100 / len(self.AMDock.target.fill_list), self.AMDock.project.mode,
                              'Determining better poses for Target...')
            else:
                self.progress(100, self.AMDock.project.mode, 'Determining better poses for Target...', 1)
        if prog_name == 'AutoDock4ZN B':
            self.timerAD.stop()
            self.autodock_output()
            if self.AMDock.project.bsd_mode_offtarget == 0:
                self.progress(100 / len(self.AMDock.offtarget.fill_list), 0, 'Determining better poses for '
                                                                             'Off-Target...')
            else:
                self.progress(100, 0, 'Determining better poses for Target...', 1)

        if prog_name == 'Align':
            self.AMDock.log_widget.textedit.append(Ft('Running proteins alignment... Done').process())

        if prog_name == 'PyMol_box_Target':
            if hasattr(self, 'b_pymol'):
                delattr(self, 'b_pymol')
        elif prog_name == 'PyMol_box_Off-Target':
            if hasattr(self, 'b_pymolB'):
                delattr(self, 'b_pymolB')
        else:
            self.W.start_process()

    def progress(self, value, mode=0, mess=None, set=0):
        if mode == 1 and value:
            value = value / 2
        if set:
            self.progressBar_section.setValue(value)
        else:
            self.progressBar_section.setValue(self.progressBar_section.value() + value)

    def readStdOutput(self):
        self.codec = QTextCodec.codecForName('UTF-8')
        self.output = self.codec.toUnicode(self.W.process.readAllStandardOutput())
        # self.output = str(self.output)
        if not self.AMDock.project.prog in ['AutoLigand', 'AutoLigand B']:
            if self.AMDock.log_level == 2:
                self.AMDock.log_widget.textedit.insertPlainText(self.output)
        # thread = THREAD(self.AMDock, self.output)
        # thread.run()
        print(self.output)
        self.output = str(self.output)
        if self.AMDock.project.prog == 'AutoGrid4':
            if re.search('%', self.output):
                try:
                    current = float(self.output.split()[2].strip('%')) * 0.4 - self.AMDock.project.part
                except:
                    return
                if self.AMDock.project.bsd_mode_target == 0 and self.AMDock.section == 2:
                    self.progress(current / len(self.AMDock.target.fill_list), self.AMDock.project.mode)
                else:
                    self.progress(current, self.AMDock.project.mode)
                self.AMDock.project.part = float(self.output.split()[2].strip('%')) * 0.4
        elif self.AMDock.project.prog == 'AutoGrid4 B':
            if re.search('%', self.output):
                try:
                    current = float(self.output.split()[2].strip('%')) * 0.4 - self.AMDock.project.part
                except:
                    return
                if self.AMDock.project.bsd_mode_offtarget == 0 and self.AMDock.section == 2:
                    self.progress(current / len(self.AMDock.offtarget.fill_list), 0)
                else:
                    self.progress(current, 0)
                self.AMDock.project.part = float(self.output.split()[2].strip('%')) * 0.4

        elif self.AMDock.project.prog == 'AutoDock Vina':
            current = self.output.count('*') * 2 * (50. / 51)
            if self.AMDock.project.bsd_mode_target != 0:
                self.progress(current, self.AMDock.project.mode, mess='Running Molecular Docking Simulation...')

        elif self.AMDock.project.prog == 'AutoDock Vina B':
            current = self.output.count('*') * (50. / 51)
            if self.AMDock.project.bsd_mode_offtarget != 0:
                self.progress(current, 0)
        elif self.AMDock.project.prog == 'AutoLigand':
            if re.search('Progress:', self.output):
                try:
                    current = float(self.output.split()[1]) * 0.4 - self.AMDock.project.part
                except:
                    return
                self.progress(current, self.AMDock.project.mode)
                self.AMDock.project.part = float(self.output.split()[1]) * 0.4
        elif self.AMDock.project.prog == 'AutoLigand B':
            if re.search('Progress:', self.output):
                try:
                    current = float(self.output.split()[1]) * 0.4 - self.AMDock.project.part
                except:
                    return
                self.progress(current, 0)
                self.AMDock.project.part = float(self.output.split()[1]) * 0.4

    def readStdError(self):
        self.error = str(self.worker.readAllStandardError())

    def pymol_readStdOutput(self):
        pymol_output = None
        if hasattr(self, 'b_pymol'):
            pymol_output = str(self.b_pymol.process.readAllStandardOutput())
        if pymol_output:
            self.pymol_out = str(pymol_output)
        else:
            return
        print(self.pymol_out)
        if re.search('AMDock INFO', self.pymol_out):
            if len(self.pymol_out.split()) > 9:
                a, i, prot, cx, cy, cz, sx, sy, sz, prot1, cx1, cy1, cz1, sx1, sy1, sz1 = self.pymol_out.split()
                if prot1:
                    self.btnB_user.setChecked(True)
                    self.coor_xB.setValue(float(cx1))
                    self.coor_yB.setValue(float(cy1))
                    self.coor_zB.setValue(float(cz1))
                    self.size_xB.setValue(int(sx1))
                    self.size_yB.setValue(int(sy1))
                    self.size_zB.setValue(int(sz1))
                    self.grid_centerB = [str(self.coor_xB.value()), str(self.coor_yB.value()),
                                         str(self.coor_zB.value())]
                    self.sizeB = [self.size_xB.value(), self.size_yB.value(), self.size_zB.value()]
            else:
                a, i, prot, cx, cy, cz, sx, sy, sz = self.pymol_out.split()

            if prot == 'target':
                self.btnA_user.setChecked(True)
                self.coor_x.setValue(float(cx))
                self.coor_y.setValue(float(cy))
                self.coor_z.setValue(float(cz))
                self.size_x.setValue(int(float(sx)))
                self.size_y.setValue(int(float(sy)))
                self.size_z.setValue(int(float(sz)))
                self.grid_center = [str(self.coor_x.value()), str(self.coor_y.value()), str(self.coor_z.value())]
                self.size = [self.size_x.value(), self.size_y.value(), self.size_z.value()]

            elif prot == 'off-target':
                self.btnB_user.setChecked(True)
                self.coor_xB.setValue(float(cx))
                self.coor_yB.setValue(float(cy))
                self.coor_zB.setValue(float(cz))
                self.size_xB.setValue(int(float(sx)))
                self.size_yB.setValue(int(float(sy)))
                self.size_zB.setValue(int(float(sz)))
                self.grid_centerB = [str(self.coor_xB.value()), str(self.coor_yB.value()), str(self.coor_zB.value())]
                self.sizeB = [self.size_xB.value(), self.size_yB.value(), self.size_zB.value()]

            self.AMDock.section = 1
            self.progressBar_global.setValue(50)

    def autodock_output(self):
        if self.AMDock.project.prog in ['AutoDock4', 'AutoDock4ZN']:
            if self.AMDock.project.mode != 2:
                self.ADout_file = os.path.join(self.AMDock.project.results, self.AMDock.ligand.pdbqt_name + '_' +
                                               self.AMDock.target.dlg)
        elif self.AMDock.project.prog in ['AutoDock4 B', 'AutoDock4ZN B']:
            self.ADout_file = os.path.join(self.AMDock.project.results, self.AMDock.ligand.pdbqt_name + '_' +
                                           self.AMDock.offtarget.dlg)

        if self.AMDock.project.mode == 2:
            return
        ADout = open(self.ADout_file)
        Ad_count = 0
        local_line = 1
        for line in ADout:
            line = line.strip('\n')
            if local_line > self.ad4_line:
                self.AMDock.log_widget.textedit.append(line)
                print(line)
            local_line += 1
            if re.search('DOCKED: MODEL', line):
                Ad_count += 1
            else:
                continue
        ADout.close()
        self.ad4_line = local_line

        if self.AMDock.ga_run <= 40:
            current = float(Ad_count) / self.AMDock.ga_run * 40 - self.AMDock.project.part
        else:
            current = float(Ad_count) / self.AMDock.ga_run * 0.4 - self.AMDock.project.part
        if current < 1:
            return
        self.progress(current, self.AMDock.project.mode)
        if self.AMDock.ga_run <= 40:
            self.AMDock.project.part = float(Ad_count) / self.AMDock.ga_run * 40
        else:
            self.AMDock.project.part = float(Ad_count) / self.AMDock.ga_run * 0.4

    def lig_select(self, lig):
        if lig.objectName() == 'lig_list':
            self.AMDock.target.selected = str(self.lig_list.currentText())
        else:
            self.AMDock.offtarget.selected = str(self.lig_listB.currentText())

    def go_result(self):
        self.AMDock.result_tab.import_text.setText(self.AMDock.project.output)
        self.AMDock.statusbar.showMessage(" Go to Results Analysis", 2000)
        self.AMDock.main_window.setTabEnabled(2, True)
        self.AMDock.main_window.setCurrentIndex(2)
        self.AMDock.main_window.setTabEnabled(1, False)
        self.AMDock.main_window.setTabEnabled(0, False)
        os.chdir(self.AMDock.project.results)
        self.AMDock.result_tab.prot_label.setText('Target: %s' % self.AMDock.target.name)
        self.AMDock.result_tab.prot_labelB.setText('Off-Target: %s' % self.AMDock.offtarget.name)
        self.AMDock.result_tab.prot_label_sel.setText('%s' % self.AMDock.target.name)
        self.AMDock.result_tab.prot_label_selB.setText('%s' % self.AMDock.offtarget.name)
        self.re = Result_Analysis(self.AMDock.docking_program, self.AMDock.target, self.AMDock.ligand)
        self.results = self.re.result2table(self.AMDock.target.all_poses)
        self.AMDock.result_tab.result_table.setRowCount(len(self.results))
        self.AMDock.result_tab.sele1.setRange(1, len(self.results))
        self.result2out = ''
        f = 0
        for x in self.results:
            c = 0
            self.result2out += '|' + ('%s' % x[0]).center(15) + '|' + ('%s' % x[1]).center(16) + '|' + \
                               ('%s' % x[2]).center(14) + '|' + ('%s' % x[3]).center(15) + '|' + \
                               ('%s' % x[4]).center(14) + '|\n'
            for item in x:
                item_table = QTableWidgetItem(str(item))
                item_table.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.AMDock.result_tab.result_table.setItem(f, c, item_table)
                self.AMDock.result_tab.result_table.item(f, c).setTextAlignment(
                    Qt.AlignHCenter | Qt.AlignVCenter)
                if c == 4:
                    item_v = float(item)
                    if item_v <= -0.3:
                        self.AMDock.result_tab.result_table.item(f, c).setBackground(
                            QColor(0, 255, 128, 200))
                c += 1
            f += 1
        self.AMDock.result_tab.value1 = float(self.AMDock.result_tab.result_table.item(0, 1).text())
        self.AMDock.result_tab.result_table.item(0, 1).setBackground(QColor('darkGray'))
        selection_model = self.AMDock.result_tab.result_table.selectionModel()
        selection_model.select(self.AMDock.result_tab.result_table.model().index(0, 0),
                               QItemSelectionModel.ClearAndSelect)
        if self.AMDock.project.bsd_mode_target == 0:
            self.AMDock.result_tab.result_table.setHorizontalHeaderLabels(
                str("Binding Site;Affinity(kcal/mol);Estimated Ki;Ki Units;Ligand Efficiency").split(";"))

        if self.AMDock.project.mode == 1:
            self.AMDock.result_tab.result_tableB.show()
            self.AMDock.result_tab.selectivity_value_text.show()
            self.AMDock.result_tab.selectivity.show()
            self.AMDock.result_tab.sele1.show()
            self.AMDock.result_tab.sele2.show()
            self.AMDock.result_tab.prot_label_sel.show()
            self.AMDock.result_tab.prot_label_selB.show()
            self.AMDock.result_tab.div.show()
            self.AMDock.result_tab.equal.show()
            self.AMDock.result_tab.prot_labelB.show()
            self.reB = Result_Analysis(self.AMDock.docking_program, self.AMDock.offtarget, self.AMDock.ligand)
            self.resultsB = self.reB.result2table(self.AMDock.offtarget.all_poses)
            self.AMDock.result_tab.result_tableB.setRowCount(len(self.resultsB))
            self.AMDock.result_tab.sele2.setRange(1, len(self.resultsB))
            f = 0
            self.result2outB = ''
            for x in self.resultsB:
                c = 0
                self.result2outB += '|' + ('%s' % x[0]).center(15) + '|' + ('%s' % x[1]).center(16) + '|' + \
                                    ('%s' % x[2]).center(14) + '|' + ('%s' % x[3]).center(15) + '|' + \
                                    ('%s' % x[4]).center(14) + '|\n'
                for item in x:
                    item_table = QTableWidgetItem(str(item))
                    item_table.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    self.AMDock.result_tab.result_tableB.setItem(f, c, item_table)
                    self.AMDock.result_tab.result_tableB.item(f, c).setTextAlignment(
                        Qt.AlignHCenter | Qt.AlignVCenter)
                    if c == 4:
                        item_v = float(item)
                        if item_v <= -0.3:
                            self.AMDock.result_tab.result_tableB.item(f, c).setBackground(
                                QColor(0, 255, 128, 200))
                    c += 1
                f += 1
            self.AMDock.result_tab.value2 = float(self.AMDock.result_tab.result_tableB.item(0, 1).text())

            self.AMDock.result_tab.result_tableB.item(0, 1).setBackground(QColor('darkGray'))
            selection_model = self.AMDock.result_tab.result_tableB.selectionModel()
            selection_model.select(self.AMDock.result_tab.result_tableB.model().index(0, 0),
                                   QItemSelectionModel.ClearAndSelect)

            self.AMDock.result_tab.selectivity_value = math.exp((self.AMDock.result_tab.value2 -
                                                                 self.AMDock.result_tab.value1) / (0.001987207 * 298))
            self.AMDock.result_tab.selectivity_value_text.setText(
                '%.01f' % self.AMDock.result_tab.selectivity_value)
            if self.AMDock.project.bsd_mode_offtarget == 0:
                self.AMDock.result_tab.result_tableB.setHorizontalHeaderLabels(
                    str("Binding Site;Affinity(kcal/mol);Estimated Ki;Ki Units;Ligand Efficiency").split(
                        ";"))
        else:
            self.AMDock.result_tab.result_tableB.hide()
            self.AMDock.result_tab.selectivity_value_text.hide()
            self.AMDock.result_tab.selectivity.hide()
            self.AMDock.result_tab.sele1.hide()
            self.AMDock.result_tab.sele2.hide()
            self.AMDock.result_tab.prot_label_sel.hide()
            self.AMDock.result_tab.prot_label_selB.hide()
            self.AMDock.result_tab.div.hide()
            self.AMDock.result_tab.equal.hide()
            self.AMDock.result_tab.prot_labelB.hide()
        self.amdock_output_file()
        amdock_file = open(self.AMDock.project.output)
        for line in amdock_file:
            line = line.strip('\n')
            self.AMDock.result_tab.rfile_show.textedit.append(line)
        amdock_file.close()

    def amdock_output_file(self):
        """make amdock output file"""
        self.AMDock.output2file.file_header(self.AMDock.project.output)
        self.AMDock.output2file.out2file('AMDOCK: DOCKING_PROGRAM'.ljust(24) + '%s\n' % self.AMDock.docking_program)
        self.AMDock.output2file.out2file('AMDOCK: PROJECT'.ljust(24) + 56 * '-' + '\n')
        self.AMDock.output2file.out2file('AMDOCK: PROJECT_NAME'.ljust(24) + '%s\n' % self.AMDock.project.name)
        self.AMDock.output2file.out2file('AMDOCK: WORKING_DIR'.ljust(24) + '%s\n' % self.AMDock.project.WDIR)
        # input section
        self.AMDock.output2file.out2file('AMDOCK: INPUT'.ljust(24) + 56 * '-' + '\n')
        if self.AMDock.project.mode == 0:
            self.AMDock.output2file.out2file('AMDOCK: MODE'.ljust(24) + 'SIMPLE\n')
        elif self.AMDock.project.mode == 1:
            self.AMDock.output2file.out2file('AMDOCK: MODE'.ljust(24) + 'OFF-TARGET\n')
        else:
            self.AMDock.output2file.out2file('AMDOCK: MODE'.ljust(24) + 'SCORING\n')
        self.AMDock.output2file.out2file('AMDOCK: TARGET'.ljust(24) + '%s\n' % self.AMDock.target.name)
        if self.target_info.get_het():
            het = ''
            c = 0
            for res in self.target_info.get_het():
                if c == len(self.target_info.get_het()):
                    het += '{}:{}:{}'.format(res[0], res[1][:3], res[1][3:])
                else:
                    het += '{}:{}:{}, '.format(res[0], res[1][:3], res[1][3:])
                c += 1
            self.AMDock.output2file.out2file('AMDOCK: TARGET_HET'.ljust(24) + '%s\n' % het)
        if self.target_info.get_zn():
            zn = ''
            c = 0
            for res in self.target_info.get_zn():
                if c == len(self.target_info.get_zn()):
                    zn += '{}:{}:{}'.format(res[0], res[1][:3], res[1][3:])
                else:
                    zn += '{}:{}:{}, '.format(res[0], res[1][:3], res[1][3:])
                c += 1
            self.AMDock.output2file.out2file('AMDOCK: TARGET_ZN'.ljust(24) + '%s\n' % zn)
        if self.AMDock.project.mode == 1:
            self.AMDock.output2file.out2file('AMDOCK: OFF-TARGET'.ljust(24) + '%s\n' % self.AMDock.offtarget.name)
            if self.offtarget_info.get_het():
                het = ''
                c = 0
                for res in self.offtarget_info.get_het():
                    if c == len(self.offtarget_info.get_het()):
                        het += '{}:{}:{}'.format(res[0], res[1][:3], res[1][3:])
                    else:
                        het += '{}:{}:{}, '.format(res[0], res[1][:3], res[1][3:])
                    c += 1
                self.AMDock.output2file.out2file('AMDOCK: OFF-TARGET_HET'.ljust(24) + '%s\n' % het)
            if self.offtarget_info.get_zn():
                zn = ''
                c = 0
                for res in self.offtarget_info.get_zn():
                    if c == len(self.offtarget_info.get_zn()):
                        zn += '{}:{}:{}'.format(res[0], res[1][:3], res[1][3:])
                    else:
                        zn += '{}:{}:{}, '.format(res[0], res[1][:3], res[1][3:])
                    c += 1
                self.AMDock.output2file.out2file('AMDOCK: OFF-TARGET_ZN'.ljust(24) + '%s\n' % zn)
        self.AMDock.output2file.out2file('AMDOCK: LIGAND'.ljust(24) + '%s\n' % self.AMDock.ligand.name)
        self.AMDock.output2file.out2file('AMDOCK: LIGAND_HA'.ljust(24) + '%s\n' % self.AMDock.ligand.ha)
        # binding site definition section
        self.AMDock.output2file.out2file('AMDOCK: SEARCH_SPACE'.ljust(24) + (56 * '-' + '\n'))
        if self.AMDock.project.mode != 2:
            if self.AMDock.project.bsd_mode_target == 0:
                mode = 'AUTOMATIC'
            elif self.AMDock.project.bsd_mode_target == 1:
                mode = 'CENTERED_ON_RESIDUE(S)'
            elif self.AMDock.project.bsd_mode_target == 2:
                mode = 'CENTERED_ON_HETERO'
            else:
                mode = 'USER-DEFINED_BOX'

            self.AMDock.output2file.out2file('AMDOCK: T_BOX_MODE'.ljust(24) + '%s\n' % mode)
            if self.AMDock.project.bsd_mode_target in [2, 3]:
                self.AMDock.output2file.out2file('AMDOCK: TARGET_BOX'.ljust(24) + 'CENTER: {:7.02f} {:7.02f} {:7.02f} '
                                                                                  'SIZE: {:2d} {:2d} {:2d}\n'.format(
                    float(self.grid_center[0]), float(self.grid_center[1]), float(self.grid_center[2]), self.size[0],
                    self.size[1], self.size[2]))
            else:
                for fill in self.AMDock.target.fill_list:
                    self.AMDock.output2file.out2file('AMDOCK: TARGET_BOX'.ljust(24) + 'FILL: {:02d} CENTER: {:7.02f}'
                                                                                      ' {:7.02f} {:7.02f} SIZE: {:2d} '
                                                                                      '{:2d} {:2d}\n'.format(
                        fill, self.AMDock.target.fill_list[fill][2][0], self.AMDock.target.fill_list[fill][2][1],
                        self.AMDock.target.fill_list[fill][2][2], self.size[0], self.size[1], self.size[2]))
            if self.AMDock.project.mode == 1:
                if self.AMDock.project.bsd_mode_offtarget == 0:
                    mode = 'AUTOMATIC'
                elif self.AMDock.project.bsd_mode_offtarget == 1:
                    mode = 'CENTERED_ON_RESIDUE(S)'
                elif self.AMDock.project.bsd_mode_offtarget == 2:
                    mode = 'CENTERED_ON_HETERO'
                else:
                    mode = 'USER-DEFINED_BOX'

                self.AMDock.output2file.out2file('AMDOCK: O_BOX_MODE'.ljust(24) + '%s\n' % mode)
                if self.AMDock.project.bsd_mode_offtarget in [2, 3]:
                    self.AMDock.output2file.out2file(
                        'AMDOCK: OFF-TARGET_BOX'.ljust(24) + 'CENTER: {:7.02f} {:7.02f} {:7.02f} SIZE: {:2d} {:2d} '
                                                             '{:2d}\n'.format(float(self.grid_centerB[0]),
                                                                              float(self.grid_centerB[1]),
                                                                              float(self.grid_centerB[2]),
                                                                              self.sizeB[0], self.sizeB[1],
                                                                              self.sizeB[2]))
                else:
                    for fill in self.AMDock.offtarget.fill_list:
                        self.AMDock.output2file.out2file(
                            'AMDOCK: OFF-TARGET_BOX'.ljust(24) + 'FILL: {:02d} CENTER: {:7.02f} {:7.02f} {:7.02f} '
                                                                 'SIZE: {:2d} {:2d} {:2d}\n'.format(
                                fill, self.AMDock.offtarget.fill_list[fill][2][0],
                                self.AMDock.offtarget.fill_list[fill][2][1],
                                self.AMDock.offtarget.fill_list[fill][2][2], self.sizeB[0], self.sizeB[1],
                                self.sizeB[2]))

        # results section
        self.AMDock.output2file.out2file('AMDOCK: RESULT'.ljust(24) + (56 * '-' + '\n'))
        if self.AMDock.project.bsd_mode_target == 0:
            self.AMDock.output2file.out2file('AMDOCK: RESULT_NOTE'.ljust(24) + 'EACH POSE IS THE BEST DOCKING RESULT '
                                                                               'FOR EACH BINDING\n')
            self.AMDock.output2file.out2file('AMDOCK: RESULT_NOTE'.ljust(24) + 'SITE PREDICTED BY AUTLIGAND (SEE '
                                                                               'MANUAL) \n')
        self.AMDock.output2file.out2file(
            ' ______________________________________________________________________________ \n'
            '|                                                                              |\n'
            '|' + (' RESULT FOR TARGET: %s' % self.AMDock.target.name).ljust(78) + '|\n'
                                                                                   '|______________________________________________________________________________|\n'
                                                                                   '|               |                |              |               |              |\n'
                                                                                   '|     POSES     |    AFFINITY    | ESTIMATED Ki |    Ki UNITS   |   LIGAND     |\n'
                                                                                   '|               |   (KCAL/MOL)   |              |               |  EFFICIENCY  |\n'
                                                                                   '|_______________|________________|______________|_______________|______________|\n')
        self.AMDock.output2file.out2file(self.result2out)  # added all result in table form
        self.AMDock.output2file.out2file(
            '|_______________|________________|______________|_______________|______________|\n\n')
        if self.AMDock.project.mode == 1:
            if self.AMDock.project.bsd_mode_offtarget == 0:
                self.AMDock.output2file.out2file('AMDOCK: RESULT_NOTE'.ljust(24) + 'EACH POSE IS THE BEST DOCKING '
                                                                                   'RESULT FOR EACH BINDING\n')
                self.AMDock.output2file.out2file('AMDOCK: RESULT_NOTE'.ljust(24) + 'SITE PREDICTED BY AUTLIGAND (SEE '
                                                                                   'MANUAL) \n')
            self.AMDock.output2file.out2file(
                ' ______________________________________________________________________________ \n'
                '|                                                                              |\n'
                '|' + (' RESULT FOR OFF-TARGET: %s' % self.AMDock.offtarget.name).ljust(78) + '|\n'
                                                                                              '|______________________________________________________________________________|\n'
                                                                                              '|               |                |              |               |              |\n'
                                                                                              '|     POSES     |    AFFINITY    | ESTIMATED Ki |    Ki UNITS   |   LIGAND     |\n'
                                                                                              '|               |   (KCAL/MOL)   |              |               |  EFFICIENCY  |\n'
                                                                                              '|_______________|________________|______________|_______________|______________|\n')
            self.AMDock.output2file.out2file(self.result2outB)  # added all result in table form
            self.AMDock.output2file.out2file(
                '|_______________|________________|______________|_______________|______________|\n\n')
            if self.AMDock.project.bsd_mode_offtarget != 0 and self.AMDock.project.bsd_mode_target != 0:
                self.AMDock.output2file.out2file('AMDOCK: SELECTIVITY'.ljust(24) + 'Using only the best pose '
                                                                                   '(smallest energy)\n')
                self.AMDock.output2file.out2file('AMDOCK: SELEC_NOTE'.ljust(24) + 'EXP( [OFF-TARGET  -  TARGET] / RT ) '
                                                                                  '=  '
                                                                                  'SELECTIVITY\n')
                self.AMDock.output2file.out2file('AMDOCK: SELEC_VALUE'.ljust(24) + 'EXP( [' + ('{:10.02f}'.format(
                    self.resultsB[0][1])).center(10) + '  -  ' + ('{:6.02f}]'.format(self.results[0][1])).center(6)
                                                 + ' / RT ) =  ' + '{:11.02f}'.format(
                    self.AMDock.result_tab.selectivity_value))
        self.AMDock.output2file.conclude()

    def go_scoring(self):
        self.AMDock.result_tab.import_text.setText(self.AMDock.project.output)
        self.AMDock.statusbar.showMessage(" Go to Results Analysis", 2000)
        self.AMDock.main_window.setTabEnabled(2, True)
        self.AMDock.main_window.setCurrentIndex(2)
        self.AMDock.main_window.setTabEnabled(1, False)
        self.AMDock.main_window.setTabEnabled(0, False)
        os.chdir(self.AMDock.project.results)
        self.AMDock.result_tab.prot_label.setText('Target: %s' % self.AMDock.target.name)
        self.AMDock.result_tab.result_table.setRowCount(1)
        self.scoring_re = Result_Analysis(self.AMDock.docking_program, self.AMDock.target, self.AMDock.ligand)
        self.results = self.scoring_re.result2table(self.AMDock.target.score, True)
        self.result2out = ''
        f = 0
        for x in self.results:
            c = 0
            self.result2out += '|' + ('%s' % x[0]).center(15) + '|' + ('%s' % x[1]).center(16) + '|' + \
                               ('%s' % x[2]).center(14) + '|' + ('%s' % x[3]).center(15) + '|' + \
                               ('%s' % x[4]).center(14) + '|\n'
            for item in x:
                item_table = QTableWidgetItem(str(item))
                item_table.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.AMDock.result_tab.result_table.setItem(f, c, item_table)
                self.AMDock.result_tab.result_table.item(f, c).setTextAlignment(
                    Qt.AlignHCenter | Qt.AlignVCenter)
                if c == 4:
                    item_v = float(item)
                    if item_v <= -0.3:
                        self.AMDock.result_tab.result_table.item(f, c).setBackground(
                            QColor(0, 255, 128, 200))
                c += 1
            f += 1
        selection_model = self.AMDock.result_tab.result_table.selectionModel()
        selection_model.select(self.AMDock.result_tab.result_table.model().index(0, 0),
                               QItemSelectionModel.ClearAndSelect)
        self.amdock_output_file()
        amdock_file = open(self.AMDock.project.output)
        for line in amdock_file:
            line = line.strip('\n')
            self.AMDock.result_tab.rfile_show.textedit.append(line)
        amdock_file.close()

    def scoring(self):
        '''scoring'''
        queue = Queue()
        if self.AMDock.docking_program == 'AutoDock Vina':
            pass
        elif self.AMDock.docking_program == 'AutoDock4':
            protein_gpf = str(self.AMDock.target.pdbqt.split('.')[0] + '.gpf')
            protein_dlg = str(self.AMDock.target.pdbqt.split('.')[0] + '.dlg')
            protein_dpf = str(self.AMDock.target.pdbqt.split('.')[0] + '.dpf')

            prepare_gpf4_arg = [self.AMDock.prepare_gpf4_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                self.AMDock.target.pdbqt, '-f', self.AMDock.gd, '-p', 'spacing=%.3f' %
                                self.AMDock.spacing_autodock, '-p', 'npts=%d,%d,%d' % (
                                    self.size[0] / self.AMDock.spacing_autodock,
                                    self.size[1] / self.AMDock.spacing_autodock,
                                    self.size[2] / self.AMDock.spacing_autodock)]
            if self.AMDock.para_file:
                prepare_gpf4_arg = prepare_gpf4_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]

            self.prepare_gpf4 = {'Prepare_gpf4': [self.AMDock.this_python, prepare_gpf4_arg]}
            autogrid_arg = ['-p', protein_gpf]
            self.autogrid4 = {'AutoGrid4': [self.AMDock.autogrid, autogrid_arg]}
            prepare_dpf_arg = [self.AMDock.prepare_dpf_py, '-l', str(self.AMDock.ligand_pdbqt), '-r',
                               str(self.AMDock.target.pdbqt), '-e']
            if self.AMDock.para_file:
                prepare_dpf_arg = prepare_dpf_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]
            self.prepare_dpf4 = {'Prepare_dpf4': [self.AMDock.this_python, prepare_dpf_arg]}
            self.autodock_dlg = str(self.AMDock.ligand_pdbqt.split('.')[0] + '_' + protein_dlg)
            autodock_arg = ['-p', str(self.AMDock.ligand_pdbqt.split('.')[0] + '_' + protein_dpf), '-l',
                            os.path.join(self.AMDock.project.results,
                                         self.AMDock.ligand.name + '_' + self.AMDock.target.name + '_score.log')]
            self.autodock = {'AutoDock4': [self.AMDock.autodock, autodock_arg]}
            self.list_process = [self.prepare_gpf4, self.autogrid4, self.prepare_dpf4, self.autodock]
            for process in self.list_process:
                self.queue.put(process)
        else:

            protein_TZ = str(self.AMDock.target.pdbqt.split('.')[0] + '_TZ.pdbqt')
            protein_gpf = str(self.AMDock.target.pdbqt.split('.')[0] + '_TZ.gpf')
            protein_dlg = str(self.AMDock.target.pdbqt.split('.')[0] + '_TZ.dlg')
            protein_dpf = str(self.AMDock.target.pdbqt.split('.')[0] + '_TZ.dpf')
            pseudozn_arg = [self.AMDock.zinc_pseudo_py, '-r', str(self.AMDock.target.pdbqt)]
            self.pseudozn = {'PseudoZn': [self.AMDock.this_python, pseudozn_arg]}
            prepare_gpf4zn_arg = [self.AMDock.prepare_gpf4zn_py, '-l', str(self.AMDock.ligand_pdbqt), '-r',
                                  protein_TZ, '-f', self.AMDock.gd, '-p',
                                  'spacing=%.3f' % self.AMDock.spacing_autodock, '-p', 'npts=%d,%d,%d' %
                                  (self.size[0] / self.AMDock.spacing_autodock,
                                   self.size[1] / self.AMDock.spacing_autodock,
                                   self.size[2] / self.AMDock.spacing_autodock), '-p',
                                  ]
            if self.AMDock.para_file:
                prepare_gpf4zn_arg = prepare_gpf4zn_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]

            else:
                shutil.copy(self.AMDock.zn_ff, os.getcwd())
                prepare_gpf4zn_arg = prepare_gpf4zn_arg + ['-p', 'parameter_file=AD4Zn.dat']

            self.prepare_gpf4zn = {'Prepare_gpf4zn': [self.AMDock.this_python, prepare_gpf4zn_arg]}
            autogridzn_arg = ['-p', protein_gpf]
            self.autogrid4 = {'AutoGrid4': [self.AMDock.autogrid, autogridzn_arg]}
            prepare_dpfzn_arg = [self.AMDock.prepare_dpf_py, '-l', str(self.AMDock.ligand_pdbqt), '-r', protein_TZ,
                                 '-e']
            if self.AMDock.para_file:
                prepare_dpfzn_arg = prepare_dpfzn_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]
            else:
                prepare_dpfzn_arg = prepare_dpfzn_arg + ['-p', 'parameter_file=AD4Zn.dat']

            self.prepare_dfp4zn = {'Prepare_dpf4': [self.AMDock.this_python, prepare_dpfzn_arg]}
            self.autodock_dlg = str(self.AMDock.ligand_pdbqt.split('.')[0] + '_' + protein_dlg)
            autodockzn_arg = ['-p', str(self.AMDock.ligand_pdbqt.split('.')[0] + '_' + protein_dpf),
                              '-l', os.path.join(self.AMDock.project.results,
                                                 self.AMDock.ligand.name + '_' + self.AMDock.target.name + '_score.log')]
            self.autodockzn = {'AutoDock4ZN': [self.AMDock.autodock, autodockzn_arg]}
            self.list_process = [self.pseudozn, self.prepare_gpf4zn, self.autogrid4, self.prepare_dfp4zn,
                                 self.autodockzn]
            for process in self.list_process:
                self.queue.put(process)
        self.worker.init(self.queue, 'Scoring Process')
        self.worker.start_process()

    def stop_function(self):
        if self.AMDock.state:
            self.stop_opt = stop_warning(self)
            if self.stop_opt == QMessageBox.Yes:
                self.W.force_finished()

    def process_stoped(self, state, queue):
        if state:
            self.program_label.setText('Stopping process...')
        else:
            try:
                self.timerAD.stop()  # stop timer for AutoDock
            except:
                pass
            self.program_label.setText('Stopping process... Done.')
            self.AMDock.log_widget.textedit.append(Ft('Stopping process... Done.').error())

    def start_docking_prog(self):

        self.need_grid = self.need_gridB = True
        queue = Queue()
        if self.AMDock.state == 2:
            msg = QMessageBox.critical(self.AMDock, 'Error', 'Other processes are running in the background. '
                                                             'Please wait for these to end.',
                                       QMessageBox.Ok)
            return
        elif self.AMDock.section in [-1, 0, 1]:
            if self.AMDock.project.mode == 2:
                pass
            else:
                msg = QMessageBox.critical(self.AMDock, 'Error', 'It seems that not all previous steps have been '
                                                                 'completed. Please do all the steps sequentially.',
                                           QMessageBox.Ok)
                return
        elif self.AMDock.section in [3]:
            msg = QMessageBox.warning(self.AMDock, 'Warning', 'This step was successfully completed previously.'
                                                              ' Do you want to repeat it?',
                                      QMessageBox.Yes | QMessageBox.No)
            if msg == QMessageBox.No:
                return

        if self.AMDock.docking_program == 'AutoDock Vina':
            if self.AMDock.project.mode == 2:
                queue.name = 4
                self.AMDock.target.score = os.path.join(self.AMDock.project.results,
                                                        self.AMDock.ligand.name + '_' + self.AMDock.target.name + '_score.log')
                vina_score = {'AutoDock Vina Scoring': [self.AMDock.vina_exec, ['--receptor', self.AMDock.target.pdbqt,
                                                                                '--ligand', self.AMDock.ligand.pdbqt,
                                                                                '--score_only', "--log",
                                                                                self.AMDock.target.score]]}
                queue.put(vina_score)
            else:
                queue.name = 3
                if self.AMDock.project.bsd_mode_target == 0:
                    for nfill in range(len(self.AMDock.target.fill_list)):
                        fill_info = PDBINFO('FILL_{}_{}out{:02d}.pdb'.format(self.AMDock.target.pdbqt_name,
                                                                             self.AMDock.ligand.ha * 6, nfill + 1))
                        if not fill_info.center:
                            msg = QMessageBox.warning(self.AMDock, 'Warning',
                                                      'This FILL no exist or is not possible to open '
                                                      'pdb file', QMessageBox.Ok)

                        vina_output = os.path.join(self.AMDock.project.results, self.AMDock.ligand.pdbqt_name + '_' +
                                                   self.AMDock.target.name + '_out{:02d}.pdbqt'.format(
                            nfill + 1))
                        self.AMDock.target.vina_log = os.path.join(self.AMDock.project.results,
                                                                   self.AMDock.ligand.pdbqt_name + '_' +
                                                                   self.AMDock.target.name + '_out{}.log'.format(
                                                                       nfill + 1))
                        vina_arg = ['--receptor', self.AMDock.target.pdbqt, '--ligand', self.AMDock.ligand.pdbqt,
                                    '--center_x', '{}'.format(fill_info.center[0]), '--center_y', '{}'.format(
                                fill_info.center[1]), '--center_z', '{}'.format(fill_info.center[2]), '--size_x',
                                    '{}'.format(self.size[0]), '--size_y', '{}'.format(self.size[1]), '--size_z',
                                    '{}'.format(self.size[2]), '--cpu', str(self.AMDock.ncpu), '--num_modes', '1',
                                    '--exhaustiveness', str(self.AMDock.exhaustiveness), '--out',
                                    vina_output, "--log", self.AMDock.target.vina_log]
                        vina = {'AutoDock Vina': [self.AMDock.vina_exec, vina_arg]}
                        queue.put(vina)

                else:
                    self.AMDock.target.vina_output = os.path.join(self.AMDock.project.results,
                                                                  self.AMDock.ligand.pdbqt_name + '_' +
                                                                  self.AMDock.target.name + '_out.pdbqt')
                    self.AMDock.target.vina_log = os.path.join(self.AMDock.project.results,
                                                               self.AMDock.ligand.pdbqt_name + '_' +
                                                               self.AMDock.target.name + '_out.log')
                    vina_arg = ['--receptor', self.AMDock.target.pdbqt, '--ligand', self.AMDock.ligand.pdbqt,
                                '--center_x', '{}'.format(self.grid_center[0]), '--center_y',
                                '{}'.format(self.grid_center[1]), '--center_z', '{}'.format(self.grid_center[2]),
                                '--size_x', '{}'.format(self.size[0]), '--size_y', '{}'.format(self.size[1]),
                                '--size_z', '{}'.format(self.size[2]), '--cpu', str(self.AMDock.ncpu), '--num_modes',
                                str(self.AMDock.poses_vina), '--exhaustiveness', str(self.AMDock.exhaustiveness),
                                '--out', self.AMDock.target.vina_output, "--log", self.AMDock.target.vina_log]
                    vina = {'AutoDock Vina': [self.AMDock.vina_exec, vina_arg]}
                    queue.put(vina)
                if self.AMDock.project.mode == 1:
                    if self.AMDock.project.bsd_mode_offtarget == 0:
                        for nfill in range(len(self.AMDock.offtarget.fill_list)):
                            fill_info = PDBINFO('FILL_{}_{}out{:02d}.pdb'.format(self.AMDock.offtarget.pdbqt_name,
                                                                                 self.AMDock.ligand.ha * 6, nfill + 1))
                            if not fill_info.center:
                                msg = QMessageBox.warning(self.AMDock, 'Warning',
                                                          'This FILL no exist or is not possible to open '
                                                          'pdb file', QMessageBox.Ok)
                            vina_output = os.path.join(self.AMDock.project.results,
                                                       self.AMDock.ligand.pdbqt_name + '_' +
                                                       self.AMDock.offtarget.name +
                                                       '_out{:02d}.pdbqt'.format(nfill + 1))
                            self.AMDock.offtarget.vina_log = os.path.join(self.AMDock.project.results,
                                                                          self.AMDock.ligand.pdbqt_name + '_' +
                                                                          self.AMDock.offtarget.name + '_out{}.log'.format(
                                                                              nfill + 1))
                            vina_arg = ['--receptor', self.AMDock.offtarget.pdbqt, '--ligand', self.AMDock.ligand.pdbqt,
                                        '--center_x', '{}'.format(fill_info.center[0]), '--center_y', '{}'.format(
                                    fill_info.center[1]), '--center_z', '{}'.format(fill_info.center[2]), '--size_x',
                                        '{}'.format(self.size[0]), '--size_y', '{}'.format(self.size[1]), '--size_z',
                                        '{}'.format(self.size[2]), '--cpu', str(self.AMDock.ncpu), '--num_modes', '1',
                                        '--exhaustiveness', str(self.AMDock.exhaustiveness), '--out',
                                        vina_output, "--log", self.AMDock.offtarget.vina_log]
                            vina = {'AutoDock Vina': [self.AMDock.vina_exec, vina_arg]}
                            queue.put(vina)

                    else:
                        self.AMDock.offtarget.vina_output = os.path.join(self.AMDock.project.results,
                                                                         self.AMDock.ligand.pdbqt_name + '_' +
                                                                         self.AMDock.offtarget.name + '_out.pdbqt')
                        self.AMDock.offtarget.vina_log = os.path.join(self.AMDock.project.results,
                                                                      self.AMDock.ligand.pdbqt_name + '_' +
                                                                      self.AMDock.offtarget.name + '_out.log')
                        vina_argB = ['--receptor', self.AMDock.offtarget.pdbqt, '--ligand', self.AMDock.ligand.pdbqt,
                                     '--center_x', '{}'.format(self.grid_centerB[0]), '--center_y', '{}'.format(
                                self.grid_centerB[1]), '--center_z', '{}'.format(self.grid_centerB[2]), '--size_x',
                                     '{}'.format(self.size[0]), '--size_y', '{}'.format(self.size[0]), '--size_z',
                                     '{}'.format(self.size[2]), '--cpu', str(self.AMDock.ncpu), '--num_modes',
                                     str(self.AMDock.poses_vina), '--exhaustiveness', str(self.AMDock.exhaustiveness),
                                     '--out', self.AMDock.offtarget.vina_output, "--log",
                                     self.AMDock.offtarget.vina_log]
                        vinaB = {'AutoDock Vina B': [self.AMDock.vina_exec, vina_argB]}
                        queue.put(vinaB)

        elif self.AMDock.docking_program == 'AutoDock4':
            if self.AMDock.project.mode == 2:
                queue.name = 4
                self.AMDock.target.score = os.path.join(self.AMDock.project.results,
                                                        self.AMDock.ligand.name + '_' + self.AMDock.target.name + '_score.log')
                prepare_gpf4_arg = [self.AMDock.prepare_gpf4_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                    self.AMDock.target.pdbqt, '-p', 'spacing=%.3f' % self.AMDock.spacing_autodock, '-p',
                                    'npts=%d,%d,%d' % (self.size[0] / self.AMDock.spacing_autodock,
                                                       self.size[1] / self.AMDock.spacing_autodock, self.size[2] /
                                                       self.AMDock.spacing_autodock),
                                    '-p', 'gridcenter={0},{1},{2}'.format(*self.ligand_info.center)]
                if self.AMDock.para_file:
                    prepare_gpf4_arg = prepare_gpf4_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]
                prepare_gpf4 = {'Prepare_gpf4': [self.AMDock.this_python, prepare_gpf4_arg]}
                queue.put(prepare_gpf4)
                autogrid4 = {'AutoGrid4': [self.AMDock.autogrid, ['-p', self.AMDock.target.gpf]]}
                queue.put(autogrid4)
                prepare_dpf_arg = [self.AMDock.prepare_dpf_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                   self.AMDock.target.pdbqt, '-e']
                if self.AMDock.para_file:
                    prepare_dpf_arg = prepare_dpf_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]

                prepare_dpf4 = {'Prepare_dpf4': [self.AMDock.this_python, prepare_dpf_arg]}
                queue.put(prepare_dpf4)
                autodock_arg = ['-p', self.AMDock.ligand.pdbqt_name + '_' + self.AMDock.target.dpf, '-l',
                                self.AMDock.target.score]
                autodock = {'AutoDock4': [self.AMDock.autodock, autodock_arg]}
                queue.put(autodock)
            else:
                queue.name = 3
                if self.AMDock.project.bsd_mode_target == 0:
                    for nfill in range(len(self.AMDock.target.fill_list)):
                        fill_info = PDBINFO('FILL_{}_{}out{:02d}.pdb'.format(self.AMDock.target.pdbqt_name,
                                                                             self.AMDock.ligand.ha * 6, nfill + 1))
                        if not fill_info.center:
                            msg = QMessageBox.warning(self.AMDock, 'Warning', 'This FILL no exist or is not '
                                                                              'possible to open pdb file',
                                                      QMessageBox.Ok)
                        ad4_output = os.path.join(self.AMDock.project.results, self.AMDock.ligand.pdbqt_name + '_' +
                                                  self.AMDock.target.name + '_{:02d}.dlg'.format(
                            nfill + 1))
                        prepare_gpf4_arg = [self.AMDock.prepare_gpf4_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                            self.AMDock.target.pdbqt, '-p', 'spacing=%.3f' %
                                            self.AMDock.spacing_autodock, '-p', 'npts=%d,%d,%d' % (
                                                self.size[0] / self.AMDock.spacing_autodock,
                                                self.size[1] / self.AMDock.spacing_autodock,
                                                self.size[2] / self.AMDock.spacing_autodock),
                                            '-p', 'gridcenter={0},{1},{2}'.format(*fill_info.center)]
                        if self.AMDock.para_file:
                            prepare_gpf4_arg = prepare_gpf4_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]
                        prepare_gpf4 = {'Prepare_gpf4': [self.AMDock.this_python, prepare_gpf4_arg]}
                        queue.put(prepare_gpf4)
                        autogrid4 = {'AutoGrid4': [self.AMDock.autogrid, ['-p', self.AMDock.target.gpf]]}
                        queue.put(autogrid4)
                        prepare_dpf_arg = [self.AMDock.prepare_dpf_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                           self.AMDock.target.pdbqt, '-p', 'rmstol=%s' % self.AMDock.rmsdtol, '-p',
                                           'ga_num_evals=%s' % self.AMDock.ga_num_eval, '-p',
                                           'ga_run=%s' % self.AMDock.ga_run]
                        if self.AMDock.para_file:
                            prepare_dpf_arg = prepare_dpf_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]

                        prepare_dpf4 = {'Prepare_dpf4': [self.AMDock.this_python, prepare_dpf_arg]}
                        queue.put(prepare_dpf4)
                        autodock_arg = ['-p', self.AMDock.ligand.pdbqt_name + '_' + self.AMDock.target.dpf, '-l',
                                        ad4_output]
                        autodock = {'AutoDock4': [self.AMDock.autodock, autodock_arg]}
                        queue.put(autodock)

                else:
                    self.AMDock.target.ad4_output = os.path.join(self.AMDock.project.results,
                                                                 self.AMDock.ligand.pdbqt_name + '_' +
                                                                 self.AMDock.target.name + '_out.dlg')
                    prepare_gpf4_arg = [self.AMDock.prepare_gpf4_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                        self.AMDock.target.pdbqt, '-p', 'spacing=%.3f' % self.AMDock.spacing_autodock,
                                        '-p',
                                        'npts=%d,%d,%d' % (self.size[0] / self.AMDock.spacing_autodock, self.size[1] /
                                                           self.AMDock.spacing_autodock, self.size[2] /
                                                           self.AMDock.spacing_autodock), '-p', 'gridcenter={0},{1},'
                                                                                                '{2}'.format(
                            *self.grid_center)]
                    if self.AMDock.para_file:
                        prepare_gpf4_arg = prepare_gpf4_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]
                    prepare_gpf4 = {'Prepare_gpf4': [self.AMDock.this_python, prepare_gpf4_arg]}
                    queue.put(prepare_gpf4)
                    autogrid4 = {'AutoGrid4': [self.AMDock.autogrid, ['-p', self.AMDock.target.gpf]]}
                    queue.put(autogrid4)
                    prepare_dpf_arg = [self.AMDock.prepare_dpf_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                       self.AMDock.target.pdbqt, '-p', 'rmstol=%s' % self.AMDock.rmsdtol, '-p',
                                       'ga_num_evals=%s' % self.AMDock.ga_num_eval, '-p',
                                       'ga_run=%s' % self.AMDock.ga_run]
                    if self.AMDock.para_file:
                        prepare_dpf_arg = prepare_dpf_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]

                    prepare_dpf4 = {'Prepare_dpf4': [self.AMDock.this_python, prepare_dpf_arg]}
                    queue.put(prepare_dpf4)
                    autodock_arg = ['-p', self.AMDock.ligand.pdbqt_name + '_' + self.AMDock.target.dpf, '-l',
                                    self.AMDock.target.ad4_output]
                    autodock = {'AutoDock4': [self.AMDock.autodock, autodock_arg]}
                    queue.put(autodock)

                if self.AMDock.project.mode == 1:
                    if self.AMDock.project.bsd_mode_offtarget == 0:
                        for nfill in range(len(self.AMDock.offtarget.fill_list)):
                            fill_info = PDBINFO('FILL_{}_{}out{:02d}.pdb'.format(self.AMDock.offtarget.pdbqt_name,
                                                                                 self.AMDock.ligand.ha * 6, nfill + 1))
                            if not fill_info.center:
                                msg = QMessageBox.warning(self.AMDock, 'Warning',
                                                          'This FILL no exist or is not possible to open '
                                                          'pdb file', QMessageBox.Ok)
                            ad4_output = os.path.join(self.AMDock.project.results, self.AMDock.ligand.pdbqt_name + '_' +
                                                      self.AMDock.offtarget.name +
                                                      '_out{:02d}.dlg'.format(nfill + 1))
                            prepare_gpf4_argB = [self.AMDock.prepare_gpf4_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                                 self.AMDock.offtarget.pdbqt, '-p',
                                                 'spacing=%.3f' % self.AMDock.spacing_autodock, '-p',
                                                 'npts=%d,%d,%d' % (
                                                     self.size[0] / self.AMDock.spacing_autodock, self.size[1] /
                                                     self.AMDock.spacing_autodock, self.size[2] /
                                                     self.AMDock.spacing_autodock), '-p', 'gridcenter={0},{1},'
                                                                                          '{2}'.format(
                                    *fill_info.center)]
                            if self.AMDock.para_file:
                                prepare_gpf4_argB = prepare_gpf4_argB + ['-p',
                                                                         'parameter_file=%s' % self.AMDock.para_file]
                            prepare_gpf4B = {'Prepare_gpf4 B': [self.AMDock.this_python, prepare_gpf4_argB]}
                            queue.put(prepare_gpf4B)

                            autogrid4B = {'AutoGrid4 B': [self.AMDock.autogrid, ['-p', self.AMDock.offtarget.gpf]]}
                            queue.put(autogrid4B)

                            prepare_dpf_argB = [self.AMDock.prepare_dpf_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                                self.AMDock.offtarget.pdbqt,
                                                '-p', 'rmstol=%s' % self.AMDock.rmsdtol, '-p',
                                                'ga_num_evals=%s' % self.AMDock.ga_num_eval,
                                                '-p', 'ga_run=%s' % self.AMDock.ga_run]
                            if self.AMDock.para_file:
                                prepare_dpf_argB = prepare_dpf_argB + ['-p', 'parameter_file=%s' %
                                                                       self.AMDock.para_file]

                            prepare_dpf4B = {'Prepare_dpf4 B': [self.AMDock.this_python, prepare_dpf_argB]}
                            queue.put(prepare_dpf4B)

                            autodock_argB = ['-p', self.AMDock.ligand.pdbqt_name + '_' + self.AMDock.offtarget.dpf,
                                             '-l', ad4_output]
                            autodockB = {'AutoDock4 B': [self.AMDock.autodock, autodock_argB]}
                            queue.put(autodockB)
                    else:
                        self.AMDock.offtarget.ad4_output = os.path.join(self.AMDock.project.results,
                                                                        self.AMDock.ligand.pdbqt_name + '_' +
                                                                        self.AMDock.offtarget.name + '_out.dlg')
                        prepare_gpf4_argB = [self.AMDock.prepare_gpf4_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                             self.AMDock.offtarget.pdbqt, '-p',
                                             'spacing=%.3f' % self.AMDock.spacing_autodock, '-p',
                                             'npts=%d,%d,%d' % (
                                                 self.size[0] / self.AMDock.spacing_autodock, self.size[1] /
                                                 self.AMDock.spacing_autodock, self.size[2] /
                                                 self.AMDock.spacing_autodock), '-p', 'gridcenter={0},{1},'
                                                                                      '{2}'.format(*self.grid_centerB)]
                        if self.AMDock.para_file:
                            prepare_gpf4_argB = prepare_gpf4_argB + ['-p', 'parameter_file=%s' % self.AMDock.para_file]
                        prepare_gpf4B = {'Prepare_gpf4 B': [self.AMDock.this_python, prepare_gpf4_argB]}
                        queue.put(prepare_gpf4B)

                        autogrid4B = {'AutoGrid4 B': [self.AMDock.autogrid, ['-p', self.AMDock.offtarget.gpf]]}
                        queue.put(autogrid4B)

                        prepare_dpf_argB = [self.AMDock.prepare_dpf_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                            self.AMDock.offtarget.pdbqt,
                                            '-p', 'rmstol=%s' % self.AMDock.rmsdtol, '-p',
                                            'ga_num_evals=%s' % self.AMDock.ga_num_eval,
                                            '-p', 'ga_run=%s' % self.AMDock.ga_run]
                        if self.AMDock.para_file:
                            prepare_dpf_argB = prepare_dpf_argB + ['-p', 'parameter_file=%s' % self.AMDock.para_file]

                        prepare_dpf4B = {'Prepare_dpf4 B': [self.AMDock.this_python, prepare_dpf_argB]}
                        queue.put(prepare_dpf4B)

                        autodock_argB = ['-p', self.AMDock.ligand.pdbqt_name + '_' + self.AMDock.offtarget.dpf, '-l',
                                         self.AMDock.offtarget.ad4_output]
                        autodockB = {'AutoDock4 B': [self.AMDock.autodock, autodock_argB]}
                        queue.put(autodockB)

        elif self.AMDock.docking_program == 'AutoDockZn':
            if not self.AMDock.para_file:
                shutil.copy(self.AMDock.zn_ff, os.getcwd())
            self.AMDock.target.score = os.path.join(self.AMDock.project.results,
                                                    self.AMDock.ligand.name + '_' + self.AMDock.target.name + '_score.log')
            if self.AMDock.project.mode == 2:
                queue.name = 4
                pseudozn = {'PseudoZn': [self.AMDock.this_python, [self.AMDock.zinc_pseudo_py, '-r',
                                                                   self.AMDock.target.pdbqt]]}
                queue.put(pseudozn)
                prepare_gpf4zn_arg = [self.AMDock.prepare_gpf4zn_py, '-l', str(self.AMDock.ligand.pdbqt), '-r',
                                      self.AMDock.target.tzpdbqt, '-p', 'spacing=%.3f' % self.AMDock.spacing_autodock,
                                      '-p',
                                      'npts=%d,%d,%d' % (self.size[1] / self.AMDock.spacing_autodock, self.size[1] /
                                                         self.AMDock.spacing_autodock,
                                                         self.size[2] / self.AMDock.spacing_autodock), '-p',
                                      'gridcenter={0},{1},{2}'.format(*self.ligand_info.center), '-p',
                                      ]
                if self.AMDock.para_file:
                    prepare_gpf4zn_arg = prepare_gpf4zn_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]
                else:
                    prepare_gpf4zn_arg = prepare_gpf4zn_arg + ['-p', 'parameter_file=AD4Zn.dat']

                prepare_gpf4zn = {'Prepare_gpf4zn': [self.AMDock.this_python, prepare_gpf4zn_arg]}
                queue.put(prepare_gpf4zn)
                autogrid4 = {'AutoGrid4': [self.AMDock.autogrid, ['-p', self.AMDock.target.tzgpf]]}
                queue.put(autogrid4)
                prepare_dpfzn_arg = [self.AMDock.prepare_dpf_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                     self.AMDock.target.tzpdbqt, '-e']
                if self.AMDock.para_file:
                    prepare_dpfzn_arg = prepare_dpfzn_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]
                else:
                    prepare_dpfzn_arg = prepare_dpfzn_arg + ['-p', 'parameter_file=AD4Zn.dat']
                prepare_dpf4 = {'Prepare_dpf4': [self.AMDock.this_python, prepare_dpfzn_arg]}

                queue.put(prepare_dpf4)
                autodockzn_arg = ['-p', self.AMDock.ligand.pdbqt_name + '_' + self.AMDock.target.tzdpf, '-l',
                                  self.AMDock.target.score]
                autodockzn = {'AutoDock4ZN': [self.AMDock.autodock, autodockzn_arg]}
                queue.put(autodockzn)
            else:
                queue.name = 3
                if self.AMDock.project.bsd_mode_target == 0:
                    for nfill in range(len(self.AMDock.target.fill_list)):
                        fill_info = PDBINFO('FILL_{}_{}out{:02d}.pdb'.format(self.AMDock.target.pdbqt_name,
                                                                             self.AMDock.ligand.ha * 6, nfill + 1))
                        if not fill_info.center:
                            msg = QMessageBox.warning(self.AMDock, 'Warning', 'This FILL no exist or is not '
                                                                              'possible to open pdb file',
                                                      QMessageBox.Ok)
                        ad4_output = os.path.join(self.AMDock.project.results, self.AMDock.ligand.pdbqt_name + '_' +
                                                  self.AMDock.target.name + '_{:02d}.dlg'.format(
                            nfill + 1))
                        pseudozn = {'PseudoZn': [self.AMDock.this_python, [self.AMDock.zinc_pseudo_py, '-r',
                                                                           self.AMDock.target.pdbqt]]}
                        queue.put(pseudozn)
                        prepare_gpf4zn_arg = [self.AMDock.prepare_gpf4zn_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                              self.AMDock.target.tzpdbqt, '-p', 'spacing=%.3f' %
                                              self.AMDock.spacing_autodock, '-p', 'npts=%d,%d,%d' %
                                              (self.size[0] / self.AMDock.spacing_autodock,
                                               self.size[1] / self.AMDock.spacing_autodock,
                                               self.size[2] / self.AMDock.spacing_autodock),
                                              '-p', 'gridcenter={0},{1},{2}'.format(*fill_info.center),
                                              '-p', 'parameter_file=AD4Zn.dat']
                        if self.AMDock.para_file:
                            prepare_gpf4zn_arg = prepare_gpf4zn_arg + ['-p', 'parameter_file=%s' %
                                                                       self.AMDock.para_file]
                        else:
                            prepare_gpf4zn_arg = prepare_gpf4zn_arg + ['-p', 'parameter_file=AD4Zn.dat']

                        prepare_gpf4zn = {'Prepare_gpf4zn': [self.AMDock.this_python, prepare_gpf4zn_arg]}
                        queue.put(prepare_gpf4zn)
                        autogrid4 = {'AutoGrid4': [self.AMDock.autogrid, ['-p', self.AMDock.target.tzgpf]]}
                        queue.put(autogrid4)
                        prepare_dpfzn_arg = [self.AMDock.prepare_dpf_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                             self.AMDock.target.tzpdbqt, '-p', 'rmstol=%s' % self.AMDock.rmsdtol, '-p',
                                             'ga_num_evals=%s' % self.AMDock.ga_num_eval, '-p',
                                             'ga_run=%s' % self.AMDock.ga_run]
                        if self.AMDock.para_file:
                            prepare_dpfzn_arg = prepare_dpfzn_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]
                        else:
                            prepare_dpfzn_arg = prepare_dpfzn_arg + ['-p', 'parameter_file=AD4Zn.dat']
                        prepare_dpf4 = {'Prepare_dpf4': [self.AMDock.this_python, prepare_dpfzn_arg]}
                        queue.put(prepare_dpf4)
                        autodockzn_arg = ['-p', self.AMDock.ligand.pdbqt_name + '_' + self.AMDock.target.tzdpf, '-l',
                                          ad4_output]
                        autodockzn = {'AutoDock4ZN': [self.AMDock.autodock, autodockzn_arg]}
                        queue.put(autodockzn)

                else:
                    self.AMDock.target.ad4_output = os.path.join(self.AMDock.project.results,
                                                                 self.AMDock.ligand.pdbqt_name + '_' +
                                                                 self.AMDock.target.name + '_out.dlg')
                    pseudozn = {'PseudoZn': [self.AMDock.this_python, [self.AMDock.zinc_pseudo_py, '-r',
                                                                       self.AMDock.target.pdbqt]]}
                    queue.put(pseudozn)
                    prepare_gpf4zn_arg = [self.AMDock.prepare_gpf4zn_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                          self.AMDock.target.tzpdbqt, '-p',
                                          'spacing=%.3f' % self.AMDock.spacing_autodock, '-p',
                                          'npts=%d,%d,%d' % (self.size[0] / self.AMDock.spacing_autodock, self.size[1] /
                                                             self.AMDock.spacing_autodock,
                                                             self.size[2] / self.AMDock.spacing_autodock),
                                          '-p', 'gridcenter={0},{1},''{2}'.format(*self.grid_center)]
                    if self.AMDock.para_file:
                        prepare_gpf4zn_arg = prepare_gpf4zn_arg + ['-p', 'parameter_file=%s' %
                                                                   self.AMDock.para_file]
                    else:
                        prepare_gpf4zn_arg = prepare_gpf4zn_arg + ['-p', 'parameter_file=AD4Zn.dat']

                    prepare_gpf4zn = {'Prepare_gpf4zn': [self.AMDock.this_python, prepare_gpf4zn_arg]}
                    queue.put(prepare_gpf4zn)
                    autogrid4 = {'AutoGrid4': [self.AMDock.autogrid, ['-p', self.AMDock.target.tzgpf]]}
                    queue.put(autogrid4)
                    prepare_dpfzn_arg = [self.AMDock.prepare_dpf_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                         self.AMDock.target.tzpdbqt, '-p', 'rmstol=%s' % self.AMDock.rmsdtol, '-p',
                                         'ga_num_evals=%s' % self.AMDock.ga_num_eval, '-p',
                                         'ga_run=%s' % self.AMDock.ga_run]
                    if self.AMDock.para_file:
                        prepare_dpfzn_arg = prepare_dpfzn_arg + ['-p', 'parameter_file=%s' % self.AMDock.para_file]
                    else:
                        prepare_dpfzn_arg = prepare_dpfzn_arg + ['-p', 'parameter_file=AD4Zn.dat']
                    prepare_dpf4 = {'Prepare_dpf4': [self.AMDock.this_python, prepare_dpfzn_arg]}
                    queue.put(prepare_dpf4)
                    autodockzn_arg = ['-p', self.AMDock.ligand.pdbqt_name + '_' + self.AMDock.target.tzdpf, '-l',
                                      self.AMDock.target.ad4_output]
                    autodockzn = {'AutoDock4ZN': [self.AMDock.autodock, autodockzn_arg]}
                    queue.put(autodockzn)

                if self.AMDock.project.mode == 1:
                    if self.AMDock.project.bsd_mode_offtarget == 0:
                        for nfill in range(len(self.AMDock.offtarget.fill_list)):
                            fill_info = PDBINFO('FILL_{}_{}out{:02d}.pdb'.format(self.AMDock.offtarget.pdbqt_name,
                                                                                 self.AMDock.ligand.ha * 6, nfill + 1))
                            if not fill_info.center:
                                msg = QMessageBox.warning(self.AMDock, 'Warning',
                                                          'This FILL no exist or is not possible to open '
                                                          'pdb file', QMessageBox.Ok)
                            ad4_output = os.path.join(self.AMDock.project.results, self.AMDock.ligand.pdbqt_name + '_' +
                                                      self.AMDock.offtarget.name +
                                                      '_out{:02d}.dlg'.format(nfill + 1))
                            pseudoznB = {'PseudoZn B': [self.AMDock.this_python, [self.AMDock.zinc_pseudo_py, '-r',
                                                                                  self.AMDock.offtarget.pdbqt]]}
                            queue.put(pseudoznB)

                            prepare_gpf4zn_argB = [self.AMDock.prepare_gpf4zn_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                                   self.AMDock.offtarget.tzpdbqt, '-p', 'spacing=%.3f' %
                                                   self.AMDock.spacing_autodock, '-p', 'npts=%d,%d,%d' % (
                                                       self.size[0] / self.AMDock.spacing_autodock,
                                                       self.size[1] / self.AMDock.spacing_autodock,
                                                       self.size[2] / self.AMDock.spacing_autodock),
                                                   '-p', 'gridcenter={0},{1},{2}'.format(*fill_info.center)]
                            if self.AMDock.para_file:
                                prepare_gpf4zn_argB = prepare_gpf4zn_argB + ['-p', 'parameter_file=%s' %
                                                                             self.AMDock.para_file]
                            else:
                                prepare_gpf4zn_argB = prepare_gpf4zn_argB + ['-p', 'parameter_file=AD4Zn.dat']

                            prepare_gpf4znB = {'Prepare_gpf4zn B': [self.AMDock.this_python, prepare_gpf4zn_argB]}
                            queue.put(prepare_gpf4znB)

                            autogrid4B = {'AutoGrid4 B': [self.AMDock.autogrid, ['-p', self.AMDock.offtarget.tzgpf]]}
                            queue.put(autogrid4B)

                            prepare_dpfzn_argB = [self.AMDock.prepare_dpf_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                                  self.AMDock.offtarget.tzpdbqt,
                                                  '-p', 'rmstol=%s' % self.AMDock.rmsdtol, '-p',
                                                  'ga_num_evals=%s' % self.AMDock.ga_num_eval,
                                                  '-p', 'ga_run=%s' % self.AMDock.ga_run]
                            if self.AMDock.para_file:
                                prepare_dpfzn_argB = prepare_dpfzn_argB + ['-p', 'parameter_file=%s' %
                                                                           self.AMDock.para_file]
                            else:
                                prepare_dpfzn_argB = prepare_dpfzn_argB + ['-p', 'parameter_file=AD4Zn.dat']
                            prepare_dpf4B = {'Prepare_dpf4 B': [self.AMDock.this_python, prepare_dpfzn_argB]}
                            queue.put(prepare_dpf4B)

                            autodockzn_argB = ['-p', self.AMDock.ligand.pdbqt_name + '_' + self.AMDock.offtarget.tzdpf,
                                               '-l', ad4_output]
                            autodockznB = {'AutoDock4ZN B': [self.AMDock.autodock, autodockzn_argB]}
                            queue.put(autodockznB)
                    else:
                        self.AMDock.offtarget.ad4_output = os.path.join(self.AMDock.project.results,
                                                                        self.AMDock.ligand.pdbqt_name + '_' +
                                                                        self.AMDock.offtarget.name + '_out.dlg')
                        pseudoznB = {'PseudoZn B': [self.AMDock.this_python, [self.AMDock.zinc_pseudo_py, '-r',
                                                                              self.AMDock.offtarget.pdbqt]]}
                        queue.put(pseudoznB)

                        prepare_gpf4zn_argB = [self.AMDock.prepare_gpf4zn_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                               self.AMDock.offtarget.tzpdbqt, '-p',
                                               'spacing=%.3f' % self.AMDock.spacing_autodock, '-p',
                                               'npts=%d,%d,%d' % (
                                                   self.size[0] / self.AMDock.spacing_autodock, self.size[1] /
                                                   self.AMDock.spacing_autodock,
                                                   self.size[2] / self.AMDock.spacing_autodock),
                                               '-p', 'gridcenter={0},{1},{2}'.format(*self.grid_centerB)]
                        if self.AMDock.para_file:
                            prepare_gpf4zn_argB = prepare_gpf4zn_argB + ['-p', 'parameter_file=%s' %
                                                                         self.AMDock.para_file]
                        else:
                            prepare_gpf4zn_argB = prepare_gpf4zn_argB + ['-p', 'parameter_file=AD4Zn.dat']

                        prepare_gpf4znB = {'Prepare_gpf4zn B': [self.AMDock.this_python, prepare_gpf4zn_argB]}
                        queue.put(prepare_gpf4znB)

                        autogrid4B = {'AutoGrid4 B': [self.AMDock.autogrid, ['-p', self.AMDock.offtarget.tzgpf]]}
                        queue.put(autogrid4B)

                        prepare_dpfzn_argB = [self.AMDock.prepare_dpf_py, '-l', self.AMDock.ligand.pdbqt, '-r',
                                              self.AMDock.offtarget.tzpdbqt,
                                              '-p', 'rmstol=%s' % self.AMDock.rmsdtol, '-p',
                                              'ga_num_evals=%s' % self.AMDock.ga_num_eval,
                                              '-p', 'ga_run=%s' % self.AMDock.ga_run]
                        if self.AMDock.para_file:
                            prepare_dpfzn_argB = prepare_dpfzn_argB + ['-p', 'parameter_file=%s' %
                                                                       self.AMDock.para_file]
                        else:
                            prepare_dpfzn_argB = prepare_dpfzn_argB + ['-p', 'parameter_file=AD4Zn.dat']
                        prepare_dpf4B = {'Prepare_dpf4 B': [self.AMDock.this_python, prepare_dpfzn_argB]}
                        queue.put(prepare_dpf4B)

                        autodockzn_argB = ['-p', self.AMDock.ligand.pdbqt_name + '_' + self.AMDock.offtarget.tzdpf,
                                           '-l',
                                           self.AMDock.offtarget.ad4_output]
                        autodockznB = {'AutoDock4ZN B': [self.AMDock.autodock, autodockzn_argB]}
                        queue.put(autodockznB)

        self.W.set_queue(queue)  # , 'Molecular Docking Simulation')
        self.W.start_process()

    def check_state(self, state, prog):
        self.AMDock.state = state
        if self.AMDock.state == 2:
            self.process_state.setText('RUNNING')
            self.process_state.setStyleSheet("QLabel {font-weight: bold; color: red;}")
            self.init_prog(prog)
        elif self.AMDock.state == 1:
            self.process_state.setText('STARTING')
            self.process_state.setStyleSheet("QLabel {font-weight: bold; color: blue;}")
        else:
            self.process_state.setText('NOT RUNNING')
            self.process_state.setStyleSheet("QLabel {font-weight: bold; color: green;}")

    def check_section(self, qname):
        self.AMDock.project.previous = 0
        self.AMDock.section = qname
        self.highlight()
        if self.AMDock.section == 1:
            self.progressBar_global.setValue(50)
            self.progressBar_section.setValue(0)
            self.program_label.setText('Processing Input Files...Done.')
            self.size_x.setValue(self.lig_size)
            self.size_y.setValue(self.lig_size)
            self.size_z.setValue(self.lig_size)
            self.size_xB.setValue(self.lig_size)
            self.size_yB.setValue(self.lig_size)
            self.size_zB.setValue(self.lig_size)
            self.AMDock.log_widget.textedit.append(Ft('Prepare Initial Files...Done.\n').section())
        elif self.AMDock.section == 2:
            self.progressBar_global.setValue(75)
            self.progressBar_section.setValue(0)
            if self.AMDock.project.bsd_mode_target == 0:
                self.AMDock.log_widget.textedit.append(Ft('Binding site determination mode for Target: Automatic '
                                                          'Mode').definitions())
            elif self.AMDock.project.bsd_mode_target == 1:
                self.AMDock.log_widget.textedit.append(Ft('Binding site determination mode for Target: Centered on '
                                                          'Residue(s)').definitions())
            elif self.AMDock.project.bsd_mode_target == 2:
                self.AMDock.log_widget.textedit.append(Ft('Binding site determination mode for Target: Centered on'
                                                          'Hetero').definitions())
            else:
                self.AMDock.log_widget.textedit.append(Ft('Binding site determination mode for Target: User-defined Box'
                                                          ).definitions())
            if self.AMDock.project.bsd_mode_target in [2, 3]:
                self.coor_x.setValue(float(self.grid_center[0]))
                self.coor_y.setValue(float(self.grid_center[1]))
                self.coor_z.setValue(float(self.grid_center[2]))
                self.AMDock.log_widget.textedit.append(Ft('Target BOX: Center: {:7.02f} {:7.02f} {:7.02f}  Size: {:4d}'
                                                          '{:4d} {:4d}'.format(float(self.grid_center[0]),
                                                                               float(self.grid_center[1]),
                                                                               float(self.grid_center[2]),
                                                                               self.size[0], self.size[1], self.size[2]
                                                                               )).definitions())
            else:
                for fill in self.AMDock.target.fill_list:
                    self.AMDock.log_widget.textedit.append(Ft('Target Box at FILL: {:02d} Center: {:7.02f} {:7.02f} '
                                                              '{:7.02f} Size: {:4d} {:4d} {:4d}'.format(
                        fill, self.AMDock.target.fill_list[fill][2][0], self.AMDock.target.fill_list[fill][2][1],
                        self.AMDock.target.fill_list[fill][2][2], self.size[0], self.size[1],
                        self.size[2])).definitions())
            if self.AMDock.project.mode == 1:
                if self.AMDock.project.bsd_mode_target == 0:
                    self.AMDock.log_widget.textedit.append(Ft('Binding site determination mode for Off-Target: '
                                                              'Automatic Mode').definitions())
                elif self.AMDock.project.bsd_mode_target == 1:
                    self.AMDock.log_widget.textedit.append(Ft('Binding site determination mode for Off-Target: '
                                                              'Centered on Residue(s)').definitions())
                elif self.AMDock.project.bsd_mode_target == 2:
                    self.AMDock.log_widget.textedit.append(Ft('Binding site determination mode for Off-Target: '
                                                              'Centered on Hetero').definitions())
                else:
                    self.AMDock.log_widget.textedit.append(Ft('Binding site determination mode for Off-Target: '
                                                              'User-defined Box').definitions())

                if self.AMDock.project.bsd_mode_offtarget in [2, 3]:
                    self.coor_xB.setValue(float(self.grid_centerB[0]))
                    self.coor_yB.setValue(float(self.grid_centerB[1]))
                    self.coor_zB.setValue(float(self.grid_centerB[2]))
                    self.AMDock.log_widget.textedit.append(Ft('Off-Target BOX: Center: {:8.02f} {:8.02f} {:8.02f} '
                                                              'Size: {:4d} {:4d} {:4d}'.format(
                        float(self.grid_centerB[0]), float(self.grid_centerB[1]), float(self.grid_centerB[2]),
                        self.sizeB[0], self.sizeB[1], self.sizeB[2]
                    )).definitions())
                else:
                    for fill in self.AMDock.offtarget.fill_list:
                        self.AMDock.log_widget.textedit.append(Ft('Off-Target Box at FILL: {:02d} Center: {:7.02f} '
                                                                  '{:7.02f} {:7.02f} Size: {:4d} {:4d} {:4d}'.format(
                            fill, self.AMDock.offtarget.fill_list[fill][2][0],
                            self.AMDock.offtarget.fill_list[fill][2][1],
                            self.AMDock.offtarget.fill_list[fill][2][2],
                            self.sizeB[0], self.sizeB[1], self.sizeB[2])).definitions())
            self.program_label.setText('Binding Site Definition...Done.')
            self.AMDock.log_widget.textedit.append(Ft('Binding Site Definition...Done.\n').section())
        elif self.AMDock.section == 3:
            self.progressBar_global.setValue(100)
            self.progressBar_section.setValue(0)
            self.program_label.setText('Molecular Docking...Done.')
            self.AMDock.log_widget.textedit.append(Ft('Molecular Docking...Done.\n').section())
            self.go_result()
        elif self.AMDock.section == 4:
            ADout = open(self.AMDock.target.score)
            for line in ADout:
                line = line.strip('\n')
                self.AMDock.log_widget.textedit.append(line)
            ADout.close()
            self.progressBar_global.setValue(100)
            self.progressBar_section.setValue(0)
            self.program_label.setText('Scoring...Done.')
            self.AMDock.log_widget.textedit.append(Ft('Scoring...Done.\n').section())
            self.go_scoring()

    def reset_ligand(self):
        try:
            os.remove(self.AMDock.ligand.input)
        except:
            pass
        self.ligand_label.clear()
        self.ligand_text.clear()
        self.ligand_label.hide()
        self.AMDock.ligand = BASE()

    def reset_target(self):
        try:
            os.remove(self.AMDock.target.input)
        except:
            pass
        self.target_label.clear()
        self.target_text.clear()
        self.target_label.hide()
        self.AMDock.target = BASE()

    def reset_offtarget(self):
        try:
            os.remove(self.AMDock.offtarget.input)
        except:
            pass
        self.offtarget_label.clear()
        self.offtarget_text.clear()
        self.offtarget_label.hide()
        self.AMDock.offtarget = BASE()

    def init_prog(self, prog):
        self.AMDock.project.prog = prog
        self.program_label.setText('Running {}...'.format(prog))
        # print type(prog), type(str(prog)), prog
        prog = str(prog)
        if prog == 'Align':
            self.AMDock.log_widget.textedit.append(Ft('Running proteins alignment...').process())
        else:
            if prog[-1] == 'B':
                self.AMDock.log_widget.textedit.append(Ft('Running {} for Off-Target...'.format(prog[:-2])).process())
                self.AMDock.log_widget.textedit.append('\n')
            else:
                if prog in ['Prepare_Ligand4', 'Protonate Ligand']:
                    self.AMDock.log_widget.textedit.append(Ft('Running {} for Ligand...'.format(prog)).process())
                else:
                    self.AMDock.log_widget.textedit.append(Ft('Running {} for Target...'.format(prog)).process())
                    self.AMDock.log_widget.textedit.append('\n')
            if prog in ['AutoDock4', 'AutoDock4 B', 'AutoDock4ZN', 'AutoDock4ZN B']:
                self.timerAD = QTimer()
                self.timerAD.timeout.connect(self.autodock_output)
                self.timerAD.start(200)
                self.ad4_line = 0  # for check line number in autodock output

    def log_toggle(self):
        if self.AMDock.log_widget.isVisible():
            self.AMDock.log_widget.hide()
        else:
            self.AMDock.log_widget.show()

    def highlight(self):
        if self.AMDock.section == -1:
            self.section_state.setText('PROJECT')
        if self.AMDock.section == 0:
            self.section_state.setText('INPUT FILES')
        elif self.AMDock.section == 1:
            if self.AMDock.project.mode == 2:
                self.section_state.setText('SCORING')
            else:
                self.section_state.setText('SEARCH SPACE')
        elif self.AMDock.section == 2:
            self.section_state.setText('DOCKING')
