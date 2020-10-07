# Changes History
##Version 1.5.x
- Added keep metals option (Experimental)
- User-define metal charge (Experimental)
- User-define AD4 parameters file
##Version 1.4.x
- *Publication in Biology Direct*
- Upgrade PyMOL to v 2.1 (last in Python 2.x)
-Changed the way that objects are selected to center in binding site determination from AutoLigand. Now by default all
are selected and at each site previously determined docking are made. The results show the affinities for each pose.
-Changed the way that results and box are visualized
-Now we do the docking for every possible site identified by AutoLigand instead of doing it for arbitrary selection
-Added a log that contains all the information of the process
-Progress bars have been changed. Now there is better monitoring of the progress of the docking process
-Output file now contains more information and is better organized
-Fixed selectivity
##Version 1.3.x
-Graphical interface improvements
-fixed some inconsistencies
-improved user experience
-added more options
-added functionalities for better results in search space definition
##Version 1.1.x
-Graphical interface improvements
-fixed some inconsistencies
-added tutorial files
-update documentation
-fixed pymol alignment in off-target docking
-Graphical interface improvements
-Change in the scoring procedure when autodock4 and autodock 4Zn are selected. Now, autodock4 is used instead of the script.
-Fixed some bugs
##Version 1.0.x
-fixed some bugs
-In Off-Target Docking module, both the target and off-target proteins are align, thus improving the visualization of
the ligand sites
-Fixed reading and writing problems in the pymol plugin directory in installation process
-fixed some bugs
-An alert box is shown when default settings parameters are modified
-first program release
