import os
import re
from math import sqrt

# import pybel
from MolKit import Read, makeMoleculeFromAtoms
from MolKit.pdbWriter import PdbqtWriter, PdbWriter

atom_prop = {"AL": 26.9815, "Al": 26.9815, "AR": 39.948, "Ar": 39.948, "AU": 196.97, "Au": 196.97, "Br": 78.9183,
             "BR": 78.9183, "C": 12, "Ca": 39.9625906, "CA": 39.9625906, "Cl": 34.968852721, "CL": 34.968852721,
             "Cs": 132.90, "CS": 132.90, "D": 2.014101779, "F": 18.998, "Fe": 53.9396127, "FE": 53.9396127, "Ge": 72.64,
             "GE": 72.64, "H": 1.007825035, "He": 4.0026, "HE": 4.0026, "Hg": 200.6, "HG": 200.6, "I": 126.90447,
             "In": 114.8, "IN": 114.8, "K": 39.102, "Mg": 24.30, "MG": 24.30, "N": 14.006723, "Na": 22.99, "NA": 22.99,
             "Ne": 20.180, "NE": 20.180, "O": 15.99491463, "P": 30.9737620, "Pb": 207.2, "PB": 207.2, "Rb": 85.47,
             "RB": 85.47, "S": 31.97207070, "Si": 28.0855, "SI": 28.0855, "Sr": 87.62, "SR": 87.62, "Ti": 47.87,
             "TI": 47.87, "Tl": 11.85, "TL": 11.85, "Zn": 63.9291448, "ZN": 63.9291448, "Co": 58.933200,
             "CO": 58.933200}
metal_prop = {'MG': [2.000, 1.700], 'AL': [3.000, 2.05], 'SI': [4.000, 2.000], 'CA': [2.000, 1.973],
              'MN': [2.000, 1.700], 'FE': [2.000, 1.700], 'CO': [2.000, 1.700], 'NI': [3.000, 1.700],
              'CU': [2.000, 1.700], 'ZN': [2.000, 1.70], 'Mg': [2.000, 1.700], 'Al': [3.000, 2.05],
              'Si': [4.000, 2.000], 'Ca': [2.000, 1.973], 'Mn': [2.000, 1.700], 'Fe': [2.000, 1.700],
              'Co': [2.000, 1.700], 'Ni': [3.000, 1.700], 'Cu': [2.000, 1.700], 'Zn': [2.000, 1.70]}

aa = ['CYS', 'ILE', 'SER', 'VAL', 'GLN', 'LYS', 'ASN', 'PRO', 'THR', 'PHE', 'ALA', 'HIS', 'GLY', 'ASP', 'LEU', 'ARG',
      'TRP', 'GLU', 'TYR', 'MET', 'HID', 'HSP', 'HIE', 'HIP', 'CYX', 'CSS', 'ALA']
aa1 = ['C', 'I', 'S', 'V', 'Q', 'K', 'N', 'P', 'T', 'F', 'H', 'G', 'D', 'L', 'R', 'W', 'E', 'Y', 'M', 'A']
na = ['DC', 'DG', 'DA', 'DT', 'DU']
glycosides = ['NAG', 'BGLN', 'FUC', 'AFUC', 'MAN', 'AMAN', 'BMA', 'BMAN']
hoh = ['HOH', 'WAT', 'TIP3', 'TIP4']
metal = ['Zn', 'CA', 'MG', 'FE', 'CO', ]

hter = ['A', 'BES', 1024]


