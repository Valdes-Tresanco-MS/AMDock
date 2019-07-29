from tools import GridDefinition
from PyQt4 import QtCore

default_setting = {
    "location_dir": "",
    "docking_program": None,
    "project_name": "Docking_Project",
    "pH": 7.4,
    "protein_name": "protein",
    "ligand_name": "ligand",
    "ligands": None,
    "metals": None,
    "selected_ligand": None,
    "grid_def": 'auto',
    "rmsd_tolerance": 2,
    "energy_range": 3,
    "cpu": 1,
    "exhaustiveness": "auto",
    "poses_vina": 10,
    "total_poses": 500,
    "protein_file": "",
    "ligand_file": "",
    "working_dir": "",
    "input_dir": 'input',
    "result_dir": 'results'
}


def values(self, k):  # ok
    if k.objectName() == 'horizontalSlider':
        self.parent.cpu = self.horizontalSlider.value()
        self.cpu_label.setText("%s" % self.parent.cpu + " CPU in use of %s" % self.number_cpu)
    elif k.objectName() == 'pH_value':
        self.parent.pH = self.pH_value.value()
    elif k.objectName() == 'nposes_value':
        self.parent.poses_vina = self.nposes_value.value()
    elif k.objectName() == "exh_value":
        self.parent.exhaustiveness = self.exh_value.value()


def check_res(self):
    try:
        self.check = GridDefinition(self.parent.input_protein, self.grid_predef_text.text())
        error = self.check.check_select()
    except:
        error = 1
    if error == 0:
        self.checker_icon_ok.show()
        self.checker_icon.hide()
        self.run_button.setEnabled(True)
    else:
        self.checker_icon.show()
        self.checker_icon_ok.hide()
        self.run_button.setEnabled(False)


def progress(self, form, phase, value=None, finish=False, reverse=False, time=0, mess=''):
    if phase == 0:
        stage = 'Initial Configuration: '
    elif phase == 1:
        stage = 'Prepare Input Files: '
    elif phase == 2:
        stage = 'Binding Site Definition: '
    else:
        stage = 'Molecular Docking Simulation: '
    timems = time * 1000
    if form == 0:
        if reverse:
            self.progressBar.setValue(value)
        else:
            if finish:
                self.progressBar.setValue(value)
            else:
                self.progressBar.setValue(value)

    elif form == 1:
        if reverse:
            self.progressBar.setValue(value)
        else:
            if finish:
                self.timeline.stop()
                self.progressBar.setValue(value)
            else:
                self.previous_value = self.progressBar.value()
                self.timeline = QtCore.QTimeLine(timems)
                self.timeline.setFrameRange(0, (value - self.previous_value) - 1)
                self.timeline.frameChanged.connect(lambda i: self.progressBar.setValue(self.previous_value + i))
                self.timeline.start()
    elif form == 3:
        if reverse:
            self.progressBar.setValue(value)
        else:
            if finish:
                self.progressBar.setValue(value)
            else:
                self.progressBar.setValue(value[0] + value[1])
