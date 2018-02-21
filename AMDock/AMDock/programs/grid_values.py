from pymol.cgo import *                                                                                     
from pymol import cmd                                                                                       
import sys, getopt, re
from pymol.vfont import plain

try:
	opt_list, args = getopt.getopt(sys.argv[1:], 'c:s:p:')
except getopt.GetoptError, msg:
	pass

for o, a in opt_list:
    if o in ('-s', '--s'):
        size_x = int(a.split(',')[0])
        size_y = int(a.split(',')[1])
        size_z = int(a.split(',')[2])
    if o in ('-c', '--c'):
        obj_file = a
    if o in ('-p','--p'):
        prot = a

obj = open(obj_file)
for line in obj:
    line = line.strip('\n')
    if re.search('center_x', line):
        center_x = float(line.split()[-1])
    if re.search('center_y', line):
        center_y = float(line.split()[-1])
    if re.search('center_z', line):
        center_z = float(line.split()[-1])

def calculate_box():
    cylinder_size = 0.15
    size = [size_x, size_y, size_z]
    xmax = center_x + size[0]/2.
    xmin = center_x - size[0]/2.
    ymax = center_y + size[1]/2.
    ymin = center_y - size[1]/2.
    zmax = center_z + size[2]/2.
    zmin = center_z - size[2]/2.
    box_edge_x = [xmin,xmax]
    box_edge_y = [ymin,ymax]
    box_edge_z = [zmin,zmax]
    box_coords  = [box_edge_x,box_edge_y,box_edge_z]
    cmd.delete('ref_amdock_box')
    display_box(box_coords,cylinder_size)
    crisscross(center_x, center_y, center_z, 0.5)
    pymol_data = open('pymol_data.txt','w')
    pymol_data.write('%s %s %s %s %s %s %s'%(prot,size_x, size_y, size_z, center_x, center_y,center_z))
    pymol_data.close()

def display_box(box, cylinder_size):
        view = cmd.get_view()
        name = "ref_amdock_box"
        obj = []
        # build cgo object
        color = [1.05,0.15,1.5]
        for i in range(2):
            for k in range (2):
                for j in range(2):
                    if i != 1:
                        obj.append(CYLINDER)
                        obj.extend([box[0][i],box[1][j],box[2][k]])
                        obj.extend([box[0][i+1],box[1][j],box[2][k]])
                        obj.append(cylinder_size)
                        obj.extend(color)
                        obj.extend(color)
                        obj.append(COLOR)
                        obj.extend(color)
                        obj.append(SPHERE)
                        obj.extend([box[0][i],box[1][j],box[2][k],cylinder_size])

                    if j != 1:
                        obj.append(CYLINDER)
                        obj.extend([box[0][i],box[1][j],box[2][k]])
                        obj.extend([box[0][i],box[1][j+1],box[2][k]])
                        obj.append(cylinder_size)
                        obj.extend(color)
                        obj.extend(color)
                        obj.append(COLOR)
                        obj.extend(color)
                        obj.append(SPHERE)
                        obj.extend([box[0][i],box[1][j+1],box[2][k],cylinder_size])
                    if k != 1:
                        obj.append(CYLINDER)
                        obj.extend([box[0][i],box[1][j],box[2][k]])
                        obj.extend([box[0][i],box[1][j],box[2][k+1]])
                        obj.append(cylinder_size)
                        obj.extend(color)
                        obj.extend(color)
                        obj.append(COLOR)
                        obj.extend(color)
                        obj.append(SPHERE)
                        obj.extend([box[0][i],box[1][j],box[2][k+1],cylinder_size])
        cmd.load_cgo(obj,name)
        cmd.set_view(view)

def crisscross(x,y,z,d,name="ref_center"):
        obj = [
            LINEWIDTH, 3,
            COLOR, float(1.05), float(0.15), float(1.5),

            BEGIN, LINE_STRIP,
            VERTEX, float(x-d), float(y), float(z),
            VERTEX, float(x+d), float(y), float(z),
            END,

            BEGIN, LINE_STRIP,
            VERTEX, float(x), float(y-d), float(z),
            VERTEX, float(x), float(y+d), float(z),
            END,

            BEGIN, LINE_STRIP,
            VERTEX, float(x), float(y), float(z-d),
            VERTEX, float(x), float(y), float(z+d),
            END

            ]
        view = cmd.get_view()
        cmd.load_cgo(obj,name)
        cmd.set_view(view)
calculate_box()