class FormatedText:
    def __init__(self, text):
        self.text = text

    def important(self):
        text = '<span style="background-color: blue; color: white; font-weight: 900">AMDOCK:</span> <span ' \
               'style="font-weight: 900">%s</span>' % self.text
        return text

    def process(self):
        text = '<span style="background-color: gray; color: white; font-weight: 900">AMDOCK:</span> <span ' \
               'style="font-weight: 900">%s</span>' % self.text
        return text

    def error(self):
        text = '<span style="background-color: red; color: white; font-weight: 900">AMDOCK:</span> <span ' \
               'style="font-weight: 900">%s</span>' % self.text
        return text

    def definitions(self):
        text = '<span style="background-color: green; color: white; font-weight: 900">AMDOCK:</span> <span ' \
               'style="font-weight: 900">%s</span>' % self.text
        return text

    def section(self):
        text = '<span style="background-color: #000066; color: white; font-weight: 900">AMDOCK:</span> <span ' \
               'style="font-weight: 900">%s</span>' % self.text
        return text

    def separator(self):
        text = '<span style="font-weight: 900">%s</span>' % self.text
        return text

    def resetting(self):
        text = '<span style="background-color: #333333; color: white; font-weight: 900"> <br> AMDOCK: %s</span>' % \
               self.text
        return text


class PROJECT:
    def __init__(self):
        self.name = "Project_Docking"
        self.location = None
        self.WDIR = None
        self.input = None
        self.results = None
        self.output = None
        self.bsd_mode_target = 0  # 0: auto, 1: residues, 2: hetero, 3: user-defined box
        self.bsd_mode_offtarget = 0  # 0: auto, 1: residues, 2: hetero, 3: user-defined box
        self.mode = 0  # 0: simple, 1: off-target docking, 2:
        self.prog = None
        self.part = 0
        self.log = None

    def get_loc(self, filenames):
        if filenames:
            self.location = str(filenames[0])

    def get_info(self, name):
        if name:
            self.name = str(name)
        self.WDIR = os.path.normpath(os.path.join(self.location, self.name))
        self.input = os.path.normpath(os.path.join(self.WDIR, 'input'))
        self.results = os.path.normpath(os.path.join(self.WDIR, 'results'))
        self.output = os.path.normpath(os.path.join(self.WDIR, self.name + '.amdock'))
        self.log = os.path.normpath(os.path.join(self.WDIR, self.name + '.log'))


class BASE:
    def __init__(self):
        self.name = None
        self.path = None
        self.ext = None
        self.prepare = True
        self.input = None
        self.ha = None
        self.selected = None
        self.pqr = None
        self.pdb = None
        self.pdbqt = None
        self.pdbqt_name = None
        self.auto_lig = None
        self.gpf = None
        self.dlg = None
        self.dpf = None
        self.tzgpf = None
        self.tzdlg = None
        self.tzdpf = None
        self.tz_name = None
        self.tzpdbqt = None
        self.het = None
        self.zn_atoms = None
        self.metals = None
        self.all_poses = None
        self.best_pose = None
        self.vina_output = None
        self.vina_fill_output = []
        self.vina_log = None
        self.score = None

        self.ad4_output = None

        self.bsd_ready = False
        self.fill_list = {}

    def get_data(self, filenames):
        if filenames:
            self.path = str(filenames[0])
            self.ext = str(os.path.basename(self.path).split('.')[1])
            self.name = str(os.path.basename(self.path).split('.')[0]).replace(' ', '_')
            self.pqr = self.name + '_h.pqr'
            self.pdb = self.name + '_h.pdb'
            if self.ext == 'pdbqt':
                self.prepare = False

            if self.ext == 'pdbqt':
                self.pdbqt = self.name + '.pdbqt'
                self.pdbqt_name = self.name
            else:
                self.pdbqt = self.name + '_h.pdbqt'
                self.pdbqt_name = self.name + '_h'
            self.tz_name = self.pdbqt_name + '_TZ'
            self.auto_lig = self.name + '_autolig.gpf'
            self.gpf = self.pdbqt_name + '.gpf'
            self.dlg = self.name + '_out.dlg'
            self.dpf = self.pdbqt_name + '.dpf'
            self.tzpdbqt = self.pdbqt_name + '_TZ.pdbqt'
            self.tzgpf = self.pdbqt_name + '_TZ.gpf'
            self.tzdlg = self.pdbqt_name + '_TZ.dlg'
            self.tzdpf = self.pdbqt_name + '_TZ.dpf'
            self.all_poses = 'all_poses' + '_' + self.pdbqt_name + '.pdb'

    def save_pdb(self, filename):
        """ avoid errors when visualize entry protein in pdbqt format"""
        mol = Read(filename)[0]
        writer = PdbWriter()
        writer.write(self.pdb, mol.allAtoms, records=['ATOM', 'HETATM'])


