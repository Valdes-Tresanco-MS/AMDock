# AMDock: **A***ssisted* **M***olecular* **Dock***ing with Autodock4 and Autodock Vina*
AMDock (Assisted Molecular Docking) is a user-friendly graphical tool to assist in the docking of protein-ligand 
complexes using Autodock-Vina or AutoDock4. This tool integrates several external programs for processing docking input 
files, define the search space (box) and perform docking under user’s supervision.

**Version 1.4.x** (**Build 1.4.96**)

**DOCUMENTATION**

A manual and the folders containing the files for each of one of the tutorials in the manual are located in Doc folder

**INSTALLATION**

-unzip the *.zip file<br>
-execute `./install.sh` and follow instructions

*If `./install.sh` is not running, change the execution permissions. To do this press 
`right click > permissions > Allow execute this file as a program`*


Before installation, verify that you have PyMOL, PyQt4 and numpy as python
  modules, if not, execute in a terminal<br> 
  `sudo apt install pymol python-qt4 python-numpy openbabel`

Before using the program, check that PyMOL has the AMDock plugin in taskbar.<br>
If it does not appear please follow the instructions:<br>
-open PyMOL > Plugins > Manager Plugins > Settings > Add new directory<br>
PyMOL should automatically have:

`~/.pymol/startup or /home/user_name/.pymol/startup` if not, please select the previous address<br>

after this you must restart PyMol

***Automatically, a file (AMDock.desktop) must be generated that allows its execution from the start menu. If you use
 a linux version where it doesn't appear, you can run it through the terminal:
`installation folder> right click> run a terminal here> (in terminal) ./AMDock.sh`***

**UNINSTALLATION**

Just search the installation directory and execute `./uninstall.sh` in a terminal and follow instructions

To view the update history, please check Changes_History file
