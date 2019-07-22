from MolKit import Read
from MolKit.pdbWriter import PdbWriter,PdbqtWriter
import re
from math import sqrt
import os
import subprocess
from AMDock.variables import WorkersAndScripts



atom_prop ={"AL":26.9815,"Al":26.9815,"AR": 39.948,"Ar": 39.948,"AU":196.97,"Au": 196.97,"Br":78.9183, "BR": 78.9183,
            "C": 12,"Ca":39.9625906, "CA": 39.9625906,"Cl":34.968852721, "CL": 34.968852721,"Cs":132.90, "CS": 132.90,
            "D": 2.014101779,"F": 18.998,"Fe": 53.9396127,"FE": 53.9396127,"Ge":72.64, "GE": 72.64,"H": 1.007825035,
            "He": 4.0026, "HE": 4.0026,"Hg": 200.6, "HG": 200.6,"I": 126.90447,"In":114.8,"IN": 114.8,"K": 39.102,
            "Mg":24.30,"MG": 24.30,"N": 14.006723,"Na":22.99,"NA": 22.99,"Ne":20.180,"NE": 20.180,"O": 15.99491463,
            "P": 30.9737620,"Pb":207.2,"PB": 207.2,"Rb": 85.47, "RB": 85.47,"S": 31.97207070,"Si":28.0855,"SI": 28.0855,
            "Sr":87.62,"SR": 87.62,"Ti":47.87,"TI": 47.87,"Tl":11.85,"TL": 11.85,"Zn":63.9291448, "ZN": 63.9291448,
            "Co":58.933200, "CO":58.933200}
metal_prop = {'MG': [2.000,1.700],'AL': [3.000,2.05],'SI': [4.000,2.000],'CA': [2.000,1.973],'MN': [2.000,1.700],
              'FE': [2.000,1.700],'CO': [2.000,1.700],'NI': [3.000,1.700],'CU': [2.000,1.700],'ZN':[2.000,1.70],
              'Mg': [2.000, 1.700],'Al': [3.000, 2.05],'Si': [4.000, 2.000],'Ca': [2.000, 1.973],'Mn': [2.000, 1.700],
              'Fe': [2.000, 1.700],'Co': [2.000, 1.700],'Ni': [3.000, 1.700],'Cu': [2.000, 1.700],'Zn': [2.000, 1.70]}




aa = ['CYS','ILE','SER','VAL','GLN','LYS','ASN','PRO','THR','PHE','ALA','HIS','GLY','ASP','LEU','ARG','TRP','GLU','TYR',
      'MET','HID','HSP','HIE','HIP','CYX','CSS', 'ALA']
aa1 = ['C','I','S','V','Q','K','N','P','T','F','H','G','D', 'L', 'R', 'W', 'E', 'Y', 'M', 'A']
na = ['DC','DG','DA','DT','DU']
glycosides = ['NAG','BGLN', 'FUC', 'AFUC', 'MAN', 'AMAN', 'BMA', 'BMAN']
hoh = ['HOH','WAT','TIP3','TIP4']
metal = ['Zn','CA','MG','FE','CO',]

hter =['A','BES',1024]