class PDBINFO:
    def __init__(self, pdb):
        # if not is valid
        self.exception = None
        try:
            self.mol = Read(pdb)[0]
        except Exception as inst:
            self.exception = inst  # the exception instance
        self.het = []
        self.zn_atoms = []
        self.metals = []
        self.size = None
        self.center = None
        self.selection_center = None
        self.prot = []
        if not self.exception:
            self.get_info()
            self.center = self.mol.getCenter()

    def __call__(self, *args, **kwargs):
        pass

    def check_select(self, selection):
        res_list = selection.split(';')
        for res in res_list:
            res = res.strip()
            if not res:
                return
            res = res.split(':')
            if not res in [[x[0].name, x[1].name[:3], x[2]] for x in self.prot]:
                return
        return True

    def get_info(self):
        for chain in self.mol.chains:
            for res in chain.residues:
                # exclude water residues
                if res.name[:3] in ['WAT', 'HOH', 'SOL']:
                    continue
                if res.name[:3].strip() == 'ZN':
                    self.zn_atoms.append([chain, res])
                    # self.metals.append([chain, res])
                elif res.name[:3].strip().lower() in ['mn', 'mg', 'ca', 'fe']:
                    self.metals.append([chain, res])
                elif res.hetatm():
                    self.het.append([chain, res])
                elif res.name[:3] in aa:
                    self.prot.append([chain, res, res.name[3:]])

    def get_het(self):
        if self.exception:
            return
        het = []
        for lst in self.het:
            het.append([lst[0].name, lst[1].name])
        return het

    def get_zn(self):
        if self.exception:
            return
        zn = []
        for lst in self.zn_atoms:
            c = 0.0
            if lst[1].atoms[0].chargeSet:
                c = lst[1].atoms[0].charge
            zn.append([lst[0].name, lst[1].name, c])
        return zn

    def get_metals(self):
        if self.exception:
            return
        metals = []
        for lst in self.metals:
            c = 0.0
            if lst[1].atoms[0].chargeSet:
                c = lst[1].atoms[0].charge
            metals.append([lst[0].name, lst[1].name, c])
        return metals

    def get_ha(self):
        if self.exception:
            return
        return len([x for x in self.mol.allAtoms if x.element != "H"])

    def get_box(self):
        if self.exception:
            return
        prot = []
        for res in self.mol.chains.residues:
            if res.name[:3] in aa:
                prot.append(res)
        minimx = min([at.coords[0] for res in prot for at in res.atoms]) - 5
        minimy = min([at.coords[1] for res in prot for at in res.atoms]) - 5
        minimz = min([at.coords[2] for res in prot for at in res.atoms]) - 5
        maximx = max([at.coords[0] for res in prot for at in res.atoms]) + 5
        maximy = max([at.coords[1] for res in prot for at in res.atoms]) + 5
        maximz = max([at.coords[2] for res in prot for at in res.atoms]) + 5
        self.size = [int(maximx - minimx), int(maximy - minimy), int(maximz - minimz)]
        self.center = [(minimx + maximx) / 2, (minimy + maximy) / 2, (minimz + maximz) / 2]

    def get_ligand(self, sel, filename):
        selection = sel.split(':')
        new_mol = None
        for chain in self.mol.chains:
            for res in chain.residues:
                # exclude water residues
                if res.name[:3] in ['WAT', 'HOH', 'SOL', ' ZN']:
                    continue
                if selection == [chain.name, res.name[:3], res.name[3:]]:
                    new_mol = makeMoleculeFromAtoms('ligand', res.atoms)
                    writer = PdbWriter()
                    writer.write(filename, new_mol.allAtoms, records=['ATOM', 'HETATM'])
        return new_mol

    def get_center_selection(self, selection):
        # check if exist duplicate and deleted it
        res_list = []
        for x in selection.split(';'):
            x = str(x).strip()
            if x and not x in res_list:
                res_list.append(x)
        coords = []
        for res in res_list:
            res = res.split(':')
            for c in self.mol.chains:
                for mkres in self.mol.chains.residues:
                    if res == [c.name, mkres.name[:3], mkres.name[3:]]:
                        for at in mkres.atoms:
                            coords.append(at.coords)
        x = sum([c[0] for c in coords]) / (len(coords) * 1.0)
        y = sum([c[1] for c in coords]) / (len(coords) * 1.0)
        z = sum([c[2] for c in coords]) / (len(coords) * 1.0)
        self.selection_center = [x, y, z]
        for i in range(3):
            self.selection_center[i] = str(round(self.selection_center[i], 4))

    def get_gyrate(self):
        x = [at.coords[0] for at in self.mol.allAtoms if at.element != "H"]
        y = [at.coords[1] for at in self.mol.allAtoms if at.element != "H"]
        z = [at.coords[2] for at in self.mol.allAtoms if at.element != "H"]
        ref = [sum(x) / len(x), sum(y) / len(y), sum(z) / len(z)]
        xm = [((float(i) - ref[0]), (float(j) - ref[1]), (float(k) - ref[2])) for (i, j, k) in zip(x, y, z)]
        numerator = sum(i ** 2 + j ** 2 + k ** 2 for (i, j, k) in xm)
        rg = sqrt(numerator / len(x))
        '''Aspect ratio = 0.23 [Feinstein and Brylinski. Calculating an optimal box size for ligand docking and virtual 
            screening against experimental and predicted binding pockets. Journal of Cheminformatics (2015)]
            If we use the automatic way of detemination of the binding site of the ligand, then the aspect ratio 
            changes 0.21 (this difference results in an additional small margin)
        '''
        return rg / 0.21


