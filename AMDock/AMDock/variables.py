# coding=utf-8
import multiprocessing, os, sys


class Variables():
    docking_program = None
    program_mode = 'SIMPLE'  ## 'CROSS', 'SCORING'
    project_name = "Docking_Project"
    loc_project = None
    WDIR = None
    input_dir = "input"
    result_dir = "result"
    protein_path = ""
    analog_protein_path = ''
    ligand_path = ""
    pH = 7.40
    cr = False
    scoring = False
    protein_name = None
    analog_protein_name = None
    ligand_name = None
    ligands = None
    analog_ligands = None
    metals = None
    analog_metals = None
    selected_ligand = None
    analog_selected_ligand = None
    grid_def = 'auto'
    analog_grid_def = 'auto'
    exhaustiveness = 'auto'
    poses_vina = 10
    runs_AD = 10
    spacing_autoligand = 1.0
    spacing_autodock = 0.375
    eval = 2500000
    rmsd = 2.0
    runs = 10
    protein_file = None
    analog_protein_file = None
    ligand_file = None
    result_file = ''
    analog_result_file = ''
    best_result_file = ''
    best_analog_result_file = ''
    input_protein = ''
    analog_input_protein = ''
    input_ligand = ''
    number_cpu = multiprocessing.cpu_count()
    ncpu = 1
    forcefield = 'AMBER'
    protein_h = None
    analog_protein_h = None
    ligand_h = None
    amdock_file = None

    protein_pqr = None
    analog_protein_pqr = None
    protein_pdbqt = None
    analog_protein_pdbqt = None
    protein_pdbqt_file = ''
    analog_protein_pdbqt_file = ''
    prot_basename = None
    analog_protein_basename = None
    ligand_pdbqt = None
    gd = 'gd.txt'
    gd1 = 'gd1.txt'
    res_center = 'residues_center.txt'
    res_center1 = 'residues_center1.txt'
    prev_ligand = 'prev_lig_center.txt'
    prev_ligand1 = 'prev_lig_center1.txt'
    obj_center = 'obj_center.txt'
    obj_center1 = 'obj_center1.txt'
    error = 1
    errorB = 1
    gerror = 1
    gerrorB = 1
    heavy_atoms = 0
    target_prepare = True
    offtarget_prepare = True
    ligand_prepare = True
    input_lig = None
    input_target = None
    input_offtarget = None
    scoring_file = None
    prot_align = True
    log = False


class WorkersAndScripts():
    this_python = sys.executable
    extprg_path = os.path.join(os.path.dirname(__file__), 'programs')
    doc_temp_path = os.path.dirname(__file__).split('/')
    doc_temp_path.pop()
    doc_temp = '/'
    for x in doc_temp_path:
        doc_temp = os.path.join(doc_temp, x)
    doc_path = os.path.join(doc_temp, 'Doc')
    pdb2pqr_py = str(os.path.join(extprg_path, 'pdb2pqr', 'pdb2pqr.py'))
    prepare_gpf4_py = str(os.path.join(extprg_path, 'prepare_gpf4.py'))
    prepare_gpf4zn_py = str(os.path.join(extprg_path, 'prepare_gpf4zn.py'))
    prepare_dpf_py = str(os.path.join(extprg_path, 'prepare_dpf42.py'))
    prepare_receptor4_py = str(os.path.join(extprg_path, 'prepare_receptor4.py'))
    prepare_ligand4_py = str(os.path.join(extprg_path, 'prepare_ligand4.py'))
    zinc_pseudo_py = os.path.join(extprg_path, 'zinc_pseudo.py')
    zn_ff = os.path.join(extprg_path, 'AD4Zn.dat')
    grid_pymol = os.path.join(extprg_path, 'grid_values.py')
    build_pymol = os.path.join(extprg_path, 'build_grid.py')
    vina_exec = os.path.join(extprg_path, 'vina')
    autogrid = os.path.join(extprg_path, 'autogrid4')
    autodock = os.path.join(extprg_path, 'autodock4')
    autoligand_py = os.path.join(extprg_path, 'AutoLigand.py')
    aln_pymol = os.path.join(extprg_path, 'protein_align_pymol.py')

    pymol = 'pymol'

    autodock_scorer = os.path.join(extprg_path, 'compute_AutoDock41_score.py')
    lig_site_pymol = os.path.join(extprg_path, 'ligand_site_pymol.py')
    protein_cartoon_pymol = os.path.join(extprg_path, 'protein_cartoon_pymol.py')
    openbabel = 'obabel'
    manual = os.path.join(doc_path, 'AMDock_Manual.pdf')


