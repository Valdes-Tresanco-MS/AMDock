# AMDock: *A*ssisted *M*olecular *Dock*ing with Autodock4 and Autodock Vina
AMDock (Assisted Molecular Docking) is a user-friendly graphical tool to assist in the docking of protein-ligand 
complexes using Autodock-Vina or AutoDock4. This tool integrates several external programs for processing docking input 
files under user’s supervision.


**Build 1.1.0**

**INSTALL**

-unzip the *.zip file<br>
-execute `./install.sh` and follow instructions


Before installation, verify that you have PyMol, PyQt4 and numpy as python
  modules, if not, execute<br> 
  `sudo apt install pymol python-qt4 python-numpy`

Before using the program, check that pymol has the AMDock plugin in taskbar.<br>
If it does not appear please follow the instructions:<br>
-open PyMOL > Plugins > Manager Plugins > Settings > Add new directory<br>
PyMOL should automatically have:

`~/.pymol/startup or /home/users_name/.pymol/startup`

if not, please select the previous address<br>

**UNINSTALL**

search the installation directory and execute `./uninstall.sh` and follow instructions

To view the update history, please check Changes_History file