# class PDBMap():
#     '''
#     pass pdb to map. store all ATOMS and HETATM
#     '''
#
#     def __init__(self, pdb_file):
#
#         self.pdb_map = dict()
#         self.pdb_file = pdb_file
#         self.pdb_list = self.pdb2map()
#         self.protein_only, self.hetero_only = self.parts()
#
#     def imp(self):
#         return self.protein_only, self.hetero_only
#
#     def atoms(self):
#         pass
#
#     def coord(self):
#         coord = []
#         for x in range(1, len(self.pdb_map) + 1):
#             coord.append([self.pdb_map[x]['element'], self.pdb_map[x]["x"], self.pdb_map[x]["y"], self.pdb_map[x]["z"]])
#         return coord
#
#     def pdb2map(self):
#         """
#         pass atoms and hetatm to map
#         :return:
#         """
#         FILE = open(self.pdb_file, 'r')
#         i = 1
#         for line in FILE:
#             line = line.strip('\n')
#             if not (re.search("ATOM", line[0:6]) or re.search("HETATM", line[0:6])):
#                 continue
#             if not self.pdb_map.has_key(i):
#                 self.pdb_map[i] = dict()
#
#             self.pdb_map[i]["id"] = line[0:6].strip()
#             self.pdb_map[i]["atom_number"] = line[6:11].strip()
#             self.pdb_map[i]["atom_name"] = line[12:16]
#             self.pdb_map[i]["alternate_location"] = line[16]
#             self.pdb_map[i]["three_letter_code"] = line[17:21].strip()
#             self.pdb_map[i]["chain"] = line[21].strip()
#             self.pdb_map[i]["residue_number"] = line[22:26].strip()
#             self.pdb_map[i]["i_code"] = line[26]
#             self.pdb_map[i]["x"] = line[27:38].strip()
#             self.pdb_map[i]["y"] = line[38:46].strip()
#             self.pdb_map[i]["z"] = line[46:54].strip()
#             self.pdb_map[i]["occupancy"] = line[54:60].strip()
#             self.pdb_map[i]["b_factor"] = line[60:66].strip()
#             self.element = [line[76:78].strip()][0]
#             if len(self.element) == 2:
#                 if re.search(r'[A-Za-z]', self.element[0]) and re.search(r'[A-Za-z]', self.element[1]):
#                     self.pdb_map[i]["element"] = self.element[0] + self.element[1]
#                 else:
#                     self.pdb_map[i]["element"] = self.element[0]
#             elif len(self.element) == 3:
#                 if re.search(r'[A-Za-z]', self.element[0]) and re.search(r'[A-Za-z]', self.element[1]):
#                     self.pdb_map[i]["element"] = self.element[0] + self.element[1]
#                 elif re.search(r'[A-Za-z]', self.element[1]) and re.search(r'[A-Za-z]', self.element[2]):
#                     self.pdb_map[i]["element"] = self.element[1] + self.element[2]
#                 else:
#                     self.pdb_map[i]["element"] = self.element[0]
#             else:
#                 self.pdb_map[i]["element"] = self.element
#             self.pdb_map[i]["charge"] = [line[76:81].strip()][1:2]
#             if self.pdb_map[i]["three_letter_code"] in hoh:
#                 del self.pdb_map[i]
#             else:
#                 i += 1
#         FILE.close()
#         return self.pdb_map
#
#     def parts(self):
#         """
#         extract both parts: atoms and hetatm
#         :return:
#         """
#         protein = []
#         hetero = []
#         for x in range(1, len(self.pdb_list) + 1):
#             if "ATOM" in self.pdb_list[x]['id']:
#                 protein.append(self.pdb_list[x])
#             elif "HETATM" in self.pdb_list[x]['id']:
#                 hetero.append(self.pdb_list[x])
#         return protein, hetero
#
#     def count_molecules(self):
#         self.n_count = []
#         self.nl_count = []
#         self.ch_count = []
#         self.m_count = []
#         self.lig_count = []
#         self.adcount = []
#         self.all = dict()
#         for dat in self.protein_only:
#             ##  # de cadenas diferentes
#             if dat['three_letter_code'] in aa:
#                 if not dat['chain'] in self.ch_count:
#                     self.ch_count.append(dat['chain'])
#                 self.all["protein"] = self.ch_count
#             elif dat['three_letter_code'] in na:
#                 if not dat['chain'] in self.n_count:
#                     self.n_count.append(dat['chain'])
#                 self.all["nucleic_acid"] = self.n_count
#         for het in self.hetero_only:
#             if het['three_letter_code'] in na:
#                 if not het['chain'] in self.nl_count:
#                     self.n_count.append(het['chain'])
#                     self.all["nucleic_acid_lig"] = self.nl_count
#             elif het['three_letter_code'] in glycosides:
#                 if not (het["chain"], het["three_letter_code"], het["residue_number"]) in self.adcount:
#                     self.adcount.append((het["chain"], het["three_letter_code"], het["residue_number"]))
#                 self.all["glycosides"] = self.adcount
#             elif het['three_letter_code'] in metal_prop.keys():
#                 if not (het["chain"], het["three_letter_code"], het["residue_number"]) in self.m_count:
#                     self.m_count.append((het["chain"], het["three_letter_code"], het["residue_number"]))
#                     self.all["metals"] = self.m_count
#             elif het['three_letter_code'] in hoh:
#                 continue
#             elif not het['three_letter_code'] in na + aa + glycosides + metal_prop.keys() + hoh:
#                 if not (het["chain"], het["three_letter_code"], het["residue_number"]) in self.lig_count:
#                     self.lig_count.append((het["chain"], het["three_letter_code"], het["residue_number"]))
#                     self.all["ligands"] = self.lig_count
#         return self.all