class Text_and_ToolTip():
    prog_title = '<html><head/><body style="font-family:times;color:#000000;text-decoration: underline;"><p><span style="font-size:24pt;' \
                 'font-weight:600;">AMDock</span><span style="font-size:16pt;font-weight:500">  Assisted Molecular Docking with AutoDock4 and AutoDock ' \
                 'Vina</span></p></body></html>'

    project_tt = '<html><head/><body style="font-family: Times New Roman; font-size:10pt;"><p><span style="font-weight:600;">Defining the working directory. </span></p><p><span style=" font-style:italic; text-decoration: underline;">Project Name</span><span >: Define the project´s name. By default, the project will be named as &quot;Docking_Project&quot;; If a folder with the same name already exists, the new folder will be renamed as: previous name + modification date.</span></p><p align="justify"><span style="font-style:italic; text-decoration: underline;">Location for Project</span><span>: Define the project´s location. </span><span style=" text-decoration: underline; color:#ff0000;">This parameter is mandatory!!!</span></p></body></html>'
    input_tt = '<html><head/><body style="font-family:Times New Roman; font-size:10pt;"><p><span ' \
               'style="font-weight:600;">Defining the input files. </span></p><p><span style="font-style:italic; ' \
               'text-decoration: underline;">Set pH</span><span >: Protonation states of protein residues and that of the ligand will be defined based on this pH value.</span></p><p><span style=" font-style:italic; text-decoration: underline;">Simple Docking</span><span >: Perform a simple molecular docking simulation. </span></p><p><span style="font-style:italic; text-decoration: underline;">Off-Target Docking(CD)</span><span >: Perform assays of selectivity between two proteins and a ligand.</span></p><p><span style="font-style:italic; text-decoration: underline;">Scoring</span><span >: Estimate the affinity of a complex using the scoring function of the selected program.</span></p><p><span style="font-style:italic; text-decoration: underline;">Protein (Target)</span><span >: Enter the protein (target) file.</span></p><p><span style="font-style:italic; text-decoration: underline;">Ligand</span><span >: Enter the ligand file.</span></p><p><span style="font-style:italic; text-decoration: underline;">Off-Targe(if CD is selected)</span><span>: Enter the protein (Off-Target) file. The Target will be considered as reference.</span></p></body></html>'
    grid_tt = '<html><head/><body style="font-family:Times New Roman; font-size:10pt;"><p><span style="font-weight:600;">Defining the search space. </span></p><p><span style="font-style:italic;">The determination of the search space will be as follows:</span></p><p><span style="font-style:italic; text-decoration: underline;">Automatic: </span><span>A potential ligand binding site will be identified and characterized by using AutoLigand tool (see manual).<br/></span><span style="font-style:italic; text-decoration: underline;">Center on Residue(s)</span><span >: A box with optimal dimensions (see manual) will be placed on the geometric center of this/these residue(s)<br/></span><span style="font-style:italic; text-decoration: underline;">Center on Ligand</span><span > : A box with optimal dimensions (see manual) will be placed on the geometric center of ligand.<br/></span><span style="font-style:italic; text-decoration: underline;">Box</span><span >: Set the coordinates and dimensions respectively.</span></p></body></html>'
    result_tt = '<html><head/><body style="font-family:Times New Roman; font-size:10pt;"><p><span style="font-weight:600;">Loading previous projects. </span></p><p><span style="font-style:italic; text-decoration: underline;">Load Data: </span><span>Open a dialog box that allows the selection of the .amdock file.<br/></span><span style="font-style:italic; text-decoration: underline;">Result File</span><span >: Open a dialog box that allows the visualization of the content of the .amdock file.<br/></span></p></body></html>'

    reference = "<html><head/><body><p><span style='font-family:Times New Roman,serif; font-size:10pt; " \
                "font-weight:600; '>AutoDock Vina 1.2.1:</span></p><p><span style='font-family:Times New Roman," \
                "serif;  font-size:10pt;'>Trott, O., Olson, A. J. (2010) AutoDock Vina: Improving the speed and " \
                "accuracy  of docking with a new scoring function, efficient optimization, and multithreading.  " \
                "</span><span style='font-family:Times New Roman,serif; font-size:10pt; font-style:italic;'>J Comput  " \
                "Chem</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>, </span><span " \
                "style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>31</span><span " \
                "style='font-family:Times New Roman,serif; font-size:10pt;'>: 455-461.</span><span " \
                "style='font-family: Times New Roman,serif; font-size:10pt; font-style:italic;'/></p><p><span " \
                "style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>AutoDock 4.2.6:</span>" \
                "</p><p><span style='font-family:Times New Roman,serif; font-size:10pt;'>Morris, G. M., Huey, R., " \
                "Lindstrom, W., Sanner, M. F., Belew, R. K., Goodsell, D. S., Olson, A. J. (2009) Autodock4 and " \
                "AutoDockTools4: automated docking with selective receptor flexiblity. </span><span " \
                "style='font-family:Times New Roman,serif; font-size:10pt; font-style:italic;'>J Comput Chem</span>" \
                "<span style='font-family:Times New Roman,serif; font-size:10pt;'>, </span><span " \
                "style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>30</span><span" \
                " style='font-family:Times New Roman,serif; font-size:10pt;'>: 2785-2791. </span></p><p><span " \
                "style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>AutoDock4</span><span " \
                "style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600; vertical-align:sub;'>Zn " \
                "</span><span style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>Force " \
                "Field:</span></p><p><span style='font-family:Times New Roman,serif; font-size:10pt;'>Santos-Martins," \
                " D., Forli, S., João Ramos, M., Olson, A. J. (2014) AutoDock4</span><span style='font-family:Times " \
                "New Roman,serif; font-size:10pt; vertical-align:sub;'>Zn</span><span style='font-family:Times New " \
                "Roman,serif; font-size:10pt;'>: an improved AutoDock force field for small-molecule docking to " \
                "zinc metalloproteins. </span><span style='font-family:Times New Roman,serif; font-size:10pt; " \
                "font-style:italic;'>J Chem Info Model</span><span style='font-family:Times New Roman,serif; " \
                "font-size:10pt;'>,</span><span style='font-family:Times New Roman,serif; font-size:10pt; " \
                "font-style:italic;'/><span style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;" \
                "'>54</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>:</span><span " \
                "style='font-size:10pt;'/><span style='font-family:Times New Roman,serif; font-size:10pt;'>2371-2379" \
                " http://dx.doi.org/10.1021/ci500209e</span></p><p><span style='font-family:Times New Roman,serif;" \
                " font-size:10pt;'/><span style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>" \
                "Open Babel 2.4.1:</span></p><p><span style='font-family:Times New Roman,serif; font-size:10pt;'>" \
                "O'Boyle, N. M., Banck, M., James, C. A., Morley, C., Vandermeersch, T., Hutchison, G. R. (2011) " \
                "Open Babel: An open chemical toolbox. </span><span style='font-family:Times New Roman,serif; " \
                "font-size:10pt; font-style:italic;'>J Cheminf</span><span style='font-family:Times New Roman,serif; " \
                "font-size:10pt;'>, </span><span style='font-family:Times New Roman,serif; font-size:10pt; " \
                "font-weight:600;'>3</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>:" \
                " 33.</span></p><p><span style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>" \
                "PDB2PQR 2.1:</span></p><p><span style='font-family:Times New Roman,serif; font-size:10pt;'>Dolinsky, " \
                "T. J., Nielsen, J. E., McCammon, J. A., Baker, N. A. (2004) PDB2PQR: an automated pipeline for the" \
                " setup of Poisson-Boltzmann electrostatics calculations. </span><span style='font-family:Times " \
                "New Roman,serif; font-size:10pt; font-style:italic;'>Nucleic Acids Res</span><span style='font-family:" \
                "Times New Roman,serif; font-size:10pt;'>, </span><span style='font-family:Times New Roman,serif; " \
                "font-size:10pt; font-weight:600;'>32</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>: W665-7 (</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>http://dx.doi.org/10.1093/nar/gkh381</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>)</span></p><p><span style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>AutoDockTools Module 1.5.7:</span></p><p><span style='font-family:Times New Roman,serif; font-size:10pt;'>Sanner, M. F. (1999) Python: A Programming Language for Software Integration and Development. </span><span style='font-family:Times New Roman,serif; font-size:10pt; font-style:italic;'>J Mol Graphics</span><span style='font-family:Times New Roman,serif; font-size:10pt;'/><span style='font-family:Times New Roman,serif; font-size:10pt; font-style:italic;'>Mod</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>, </span><span style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>17</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>: 57-61</span></p><p><span style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>AutoLigand:</span></p><p><span style='font-family:Times New Roman,serif; font-size:10pt;'>Harris, R., Olson, A., Goodsell, D. (2008) Automated prediction of ligand-binding sites in proteins.  </span><span style='font-family:Times New Roman,serif; font-size:10pt; font-style:italic;'>Proteins</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>, </span><span style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>70</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>: 1505-1517</span></p><p><span style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>Optimal Box Size 1.1:</span></p><p><span style='font-family:Times New Roman,serif; font-size:10pt;'>Feinstein, W. P., Brylinski, M. (</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>2015</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>) </span><span style='font-family:Times New Roman,serif; font-size:10pt;'>Calculating an optimal box size for ligand docking and virtual screening against experimental and predicted binding pockets. </span><span style='font-family:Times New Roman,serif; font-size:10pt; font-style:italic;'>J Cheminf</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>, </span><span style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>7</span><span style='font-family:Times New Roman,serif; font-size:10pt;'>: 18</span></p><p><span style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'/><span style='font-family:Times New Roman,serif; font-size:10pt; font-weight:600;'>PyMOL 1.8.5:</span></p><p><span style='font-family:Times New Roman,serif; font-size:10pt;'>DeLano, W. L. (2002) The PyMOL Molecular Graphics System.</span></p></body></html>"


class Objects():
    style_file = os.path.join(os.path.dirname(__file__), 'style.css')
    iconsPath = os.path.join(os.path.dirname(__file__), 'images')
    splashscreen_path = os.path.join(iconsPath, 'splashscreen.png')
    app_icon = os.path.join(iconsPath, 'amdock_icon.png')
    reset_icon = os.path.join(iconsPath, 'reset.png')
    home_icon_white = os.path.join(iconsPath, 'home_icon_white.png')
    home_icon = os.path.join(iconsPath, 'home_icon.png')
    presentation = os.path.join(iconsPath, 'presentation.png').replace('\\', '/')
    error_checker = os.path.join(iconsPath, 'error_checker.png')
    error_checker_ok = os.path.join(iconsPath, 'error_checker_ok.png')
    new_icon = os.path.join(iconsPath, 'new_icon.png')
