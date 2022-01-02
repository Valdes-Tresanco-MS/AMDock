# coding=utf-8
import multiprocessing
import os
import sys
from pathlib import Path
import AutoDockTools, pymol
import platform


class Variables:
    def __init__(self):
        self.project_name = 'Project_Docking'
        self.docking_program = None

        self.this_python = sys.executable
        self.amdock_dir = Path(__file__).parent
        self.data_dir = self.amdock_dir.joinpath('data')

        self.adt = Path(AutoDockTools.__file__).parent
        self.doc_path = os.path.join(os.path.join(self.amdock_dir, os.pardir, 'Doc'))
        self.pdb2pqr_py = 'pdb2pqr30'
        self.prepare_gpf4_py = self.adt.joinpath('Utilities24', 'prepare_gpf4.py').as_posix()
        self.prepare_gpf4zn_py = self.data_dir.joinpath('prepare_gpf4zn.py').as_posix()
        self.prepare_dpf_py = self.adt.joinpath('Utilities24', 'prepare_dpf42.py').as_posix()
        self.prepare_receptor4_py = self.adt.joinpath('Utilities24', 'prepare_receptor4.py').as_posix()
        self.prepare_ligand4_py = self.adt.joinpath('Utilities24', 'prepare_ligand4.py').as_posix()
        self.zinc_pseudo_py = self.data_dir.joinpath('zinc_pseudo.py').as_posix()
        self.zn_ff = self.data_dir.joinpath('AD4Zn.dat').as_posix()
        self.grid_pymol = self.data_dir.joinpath('grid_values.py').as_posix()
        if platform.system() == 'Darwin':
            self.vina_exec = self.data_dir.joinpath('vina_mac').as_posix()
            self.autogrid = self.data_dir.joinpath('autogrid4_mac').as_posix()
            self.autodock = self.data_dir.joinpath('autodock4_mac').as_posix()
        else:
            self.vina_exec = self.data_dir.joinpath('vina').as_posix()
            self.autogrid = self.data_dir.joinpath('autogrid4').as_posix()
            self.autodock = self.data_dir.joinpath('autodock4').as_posix()
        self.autoligand_py = self.data_dir.joinpath('AutoLigand.py').as_posix()
        self.pymol = Path(pymol.__file__).as_posix()
        self.aln_pymol = self.data_dir.joinpath('protein_align_pymol.py').as_posix()
        self.openbabel = 'obabel'
        self.lig_site_pymol = self.data_dir.joinpath('ligand_site_pymol.py').as_posix()
        self.manual = os.path.join(self.doc_path, 'AMDock_Manual.pdf')

        self.prog_title = '<html><head/><body style="font-family:times;color:#000000;text-decoration: ' \
                          'underline;"><p><span style="font-size:24pt; font-weight:600;">AMDock</span><span ' \
                          'style="font-size:16pt;font-weight:500"> Assisted Molecular Docking with AutoDock4 and ' \
                          'AutoDock Vina</span></p></body></html> '
        self.project_tt = '<html><head/><body style="font-family: Times New Roman; font-size:10pt; color: ' \
                          'blue;"><p><span style="font-weight:600;">Defining the working directory. ' \
                          '</span></p><p><span style=" font-style:italic; text-decoration: underline;">Project ' \
                          'Name</span><span >: Define the project´s name. By default, the project will be named as ' \
                          '&quot;Docking_Project&quot;; If a folder with the same name already exists, the new folder '\
                          'will be renamed as: previous name + modification date.</span></p><p align="justify"><span ' \
                          'style="font-style:italic; text-decoration: underline;">Location for Project</span><span>: ' \
                          'Define the project´s location. </span><span style=" text-decoration: underline; ' \
                          'color:#ff0000;">This parameter is mandatory!!!</span></p></body></html> '
        self.input_tt = '<html><head/><body style="color: blue; font-family:Times New Roman; ' \
                        'font-size:10pt;"><p><span style="font-weight:600;">Defining the input files. ' \
                        '</span></p><p><span style="font-style:italic; text-decoration: underline;">Set ' \
                        'pH</span><span >: Protonation states of protein residues and that of the ligand will be ' \
                        'defined based on this pH value.</span></p><p><span style=" font-style:italic; ' \
                        'text-decoration: underline;">Simple Docking</span><span >: Perform a simple molecular ' \
                        'docking simulation. </span></p><p><span style="font-style:italic; text-decoration: ' \
                        'underline;">Off-Target Docking(OD)</span><span >: Perform assays of selectivity between two ' \
                        'proteins and a ligand.</span></p><p><span style="font-style:italic; text-decoration: ' \
                        'underline;">Scoring</span><span >: Estimate the affinity of a complex using the scoring ' \
                        'function of the selected program.</span></p><p><span style="font-style:italic; ' \
                        'text-decoration: underline;">Protein (Target)</span><span >: Enter the protein (target) ' \
                        'file.</span></p><p><span style="font-style:italic; text-decoration: ' \
                        'underline;">Ligand</span><span >: Enter the ligand file.</span></p><p><span ' \
                        'style="font-style:italic; text-decoration: underline;">Off-Target(if OD is ' \
                        'selected)</span><span>: Enter the protein (Off-Target) file. The Target will be considered ' \
                        'as reference.</span></p></body></html> '
        self.grid_tt = '<html><head/><body style="color: blue; font-family:Times New Roman; font-size:10pt;"><p><span '\
                       'style="font-weight:600;">Defining the search space. </span></p><p><span ' \
                       'style="font-style:italic;">The determination of the search space will be as ' \
                       'follows:</span></p><p><span style="font-style:italic; text-decoration: underline;">Automatic: '\
                       '</span><span>A potential ligand binding site will be identified and characterized by using ' \
                       'AutoLigand tool (see manual).<br/></span><span style="font-style:italic; text-decoration: ' \
                       'underline;">Center on Residue(s)</span><span >: A box with optimal dimensions (see manual) ' \
                       'will be placed on the geometric center of this/these residue(s)<br/></span><span ' \
                       'style="font-style:italic; text-decoration: underline;">Center on Ligand</span><span > : A box '\
                       'with optimal dimensions (see manual) will be placed on the geometric center of ' \
                       'ligand.<br/></span><span style="font-style:italic; text-decoration: ' \
                       'underline;">Box</span><span >: Set the coordinates and dimensions ' \
                       'respectively.</span></p></body></html> '
        self.result_tt = '<html><head/><body style="color: blue; font-family:Times New Roman; ' \
                         'font-size:10pt;"><p><span style="font-weight:600;">Loading previous projects. ' \
                         '</span></p><p><span style="font-style:italic; text-decoration: underline;">Load Data: ' \
                         '</span><span>Open a dialog box that allows the selection of the .amdock ' \
                         'file.<br/></span><span style="font-style:italic; text-decoration: underline;">Result ' \
                         'File</span><span >: Open a dialog box that allows the visualization of the content of the ' \
                         '.amdock file.<br/></span></p></body></html> '
        self.reference = "<html><head/><body><p><span style='font-family:Times New Roman,serif; font-size:10pt; " \
                         "font-weight:600; '>AutoDock Vina 1.2.1:</span></p><p><span style='font-family:Times New " \
                         "Roman,serif;  font-size:10pt;'>Trott, O., Olson, A. J. (2010) AutoDock Vina: Improving the " \
                         "speed and accuracy  of docking with a new scoring function, efficient optimization, " \
                         "and multithreading.  </span><span style='font-family:Times New Roman,serif; font-size:10pt; "\
                         "font-style:italic;'>J Comput  Chem</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>, </span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt; font-weight:600;'>31</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>: 455-461.</span><span style='font-family: Times New Roman," \
                         "serif; font-size:10pt; font-style:italic;'/></p><p><span style='font-family:Times New " \
                         "Roman,serif; font-size:10pt; font-weight:600;'>AutoDock 4.2.6:</span></p><p><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'>Morris, G. M., Huey, R., " \
                         "Lindstrom, W., Sanner, M. F., Belew, R. K., Goodsell, D. S., Olson, A. J. (2009) Autodock4 " \
                         "and AutoDockTools4: automated docking with selective receptor flexiblity. </span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt; font-style:italic;'>J Comput " \
                         "Chem</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>, </span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>30</span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'>: 2785-2791. </span></p><p><span "\
                         "style='font-family:Times New Roman,serif; font-size:10pt; " \
                         "font-weight:600;'>AutoDock4</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt; font-weight:600; vertical-align:sub;'>Zn </span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>Force " \
                         "Field:</span></p><p><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>Santos-Martins, D., Forli, S., João Ramos, M., Olson, A. J. (2014) " \
                         "AutoDock4</span><span style='font-family:Times New Roman,serif; font-size:10pt; " \
                         "vertical-align:sub;'>Zn</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>: an improved AutoDock force field for small-molecule docking to " \
                         "zinc metalloproteins. </span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt; font-style:italic;'>J Chem Info Model</span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'>,</span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt; font-style:italic;'/><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>54</span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'>:</span><span " \
                         "style='font-size:10pt;'/><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>2371-2379 http://dx.doi.org/10.1021/ci500209e</span></p><p><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'/><span style='font-family:Times " \
                         "New Roman,serif; font-size:10pt; font-weight:600;'>Open Babel 2.4.1:</span></p><p><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'>O'Boyle, N. M., Banck, M., " \
                         "James, C. A., Morley, C., Vandermeersch, T., Hutchison, G. R. (2011) Open Babel: An open " \
                         "chemical toolbox. </span><span style='font-family:Times New Roman,serif; font-size:10pt; " \
                         "font-style:italic;'>J Cheminf</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>, </span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt; font-weight:600;'>3</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>: 33.</span></p><p><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt; font-weight:600;'>PDB2PQR 2.1:</span></p><p><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'>Dolinsky, T. J., Nielsen, J. E., "\
                         "McCammon, J. A., Baker, N. A. (2004) PDB2PQR: an automated pipeline for the setup of " \
                         "Poisson-Boltzmann electrostatics calculations. </span><span style='font-family:Times New " \
                         "Roman,serif; font-size:10pt; font-style:italic;'>Nucleic Acids Res</span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'>, </span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>32</span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'>: W665-7 (</span><span " \
                         "style='font-family:Times New Roman,serif; " \
                         "font-size:10pt;'>http://dx.doi.org/10.1093/nar/gkh381</span><span style='font-family:Times " \
                         "New Roman,serif; font-size:10pt;'>)</span></p><p><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt; font-weight:600;'>AutoDockTools Module 1.5.7:</span></p><p><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'>Sanner, M. F. (1999) Python: A " \
                         "Programming Language for Software Integration and Development. </span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt; font-style:italic;'>J Mol " \
                         "Graphics</span><span style='font-family:Times New Roman,serif; font-size:10pt;'/><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt; " \
                         "font-style:italic;'>Mod</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>, </span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt; font-weight:600;'>17</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>: 57-61</span></p><p><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt; font-weight:600;'>AutoLigand:</span></p><p><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'>Harris, R., Olson, A., Goodsell, "\
                         "D. (2008) Automated prediction of ligand-binding sites in proteins.  </span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt; " \
                         "font-style:italic;'>Proteins</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>, </span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt; font-weight:600;'>70</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>: 1505-1517</span></p><p><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt; font-weight:600;'>Optimal Box Size 1.1:</span></p><p><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'>Feinstein, W. P., Brylinski, " \
                         "M. (</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>2015</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>) </span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>Calculating an optimal box size for ligand docking and virtual " \
                         "screening against experimental and predicted binding pockets. </span><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt; font-style:italic;'>J " \
                         "Cheminf</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>, " \
                         "</span><span style='font-family:Times New Roman,serif; font-size:10pt; " \
                         "font-weight:600;'>7</span><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt;'>: 18</span></p><p><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt; font-weight:600;'/><span style='font-family:Times New Roman," \
                         "serif; font-size:10pt; font-weight:600;'>PyMOL 1.8.5:</span></p><p><span " \
                         "style='font-family:Times New Roman,serif; font-size:10pt;'>DeLano, W. L. (2002) The PyMOL " \
                         "Molecular Graphics System.</span></p></body></html> "

        self.style_file = self.data_dir.joinpath('style.css').as_posix()
        self.config_file = self.data_dir.joinpath('configration.ini').as_posix()
        self.splashscreen_path = self.data_dir.joinpath('splashscreen.png').as_posix()
        self.app_icon = self.data_dir.joinpath('amdock_icon.png').as_posix()
        self.reset_icon = self.data_dir.joinpath('reset.png').as_posix()
        self.home_icon_white = self.data_dir.joinpath('home_icon_white.png').as_posix()
        self.home_icon = self.data_dir.joinpath('home_icon.png').as_posix()
        self.presentation = self.data_dir.joinpath('presentation.png').as_posix()
        self.error_checker = self.data_dir.joinpath('error_checker.png').as_posix()
        self.error_checker_ok = self.data_dir.joinpath('error_checker_ok.png').as_posix()
        self.new_icon = self.data_dir.joinpath('new_icon.png').as_posix()

Variables()