class PDBMap():
    '''
    pass pdb to map. store all ATOMS and HETATM
    '''
    def __init__(self,pdb_file):

        self.pdb_map = dict()
        self.pdb_file = pdb_file
        self.pdb_list = self.pdb2map()
        self.protein_only,self.hetero_only = self.parts()
        #self.coord()
    def imp(self):
        return self.protein_only,self.hetero_only

        #self.count_molecules()
    def atoms(self):
        pass

    def coord(self):
        #rint len(self.pdb_map)
        coord = []

        for x in range(1,len(self.pdb_map)+1):
            coord.append([self.pdb_map[x]['element'],self.pdb_map[x]["x"],self.pdb_map[x]["y"],self.pdb_map[x]["z"]])
        return coord
    def pdb2map(self):
        """
        pass atoms and hetatm to map
        :return:
        """
        FILE = open(self.pdb_file, 'r')
        i = 1
        for line in FILE:
            line = line.strip('\n')
            if not (re.search("ATOM", line[0:6]) or re.search("HETATM", line[0:6])):
                continue
            if not self.pdb_map.has_key(i):
                self.pdb_map[i] = dict()

            self.pdb_map[i]["id"] = line[0:6].strip()
            self.pdb_map[i]["atom_number"] = line[6:11].strip()
            self.pdb_map[i]["atom_name"] = line[12:16]
            self.pdb_map[i]["alternate_location"] = line[16]
            self.pdb_map[i]["three_letter_code"] = line[17:21].strip()
            self.pdb_map[i]["chain"] = line[21].strip()
            self.pdb_map[i]["residue_number"] = line[22:26].strip()
            self.pdb_map[i]["i_code"] = line[26]
            self.pdb_map[i]["x"] = line[27:38].strip()
            self.pdb_map[i]["y"] = line[38:46].strip()
            self.pdb_map[i]["z"] = line[46:54].strip()
            self.pdb_map[i]["occupancy"] = line[54:60].strip()
            self.pdb_map[i]["b_factor"] = line[60:66].strip()
            self.element = [line[76:78].strip()][0]
            if len(self.element) == 2:
                if re.search(r'[A-Za-z]', self.element[0]) and re.search(r'[A-Za-z]', self.element[1]):
                    self.pdb_map[i]["element"] = self.element[0]+self.element[1]
                else:
                    self.pdb_map[i]["element"] = self.element[0]
            elif len(self.element) == 3:
                if re.search(r'[A-Za-z]', self.element[0]) and re.search(r'[A-Za-z]', self.element[1]):
                    self.pdb_map[i]["element"] = self.element[0] + self.element[1]
                elif re.search(r'[A-Za-z]', self.element[1]) and re.search(r'[A-Za-z]', self.element[2]):
                    self.pdb_map[i]["element"] = self.element[1] + self.element[2]
                else:
                    self.pdb_map[i]["element"] = self.element[0]
            else:
                self.pdb_map[i]["element"] = self.element
            self.pdb_map[i]["charge"] = [line[76:81].strip()][1:2]
            if self.pdb_map[i]["three_letter_code"] in hoh:
                del self.pdb_map[i]
            else:
                i += 1
        FILE.close()
        return self.pdb_map

    def parts(self):
        """
        extract both parts: atoms and hetatm
        :return:
        """
        protein = []
        hetero = []
        for x in range(1, len(self.pdb_list)+1):
            if "ATOM" in self.pdb_list[x]['id']:
                protein.append(self.pdb_list[x])
            elif "HETATM" in self.pdb_list[x]['id']:
                hetero.append(self.pdb_list[x])
        return protein, hetero

    def count_molecules(self):
        self.n_count = []
        self.nl_count = []
        self.ch_count = []
        self.m_count = []
        self.lig_count = []
        self.adcount = []
        self.all =dict()
        for dat in self.protein_only:
              ##  # de cadenas diferentes
            if dat['three_letter_code'] in aa:
                if not dat['chain'] in self.ch_count:
                    self.ch_count.append(dat['chain'])
                self.all["protein"] = self.ch_count
            elif dat['three_letter_code'] in na:
                if not dat['chain'] in self.n_count:
                     self.n_count.append(dat['chain'])
                self.all["nucleic_acid"] = self.n_count
        for het in self.hetero_only:
            if het['three_letter_code'] in na:
                if not het['chain'] in self.nl_count:
                    self.n_count.append(het['chain'])
                    self.all["nucleic_acid_lig"]= self.nl_count
            elif het['three_letter_code'] in glycosides:
                if not (het["chain"],het["three_letter_code"],het["residue_number"]) in self.adcount:
                    self.adcount.append((het["chain"],het["three_letter_code"],het["residue_number"]))
                self.all["glycosides"]= self.adcount
            elif het['three_letter_code'] in metal_prop.keys():
                if not (het["chain"],het["three_letter_code"],het["residue_number"]) in self.m_count:
                    self.m_count.append((het["chain"],het["three_letter_code"],het["residue_number"]))
                    self.all["metals"] = self.m_count
            elif het['three_letter_code'] in hoh:
                continue
            elif not het['three_letter_code'] in na+aa+glycosides+metal_prop.keys()+hoh:
                if not (het["chain"],het["three_letter_code"],het["residue_number"]) in self.lig_count:
                    self.lig_count.append((het["chain"],het["three_letter_code"],het["residue_number"]))
                    self.all["ligands"] = self.lig_count
        return self.all

