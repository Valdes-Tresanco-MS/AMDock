from pymol.cgo import *
from pymol import cmd
from pymol.preset import *
import argparse

# colors
color = ['gray90', 'blue', 'tv_blue', 'marine', 'slate', 'lightblue', 'bluewhite', 'deepteal', 'skyblue', 'purpleblue',
         'deepblue', 'green']
color1 = ['palecyan', 'red', 'tv_red', 'raspberry', 'darksalmon', 'salmon', 'deepsalmon', 'warmpink', 'firebrick',
          'firebrick', 'chocolate', 'magenta']

parser = argparse.ArgumentParser()
parser.add_argument('--f_prot', default=None)  # pdb file
parser.add_argument('--f_prot_type', default=None)  # target or offtarget
parser.add_argument('--f_rep_type', type=int, default=3)  # only box
parser.add_argument('--f_center', type=float, default=None, nargs='+')
parser.add_argument('--f_size', type=int, default=None, nargs='+')
# rep_type == 3: None, rep_type == 2: lig, rep_type == 1: fill, # rep_type == 0: fill.pdb; ...; filln.pdb
parser.add_argument('--f_ligands', default=None, nargs='+')
parser.add_argument('--f_residues', default=None)  # only rep_type == 1
parser.add_argument('--s_prot', default=None)
parser.add_argument('--s_prot_type', default=None)
parser.add_argument('--s_rep_type', type=int, default=3)
parser.add_argument('--s_center', type=float, default=None, nargs='+')
parser.add_argument('--s_size', type=int, default=None, nargs='+')
parser.add_argument('--s_ligands', default=None, nargs='+')
parser.add_argument('--s_residues', default=None)
args = parser.parse_args()

firts_prot = {'prot_pdb': args.f_prot, 'prot_type': args.f_prot_type, 'rep_type': args.f_rep_type, 'center':
    args.f_center, 'size': args.f_size, 'ligands': args.f_ligands, 'residues': args.f_residues, 'colors': color}
sec_prot = {'prot_pdb': args.s_prot, 'prot_type': args.s_prot_type, 'rep_type': args.s_rep_type, 'center':
    args.s_center, 'size': args.s_size, 'ligands': args.s_ligands, 'residues': args.s_residues, 'colors': color1}


def calculate_box(x, y, z, xpts, ypts, zpts, prot):
    cylinder_size = 0.15
    xmax = x + xpts / 2.
    xmin = x - xpts / 2.
    ymax = y + ypts / 2.
    ymin = y - ypts / 2.
    zmax = z + zpts / 2.
    zmin = z - zpts / 2.
    box_edge_x = [xmin, xmax]
    box_edge_y = [ymin, ymax]
    box_edge_z = [zmin, zmax]
    box_coords = [box_edge_x, box_edge_y, box_edge_z]

    cmd.delete('%s_ref_box' % prot[0].upper())
    cmd.delete('%s_ref_center' % prot[0].upper())
    display_box(box_coords, cylinder_size, prot)
    crisscross(x, y, z, 0.5, '%s_ref_center' % prot[0].upper())
    cmd.zoom('%s_ref_box' % prot[0].upper(), 15)  # zoom to box


def display_box(box, cylinder_size, prot):
    view = cmd.get_view()
    name = "%s_ref_box" % prot[0].upper()
    obj = []
    color = [1.00, 0.80, 0.80] if prot != 'Target' else [1.05, 0.15, 1.5]
    for i in range(2):
        for k in range(2):
            for j in range(2):
                if i != 1:
                    obj.append(CYLINDER)
                    obj.extend([box[0][i], box[1][j], box[2][k]])
                    obj.extend([box[0][i + 1], box[1][j], box[2][k]])
                    obj.append(cylinder_size)
                    obj.extend(color)
                    obj.extend(color)
                    obj.append(COLOR)
                    obj.extend(color)
                    obj.append(SPHERE)
                    obj.extend([box[0][i], box[1][j], box[2][k], cylinder_size])

                if j != 1:
                    obj.append(CYLINDER)
                    obj.extend([box[0][i], box[1][j], box[2][k]])
                    obj.extend([box[0][i], box[1][j + 1], box[2][k]])
                    obj.append(cylinder_size)
                    obj.extend(color)
                    obj.extend(color)
                    obj.append(COLOR)
                    obj.extend(color)
                    obj.append(SPHERE)
                    obj.extend([box[0][i], box[1][j + 1], box[2][k], cylinder_size])
                if k != 1:
                    obj.append(CYLINDER)
                    obj.extend([box[0][i], box[1][j], box[2][k]])
                    obj.extend([box[0][i], box[1][j], box[2][k + 1]])
                    obj.append(cylinder_size)
                    obj.extend(color)
                    obj.extend(color)
                    obj.append(COLOR)
                    obj.extend(color)
                    obj.append(SPHERE)
                    obj.extend([box[0][i], box[1][j], box[2][k + 1], cylinder_size])
    cmd.load_cgo(obj, name)
    cmd.set_view(view)


