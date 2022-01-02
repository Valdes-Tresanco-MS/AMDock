# AMDock: **A***ssisted* **M***olecular* **Dock***ing with Autodock4 and Autodock Vina*
AMDock (Assisted Molecular Docking) is a user-friendly graphical tool to assist in the docking of protein-ligand 
complexes using Autodock-Vina or AutoDock4. This tool integrates several external programs for processing docking input 
files, define the search space (box) and perform docking under user’s supervision.

**Version 1.6.x for Linux** (**Build 1.6.1-beta**)

**DOCUMENTATION**

Manual, tutorials and test files are located in **Doc** folder. (May be out of date. Please check the wiki)

**Cite us**

Valdes-Tresanco, M.S., Valdes-Tresanco, M.E., Valiente, P.A. and Moreno E. AMDock: a versatile graphical tool for
 assisting molecular docking with Autodock Vina and Autodock4. Biol Direct 15, 12 (2020). https://doi.org/10.1186/s13062-020-00267-2
 
 <a href="https://www.scimagojr.com/journalsearch.php?q=5800173376&amp;tip=sid&amp;exact=no" title="SCImago Journal &amp; Country Rank"><img border="0" src="https://www.scimagojr.com/journal_img.php?id=5800173376" alt="SCImago Journal &amp; Country Rank"  /></a>

**INSTALL**
Installation can be carried out in two ways
1. Using a conda environment. To do this, proceed as follows:

If you don't have conda installed, please visit the [Miniconda download page](https://docs.conda.io/en/latest/miniconda.html).

Those with an existing conda installation may wish to create a new conda "environment" to avoid conflicts with what 
you already have installed. To do this:

    conda create --name AMDock
    conda activate AMDock

(Note that you would need to perform the "conda activate" step every time you wish to use AMDock in a new terminal; 
  it might be appropriate to add this to your start-up script. Creating a new environment should not be necessary if 
  you only use conda for AMDock.)

Once this is done, type:

    conda install -c conda-forge pymol-open-source openbabel pdb2pqr

and finally: 

    python -m pip install git+https://github.com/Valdes-Tresanco-MS/AutoDockTools_py3
    python -m pip install AMDock

2. Using the OS Python 3 environment. To do this, proceed as follows:

    
    sudo apt install pymol openbabel

(Note that this version of AMDock works with openbabel 3.x)

    python3 -m pip install pdb2pqr
    python3 -m pip install git+https://github.com/Valdes-Tresanco-MS/AutoDockTools_py3
    python3 -m pip install AMDock
    
Before using AMDock, you most install the PyMOL plugin (grid_amdock.py).

If it does not appear please follow the instructions:
- Download the grid_amdock.py file
- Open PyMOL > Plugins > Manager Plugins > Install New Plugin > Choose File and select the grid_amdock.py file
- Restart PyMOL


To open AMDock, type in the terminal:
    
    AMDock

To view the update history, please check Changes_History file

**TUTORIALS**

Please, check the wiki https://github.com/Valdes-Tresanco-MS/AMDock-win/wiki

[<img src="./AMDock/AMDock/images/jetbrains-variant-4.png" height="100" align="right" />](https://www.jetbrains.com/?from=https://github.com/Valdes-Tresanco-MS/AMDock)

## Support
This project is possible thanks to the Open Source license of the 
[JetBrains](https://www.jetbrains.com/?from=https://github.com/Valdes-Tresanco-MS/AMDock
) programs.