class ClearAndFix():
    '''
    Eliminate Waters residues and build bond for protein and ligands
    '''
    def __init__(self,input_file):
        self.input_file = input_file
        mols = Read(self.input_file)
        self.mol = mols[0]
        other_hetatm = []

        for atom in self.mol.allAtoms:
            if 'ZN' not in atom.name and atom.hetatm == 1:
                other_hetatm.append(atom)
        for a in other_hetatm:
            for b in a.bonds:
                at2 = b.atom1
                if at2 == a: at2 = b.atom2
                at2.bonds.remove(b)
                a.bonds.remove(b)
            a.parent.remove(a)
            del a
        self.mol.allAtoms = self.mol.chains.residues.atoms
        os.remove(self.input_file)
    def write(self):
        writer = PdbqtWriter()
        writer.write(self.input_file, self.mol.allAtoms, records=['ATOM','HETATM'])




class Fix_PQR:
    '''
    Add metal atom to PDB2PQR output
    '''
    def __init__(self, original_pdb, pqr_file,metal=False):
        self.pdb_filename = original_pdb
        self.pqr_file = pqr_file
        self.ismetallop = metal

        self.new_pdb_filename = self.pqr_file.split('.')[0]+'.pdb'

        self.pdb_map = dict()
        self.pqr_map = dict()
        self.read_Atom_Hetatm_PDB_into_map()
        self.read_Atom_Hetatm_PQR_into_map()
        if self.ismetallop:
            self.hetatm_to_pqr()
            self.metal_close_atoms()
        self.save_PDB(self.new_pdb_filename)

        #os.remove('temp.pdb')

    def metal_close_atoms(self):
        '''
		Fix hydrogen bonds near from metal atom
        '''
        for n in range(1,len(self.pdb_map)+1):
            metal_coord = [self.pdb_map[n]['x'],self.pdb_map[n]['y'],self.pdb_map[n]['z']]
            for m in range(1,len(self.pqr_map)+1):
                if self.pqr_map[m]['atom_name'] == self.pdb_map[n]['atom_name']:
                    continue
                all_coord = [self.pqr_map[m]['x'],self.pqr_map[m]['y'],self.pqr_map[m]['z']]
                distance = self.dist(metal_coord, all_coord)
                if distance <= 2.5 and distance > 0:
                    if self.pqr_map[m]['element'] == 'H':
                        self.pqr_map.pop(m)
        return self.pqr_map

    def dist(self, coords1, coords2):
        """
		return distance between two atoms, a and b.
        """
        def cuad(j):
            return j ** 2
        def resta_coord(n, m):
            return float(m) - float(n)
        def suma_coord(h, i):
            return h + i
        resta = map(resta_coord, coords1, coords2)
        cuadrado = map(cuad, resta)
        sum = reduce(suma_coord, cuadrado)
        return sqrt(sum)

    def read_Atom_Hetatm_PDB_into_map(self):

        FILE = open(self.pdb_filename, 'r')
        i = 1
        for line in FILE:
            line = line.strip('\n')
            if not re.search("HETATM", line[0:6]):
                continue
            if not self.pdb_map.has_key(i):
                self.pdb_map[i] = dict()

            self.pdb_map[i]["atom_name"] = line[12:16].strip()
            if not self.pdb_map[i]['atom_name'] in metal_prop.keys():
                self.pdb_map.pop(i)
                continue

            self.pdb_map[i]["id"] = line[0:6].strip()
            self.pdb_map[i]["atom_number"] = line[6:11].strip()
            self.pdb_map[i]["alternate_location"] = line[16]
            self.pdb_map[i]["three_letter_code"] = line[17:21].strip()
            self.pdb_map[i]["chain"] = line[21].strip()
            self.pdb_map[i]["residue_number"] = line[22:26].strip()
            self.pdb_map[i]["i_code"] = line[26]
            self.pdb_map[i]["x"] = line[27:38].strip()
            self.pdb_map[i]["y"] = line[38:46].strip()
            self.pdb_map[i]["z"] = line[46:54].strip()
            self.pdb_map[i]["charge"] = metal_prop[self.pdb_map[i]['atom_name']][0]
            self.pdb_map[i]["vdW"] = metal_prop[self.pdb_map[i]['atom_name']][1]
            self.element = line[76:78].strip()
            if len(self.element) == 2:
                if re.search(r'[A-Za-z]', self.element[0]) and re.search(r'[A-Za-z]', self.element[1]):
                    self.pdb_map[i]["element"] = self.element[0]+self.element[1]
                else:
                    self.pdb_map[i]["element"] = self.element[0]
            elif len(self.element) == 3:
                if re.search(r'[A-Za-z]', self.element[0]) and re.search(r'[A-Za-z]', self.element[1]):
                    self.pdb_map[i]["element"] = self.element[0] + self.element[1]
                elif re.search(r'[A-Za-z]', self.element[1]) and re.search(r'[A-Za-z]', self.element[2]):
                    self.pdb_map[i]["element"] = self.element[1] + self.element[2]
                else:
                    self.pdb_map[i]["element"] = self.element[0]
            else:
                self.pdb_map[i]["element"] = self.element
            i += 1
        FILE.close()
        return self.pdb_map

    def read_Atom_Hetatm_PQR_into_map(self):

        FILE = open(self.pqr_file, 'r')
        i = 1
        for line in FILE:
            line = line.strip('\n')
            if not re.search("ATOM", line[0:6]):
                continue
            if not self.pqr_map.has_key(i):
                self.pqr_map[i] = dict()

            self.pqr_map[i]["id"] = line[0:6].strip()
            self.pqr_map[i]["atom_number"] = line[6:11].strip()
            self.pqr_map[i]["atom_name"] = line[11:16].strip()
            self.pqr_map[i]["alternate_location"] = line[16]
            self.pqr_map[i]["three_letter_code"] = line[17:21].strip()
            self.pqr_map[i]["chain"] = line[21:22]
            self.pqr_map[i]["residue_number"] = line[22:26].strip()
            self.pqr_map[i]["x"] = line[27:38].strip()
            self.pqr_map[i]["y"] = line[38:46].strip()
            self.pqr_map[i]["z"] = line[46:54].strip()
            self.pqr_map[i]["charge"] = line[55:62].strip()
            self.pqr_map[i]["vdW"] = line[64:70].strip()
            self.pqr_map[i]['element'] = self.pqr_map[i]['atom_name'][0]

            i += 1
        FILE.close()
        self.j = i
        return self.pqr_map

    def hetatm_to_pqr(self):

        temp_pdb_map = self.pdb_map.copy()
        for num in temp_pdb_map:
            self.pqr_map[self.j] = dict()
            self.pqr_map[self.j]["id"] = self.pdb_map[num]["id"]
            self.pqr_map[self.j]["atom_name"] = " " + self.pdb_map[num]["atom_name"]
            self.pqr_map[self.j]["atom_number"] = `self.j`
            self.pqr_map[self.j]["three_letter_code"] = self.pdb_map[num]["three_letter_code"]
            self.pqr_map[self.j]["chain"] = self.pdb_map[num]["chain"]
            self.pqr_map[self.j]["residue_number"] = self.pdb_map[num]["residue_number"]
            self.pqr_map[self.j]["x"] = self.pdb_map[num]["x"]
            self.pqr_map[self.j]["y"] = self.pdb_map[num]["y"]
            self.pqr_map[self.j]["z"] = self.pdb_map[num]["z"]
            self.pqr_map[self.j]["charge"] = self.pdb_map[num]['charge']
            self.pqr_map[self.j]["vdW"] = self.pdb_map[num]['vdW']
            self.pqr_map[self.j]['element'] = self.pdb_map[num]['element']

            self.j += 1

    def save_PDB(self, filename):

        FILE = open(filename, 'w')
        for line_number in self.pqr_map:
            line = self.morph_line_in_pdb_map_to_pdb_line(line_number)
            FILE.write(line + "\n")

        FILE.close()
        return filename

    def morph_line_in_pdb_map_to_pdb_line(self, line_num):
        # Create the PDB line.

        line = (self.pqr_map[line_num]['id']).ljust(6) + (self.pqr_map[line_num]['atom_number']).rjust(5) + \
               ((self.pqr_map[line_num]['atom_name']).ljust(3)).rjust(5) + " " + (self.pqr_map[line_num]['three_letter_code']).rjust(3)\
               + " " + (self.pqr_map[line_num]["chain"]) + (self.pqr_map[line_num]['residue_number']).rjust(4)\
               + (self.pqr_map[line_num]['x']).rjust(12) + (self.pqr_map[line_num]['y']).rjust(8) + \
               (self.pqr_map[line_num]['z']).rjust(8) + (self.pqr_map[line_num]["element"]).rjust(24)
        return line