# class ClearAndFix():
#     '''
#     Eliminate Waters residues and build bond for protein and ligands
#     '''
#
#     def __init__(self, input_file):
#         self.input_file = input_file
#         mols = Read(self.input_file)
#         self.mol = mols[0]
#         other_hetatm = []
#
#         for atom in self.mol.allAtoms:
#             if 'ZN' not in atom.name and atom.hetatm == 1:
#                 other_hetatm.append(atom)
#         for a in other_hetatm:
#             for b in a.bonds:
#                 at2 = b.atom1
#                 if at2 == a: at2 = b.atom2
#                 at2.bonds.remove(b)
#                 a.bonds.remove(b)
#             a.parent.remove(a)
#             del a
#         self.mol.allAtoms = self.mol.chains.residues.atoms
#         os.remove(self.input_file)
#
#     def write(self):
#         writer = PdbqtWriter()
#         writer.write(self.input_file, self.mol.allAtoms, records=['ATOM', 'HETATM'])
class Convert:
    def __init__(self, filename):
        self.input_file = Read(filename)[0]
        self.output = filename.split('.')[0] + '.pdb'
        writer = PdbWriter()
        writer.write(self.output, self.input_file.allAtoms, records=['ATOM', 'HETATM'])

    def get_path(self):
        output = os.path.abspath(self.output)
        if os.path.exists(output):
            return output
