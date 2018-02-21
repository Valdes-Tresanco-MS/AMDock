import sys, getopt

opt_list = None
protein = None
size_x, size_y, size_z = 30,30,30
try:
    opt_list, args = getopt.getopt(sys.argv[1:], 'p:s:')
except getopt.GetoptError, msg:
    pass
if opt_list != None:
    for o, a in opt_list:
        if o in ('-p', '--p'):
            protein = a
        if o in ('-s', '--s'):
            size_x = int(a.split(',')[0])
            size_y = int(a.split(',')[1])
            size_z = int(a.split(',')[2])

if protein != None:
    file = open('pymol_data.txt','w')
    file.write('%s %s %s %s'%(protein,size_x, size_y, size_z))
    file.close()