def dist(coords1, coords2):
    """
	return distance between two atoms, a and b.
    """
    def cuad(j):
        return j**2
    def resta_coord(n,m):
        return m-n
    def suma_coord(h,i):
        return h+i
    resta = map(resta_coord, coords1, coords2)
    cuadrado = map(cuad,resta)
    sum = reduce(suma_coord, cuadrado)
    return sqrt(sum)


residues = ['A:LEU:85','A:VAL:83']


class GridDefinition(PDBMap):
    """
    define box based on selection
    """
    def __init__(self, pdb_filename, residues_select=None, ligand_select=None, gd_file = None,size = True):

        PDBMap.__init__(self,pdb_filename)
        #self.file = pdb_filename

        self.res_sel = residues_select
        self.lig_sel = ligand_select

        self.gd_file = gd_file
        self.size = size

        self.protein_only, self.ligands_only = PDBMap.imp(self)#self.parts()
        self.selection = self.select_list()
        try:
            self.minimun = self.minim()
            self.maximun = self.maxim()
            self.extent = map(lambda m, n: (n+1) - (m-1), self.minimun, self.maximun)
            self.imprime()
        except:
            pass

    def imprime(self):
        self.output = {'center': self.geom_center(), 'size': self.extent}
        if self.gd_file != None:
            file =open(self.gd_file,'w')
            file.write('center_x = %.3f\n'%self.geom_center()[0])
            file.write('center_y = %.3f\n'%self.geom_center()[1])
            file.write('center_z = %.3f\n'%self.geom_center()[2])
            if self.size:
                file.write('size_x = %d\n'%self.extent[0])
                file.write('size_y = %d\n'%self.extent[1])
                file.write('size_z = %d\n'%self.extent[2])
            file.close()

        # return self.output
    def check_select(self):
        if self.res_sel != None:
            self.errors = None
            self.msg = ""
            if re.search(",", self.res_sel):
                self.res_list = self.res_sel.split(',')
            elif re.search(';', self.res_sel):
                self.res_list = self.res_sel.split(';')
            elif re.search('/', self.res_sel):
                self.res_list = self.res_sel.split('/')
            elif re.search('|', self.res_sel):
                self.res_list = self.res_sel.split('|')
            contador = 0
            for resid in self.res_list:
                residue = resid.split(":")
                for coord in self.protein_only:
                    if coord['chain'] == str(residue[0]).strip() and coord['three_letter_code'] == str(residue[1]).strip() and \
                                    coord['residue_number'] == str(residue[2]).strip():
                        self.errors = 0
                        contador +=1
                        break
                    else:
                        self.errors = 1
            if contador == len(self.res_list):
                return 0
            else:
                return 1


    def select_list(self):
        if self.res_sel == None and self.lig_sel == None:
            return self.protein_only
        elif self.res_sel != None:
            self.res_list = []
            for resid in self.res_sel.split(","):
                residue = resid.split(":")
                for coord in self.protein_only:
                    if coord['chain'] == residue[0] and coord['three_letter_code'] == residue[1] and \
                                    coord['residue_number'] == residue[2]:
                        self.res_list.append(coord)
            return self.res_list
        else:
            self.lig_list = []
            self.lig_sel = self.lig_sel.split(":")
            for coord in self.ligands_only:
                if coord['chain'] == self.lig_sel[0] and coord['three_letter_code'] == self.lig_sel[1] and \
                                coord["residue_number"] == self.lig_sel[2]:
                    self.lig_list.append(coord)
            return self.lig_list

    def minim(self):
        minimx = float(self.selection[0]['x'])
        minimy = float(self.selection[0]['y'])
        minimz = float(self.selection[0]['z'])
        for x in self.selection:
            if float(x['x']) < minimx:
                minimx = float(x['x'])
            if float(x['y']) < minimy:
                minimy = float(x['y'])
            if float(x['z']) < minimz:
                minimz = float(x['z'])
        return minimx, minimy, minimz

    def maxim(self):
        maxx = float(self.selection[0]['x'])
        maxy = float(self.selection[0]['y'])
        maxz = float(self.selection[0]['z'])
        for x in self.selection:
            if float(x['x']) > maxx:
                maxx = float(x['x'])
            if float(x['y']) > maxy:
                maxy = float(x['y'])
            if float(x['z']) > maxz:
                maxz = float(x['z'])
        return maxx, maxy, maxz

    def geom_center(self):
        num_atm_select = 0
        countx = county = countz = 0
        for coord in self.selection:
            countx = countx + float(coord['x'])
            county = county + float(coord['y'])
            countz = countz + float(coord['z'])
        return countx/len(self.selection), county / len(self.selection), countz / len(self.selection)