def crisscross(x, y, z, d, name="ref_center"):
    obj = [
        LINEWIDTH, 3,
        COLOR, float(1.05), float(0.15), float(1.5),

        BEGIN, LINE_STRIP,
        VERTEX, float(x - d), float(y), float(z),
        VERTEX, float(x + d), float(y), float(z),
        END,

        BEGIN, LINE_STRIP,
        VERTEX, float(x), float(y - d), float(z),
        VERTEX, float(x), float(y + d), float(z),
        END,

        BEGIN, LINE_STRIP,
        VERTEX, float(x), float(y), float(z - d),
        VERTEX, float(x), float(y), float(z + d),
        END

    ]
    if name[0] == 'O':
        obj[3:6] = [float(1.00), float(0.80), float(0.80)]
    view = cmd.get_view()
    cmd.load_cgo(obj, name)
    cmd.set_view(view)


def load_rep(prot):
    cmd.load(prot['prot_pdb'], prot['prot_type'])  # load protein
    cmd.show('cartoon', prot['prot_type'])  # representation
    cmd.show('sticks', 'hetatm')
    cmd.show('sphere', 'resn ZN')
    cmd.hide('lines', prot['prot_type'])  # representation
    cmd.color(prot['colors'][0], prot['prot_type'])  # color
    if prot['rep_type'] == 0:
        pymol_sel = '%s or ' % prot['prot_type']
        prot['ligands'].sort()
        for lign, lig in enumerate(prot['ligands'], start=1):
            cmd.load(lig, '%s_FILL_%s' % (prot['prot_type'][0], lign))  # load ligand
            if lign < len(prot['ligands']):
                pymol_sel += '%s_FILL_%s or ' % (prot['prot_type'][0], lign)
            else:
                pymol_sel += '%s_FILL_%s' % (prot['prot_type'][0], lign)
        ligand_sites_trans(pymol_sel)
        cmd.hide("sticks", prot['prot_type'])
        cmd.hide("ribbon", prot['prot_type'])
        cmd.show('cartoon', prot['prot_type'])
        cmd.delete('polar_contacts')
        cmd.color(prot['colors'][0], prot['prot_type'])  # redundant? is needed because ligand_sites_trans
        for lign in range(len(prot['ligands'])):
            cmd.color(prot['colors'][lign + 1], '%s_FILL_%s' % (prot['prot_type'][0], lign + 1))
            # cmd.zoom('%s_ref_center'  % prot['prot_type'][0].upper(), 15, animate=1) # zoom to selected fill

    elif prot['rep_type'] == 1:
        cmd.load(prot['ligands'][0], '%s_FILL' % prot['prot_type'][0])  # load ligand
        cmd.color('cyan', '%s_FILL' % prot['prot_type'][0])
        cmd.hide('lines', '%s_FILL' % prot['prot_type'][0])
        cmd.show('dots', '%s_FILL' % prot['prot_type'][0])
        res_list = []
        for x in prot['residues'].split(';'):
            x = str(x).strip()
            if x and x not in res_list:
                res_list.append(x)
        for res in res_list:
            chain, resi, num = res.split(':')
            cmd.show('sticks', 'chain %s and resi %s' % (chain, num))
            if prot['colors'][-1] == 'green':
                util.cbag('chain %s and resi %s' % (chain, num))
            else:
                util.cbam('chain %s and resi %s' % (chain, num))
            # cmd.zoom('%s_FILL' % prot['prot_type'][0], 15, animate=1)

    elif prot['rep_type'] == 2:
        cmd.load(prot['ligands'][0], '%s_ligand' % prot['prot_type'][0])
        cmd.show('sticks', '%s_ligand' % prot['prot_type'][0])
        if prot['colors'][-1] == 'green':
            util.cbag('%s_ligand' % prot['prot_type'][0])
        else:
            util.cbam('%s_ligand' % prot['prot_type'][0])
        # cmd.zoom('%s_ligand' % prot['prot_type'][0], 15, animate=1)
    calculate_box(prot['center'][0], prot['center'][1], prot['center'][2], prot['size'][0], prot['size'][1],
                  prot['size'][2], prot['prot_type'])


pymol_data = open('pymol_data.txt', 'w')
#
if firts_prot['prot_pdb']:
    load_rep(firts_prot)
    pymol_data.write('%s %s %s %s %s %s %s\n' % (firts_prot['prot_type'].lower(), firts_prot['center'][0],
                                                 firts_prot['center'][1], firts_prot['center'][2],
                                                 firts_prot['size'][0],
                                                 firts_prot['size'][1], firts_prot['size'][2]))
if sec_prot['prot_pdb']:
    load_rep(sec_prot)
    pymol_data.write('%s %s %s %s %s %s %s\n' % (sec_prot['prot_type'].lower(), sec_prot['center'][0],
                                                 sec_prot['center'][1], sec_prot['center'][2], sec_prot['size'][0],
                                                 sec_prot['size'][1], sec_prot['size'][2]))
pymol_data.close()