class Fix_PQR:
    '''
    Add metal atom to PDB2PQR output
    '''
    def __init__(self, original_pdb, pqr_file, metals):
        self.ori_pdb = Read(original_pdb)[0]
        self.pqr = Read(pqr_file)[0]
        self.metals = metals
        self.new_pdb = pqr_file.split('.')[0] + '.pdb'

        uniq_list = {} # to avoid redundancy
        if self.metals:
            for met in self.metals:
                ele = met[1][:3].strip().lower()
                if ele not in list(uniq_list.keys()):
                    uniq_list[ele] = met[2]
                else:
                    continue
            met_atoms = self.ori_pdb.allAtoms.get(lambda x: x.element.lower() in uniq_list)
            for atm in met_atoms:
                atm.charge = uniq_list[atm.element.lower()]
                print('atoms charge', atm.element, uniq_list[atm.element.lower()])
            for met_atm in met_atoms:
                close_atoms = self.pqr.closerThan(met_atm.coords, self.pqr.allAtoms, 2.8)
            for a in close_atoms:
                if a.element == 'H':
                    for b in a.bonds:
                        at2 = b.atom1
                        if at2 == a: at2 = b.atom2
                        at2.bonds.remove(b)
                        a.bonds.remove(b)
                    a.parent.remove(a)
                    del a
                self.pqr.allAtoms = self.pqr.chains.residues.atoms
            self.pqr.allAtoms = self.pqr.chains.residues.atoms + met_atoms
        writer = PdbWriter()
        writer.write(self.new_pdb, self.pqr.allAtoms, records=['ATOM', 'HETATM'])


class Converter:
    def __init__(self, inputformat, inputfile, outputname):
        self.format = inputformat
        self.inputfile = inputfile
        self.output = outputname
        self.format2pdb()

    def format2pdb(self):
        mol = pybel.readfile(self.format, self.inputfile).next()
        if self.format == 'mol2':
            mol.write("pdb", 'temp.pdb', True)
            self.verify()
        else:
            mol.write('pdb', self.output, True)

    def verify(self):
        file = open('temp.pdb', 'r')
        out_file = open(self.output, 'w')
        count = 1
        for line in file:
            if not re.search("ATOM", line[0:6]) or re.search('HETATM', line[0:6]):
                continue
            self.id = line[0:6].strip()
            self.atom_number = str(count)
            self.atom_name = line[12:16]
            self.alternate_location = line[16]
            self.three_letter_code = "LIG"
            self.chain = "A"
            self.residue_number = "1"
            self.i_code = line[26]
            self.x = line[27:38].strip()
            self.y = line[38:46].strip()
            self.z = line[46:54].strip()
            self.occupancy = "1.000"
            self.b_factor = '0.000'
            self.element = [line[77:79].strip()][0]
            self.charge = [line[79].strip()][1:2]
            self.output_line = self.id.ljust(6) + self.atom_number.rjust(5) + self.atom_name.ljust(4) + " " + \
                               (self.three_letter_code).rjust(3) + " " + (self.chain) + \
                               (self.residue_number).rjust(4) + (self.x).rjust(12) + (self.y).rjust(8) + \
                               (self.z).rjust(8) + self.element.rjust(25) + '\n'
            count += 1
            out_file.write(self.output_line)
        file.close()
        out_file.close()
        os.remove('temp.pdb')