class HeavyAtoms():
    def __init__(self,ligand_file):
        self.mols= Read(ligand_file)

    def imp(self):
        try:
            self.mol = self.mols[0]
            self.mol_atoms = self.mol.allAtoms
            self.heavy = self.mol_atoms.get(lambda x: x.element != 'H')
            return len(self.heavy)
        except:
            return None

class Converter:
    def __init__(self,obabel, inputformat, inputfile, outputname):
        self.format = inputformat
        self.inputfile = inputfile
        self.output = outputname
        self.obabel = obabel

    def format2pdb(self):
        # mol = pybel.readfile(self.format, self.inputfile).next()
        print [self.obabel, "-i", self.format, self.inputfile, "-o", 'pdb', "-O",self.output]
        if self.format == 'mol2':
            c2 = subprocess.Popen([self.obabel, "-i", self.format, self.inputfile, "-o", 'pdb', "-O",'temp.pdb'],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            print c2.wait()
            if c2.wait():
                return c2.wait()
            else:
                self.verify()
                return c2.wait()
        else:
            c2 = subprocess.Popen([self.obabel, "-i", self.format, self.inputfile, "-o", 'pdb', "-O",self.output],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            return c2.wait()
    def verify(self):
        file = open('temp.pdb','r')
        out_file = open(self.output,'w')
        count = 1
        for line in file:
            if not re.search("ATOM",line[0:6]) or re.search('HETATM',line[0:6]):
                continue
            self.id = line[0:6].strip()
            self.atom_number = `count`
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
                                (self.z).rjust(8) + self.element.rjust(25)+'\n'
            count+=1
            out_file.write(self.output_line)
        file.close()
        out_file.close()
        os.remove('temp.pdb')

# class AddHLigand:
#     '''
#     Add hygrogens to ligand
#     '''
#     def __init__(self,obabel,inputformat,ligand_file,outputname,pH):
#         self.format = inputformat
#         self.ligand = ligand_file
#         self.pH_lig = pH
#         self.output = outputname
#         self.obabel = obabel
#         self.protonate()
#     def protonate(self):
#         mol = pybel.readfile(self.format,self.ligand).next()
#         mol.OBMol.AddHydrogens(False,True,self.pH_lig)
#         mol.write('pdb',self.output)

class Gyrate(PDBMap):
    def __init__(self,pdb_file):
        PDBMap.__init__(self,pdb_file)
        #self.pdb_file = pdb_file
        # self.gyrate()

    def gyrate(self):
        self.coord = PDBMap.coord(self)
        # mass = []
        xyz = []
        d = 0
        for atom in self.coord:
            d += 1
            if 'H' in atom[0]:
                continue
            xyz.append(atom[1:])
            # mass.append(atom_prop[atom[0]])
        countx = 0
        county = 0
        countz = 0
        for r in xyz:
            countx = countx + float(r[0])
            county = county + float(r[1])
            countz = countz + float(r[2])
        ref = [countx /len(xyz), county / len(xyz), countz /len(xyz)]
        xm = [((float(i)-ref[0]),(float(j)-ref[1]),(float(k)-ref[2])) for (i, j, k) in xyz]
        numerator = sum(i** 2 + j** 2 + k** 2 for (i,j,k) in xm)
        rg = sqrt(numerator / len(xyz))
        '''Aspect ratio = 0.23 [Feinstein and Brylinski. Calculating an optimal box size for ligand docking and virtual 
            screening against experimental and predicted binding pockets. Journal of Cheminformatics (2015)]
            If we use the automatic way of deteminacion of the binding site of the ligand, then the aspect ratio changes 
            0.21 (this difference results in an additional small margin)
        '''
        return rg/0.21




