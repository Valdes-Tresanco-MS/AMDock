
#================================================================
import Tkinter,Pmw
from Tkinter import *
import tkMessageBox
import Pmw
from pymol import cmd
from pymol.cgo import *
from pymol import stored
from numpy import *
import tkColorChooser
from pymol.vfont import plain


def __init__(self):
    
    self.menuBar.addmenu('AMDock', 'Run the AMDock Plugin',tearoff=TRUE)
    self.menuBar.addmenuitem('AMDock', 'command',
   'AMDock Plugin',
    label='AMDock Box Constructor',
    command = lambda s=self: AMDockPlugin(s))
#
    cmd.set("retain_order") # keep atom ordering


__version__ = 1.0
BOX_TYPE = 'LINE'
GRID_CENTER_FROM_SELECTION = 0
GRID_CENTER_FROM_COORDINATES = 1
#==========================================================================
class AMDockPlugin:
    """  """
    def __init__(self,app):
        parent = app.root
        self.parent = parent
        self.data = None
        try:
            self.file = open('pymol_data.txt')
            for line in self.file:
                line = line.strip('\n')
                self.data = line.split()
            self.file.close()
        except:
            pass

        # box display settings
        self.box_display_mode = BOX_TYPE
        self.box_color = [1.,1.,1.]
        self.box_is_on_display = True
        self.box_display_cylinder_size = 0.2
        self.box_display_line_width = 1
        self.box_display_mesh_grid = 1
        self.box_size = []
        self.grid_center_selection_mode = IntVar()
        self.protein = None

        # grid definition
        self.grid_spacing = DoubleVar()
        self.grid_spacing.set(1.0)

        self.grid_center = [DoubleVar(), DoubleVar(), DoubleVar()]
        self.size_x = IntVar()
        self.size_y = IntVar()
        self.size_z = IntVar()
        if self.data is not None:
            self.grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
            self.protein = self.data[0]
            self.grid_center[0].set(self.data[1])
            self.grid_center[1].set(self.data[2])
            self.grid_center[2].set(self.data[3])
            self.size_x.set(self.data[4])
            self.size_y.set(self.data[5])
            self.size_z.set(self.data[6])
        else:
            self.grid_center_selection_mode.set(GRID_CENTER_FROM_SELECTION)
            self.grid_center[0].set(0)
            self.grid_center[1].set(0)
            self.grid_center[2].set(0)
            self.size_x.set(30)
            self.size_y.set(30)
            self.size_z.set(30)



        # build main window
        self.main_window = Pmw.Dialog(parent,
                                 buttons = ('Save Grid Information',),
                                 title = 'PyMOL AMDock Plugin',
                                 command = self.button_pressed)
        self.main_window.withdraw()
        Pmw.setbusycursorattributes(self.main_window.component('hull'))
        self.status_bar = Label(self.main_window.interior(),
                                 relief='sunken',
                                 font='times 10', anchor='w',fg='green',bg='black')
        self.status_bar.pack(side=BOTTOM,fill='x', expand=1, padx=0, pady=0)


        self.main_window.geometry('550x380')
        self.main_window.bind('<Return>',self.button_pressed)

        # the title

        self.title_label = Tkinter.Label(self.main_window.interior(),
                                         text = 'PyMOL AMDock Plugin\n [ Assisted Molecular Docking For AutoDock4 and Autodock Vina ]\nMARIO\nmariosergiovaldes145@gmail.com',
                                         background = 'navy',
                                         foreground = 'white',
                                         font='times 12'
                                         )
        self.title_label.pack(expand = 0, fill = 'both', padx = 4, pady = 4)


        # GRID DEFINITION
        self.grid_group = Pmw.Group(self.main_window.interior(), tag_text='Grid Dimensions')
        self.grid_group.pack(fill = 'both', expand = 0, padx=10, pady=5)

        # n grid points entries
        self.size_x_frame = Tkinter.Frame(self.grid_group.interior())
        self.size_x_label = Label(self.size_x_frame, text='X:')
        self.size_x_location = Entry(self.size_x_frame, textvariable= self.size_x, bg='black',fg='yellow', width = 7)
        self.size_x_scrollbar = Scrollbar(self.size_x_frame, orient = 'horizontal', command = self.size_x_changed)
        self.size_x_scrollbar.set('0.5','0.51')

        self.size_y_frame = Tkinter.Frame(self.grid_group.interior())
        self.size_y_label = Label(self.size_y_frame, text='Y:')
        self.size_y_location = Entry(self.size_y_frame, textvariable= self.size_y, bg='black',fg='yellow', width = 7)
        self.size_y_scrollbar = Scrollbar(self.size_y_frame, orient = 'horizontal', command = self.size_y_changed)
        self.size_y_scrollbar.set('0.5','0.51')

        self.size_z_frame = Tkinter.Frame(self.grid_group.interior())
        self.size_z_label = Label(self.size_z_frame, text='Z:')
        self.size_z_location = Entry(self.size_z_frame, textvariable= self.size_z, bg='black',fg='yellow', width = 7)
        self.size_z_scrollbar = Scrollbar(self.size_z_frame, orient = 'horizontal', command = self.size_z_changed)
        self.size_z_scrollbar.set('0.5','0.51')

        self.size_x_label.pack(side=LEFT)
        self.size_x_location.pack(side=LEFT)
        self.size_x_scrollbar.pack(side=LEFT)
        self.size_x_frame.pack(side=LEFT, padx=4, pady=1)

        self.size_y_label.pack(side=LEFT)
        self.size_y_location.pack(side=LEFT)
        self.size_y_scrollbar.pack(side=LEFT)
        self.size_y_frame.pack(side=LEFT, padx=4, pady=1)

        self.size_z_label.pack(side=LEFT)
        self.size_z_location.pack(side=LEFT)
        self.size_z_scrollbar.pack(side=LEFT)
        self.size_z_frame.pack(side=LEFT, padx=4, pady=1)

        Pmw.alignlabels( [self.size_x_label,
                          self.size_y_label,
                          self.size_z_label
                          ])

        Pmw.alignlabels( [self.size_x_location,
                          self.size_y_location,
                          self.size_z_location
                          ])

        # display option buttons
        self.display_button_box = Pmw.ButtonBox(self.main_window.interior(), padx=1, pady=1,orient='horizontal')
        self.display_button_box.add('Show Box',command = self.show_box)
        self.display_button_box.add('Hide Box',command = self.hide_box)
        self.display_button_box.pack(side=TOP, expand=1, padx=3, pady=3)

        self.grid_center_radiogroups = []

        if self.data is not None:
            self.grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        else:
            self.grid_center_selection_mode.set(GRID_CENTER_FROM_SELECTION)

        self.grid_center_radioframe = Tkinter.Frame(self.main_window.interior())
        # if self.data is not None:
        self.grid_center_pymol_selection = Pmw.Group(self.grid_center_radioframe,
                                                                  tag_pyclass = Tkinter.Radiobutton,
                                                                  tag_text = 'Calculate Grid Center by Selection',
                                                                  tag_value = GRID_CENTER_FROM_SELECTION,
                                                                  tag_variable = self.grid_center_selection_mode
                                                                  )
        # else:
        #     self.grid_center_pymol_selection = Pmw.Group(self.grid_center_radioframe,
        #                                                  tag_pyclass=Tkinter.Radiobutton,
        #                                                  tag_text='Calculate Grid Center by Selection',
        #                                                  tag_value=0,  # GRID_CENTER_FROM_SELECTION,
        #                                                  tag_variable=self.grid_center_selection_mode
        #                                                  )
        self.grid_center_pymol_selection.pack(fill = 'x', expand = 1, side = TOP)

        self.grid_center_radiogroups.append(self.grid_center_pymol_selection)

        self.grid_center_selection_user = Pmw.EntryField(self.grid_center_pymol_selection.interior(),
                                                          labelpos = 'w',
                                                          label_text = 'Selection',
                                                          value = '(all)',
                                                          command = self.grid_center_from_selection_changed
                                                          )
        self.grid_center_selection_user.pack(fill='x',padx=4,pady=1,expand=0)

        # if self.data is not None:
        self.grid_center_coordinates = Pmw.Group(self.grid_center_radioframe,
                                                              tag_pyclass = Tkinter.Radiobutton,
                                                              tag_text = 'Grid Center Coordinates',
                                                              tag_value = GRID_CENTER_FROM_COORDINATES,
                                                              tag_variable = self.grid_center_selection_mode
                                                              )
        # else:
        #     self.grid_center_coordinates = Pmw.Group(self.grid_center_radioframe,
        #                                              tag_pyclass=Tkinter.Radiobutton,
        #                                              tag_text='Grid Center Coordinates',
        #                                              tag_value=1,  # GRID_CENTER_FROM_COORDINATES,
        #                                              tag_variable=self.grid_center_selection_mode
        #                                              )
        self.grid_center_coordinates.pack(fill = 'x', expand = 1, side = TOP)

        self.grid_center_radiogroups.append(self.grid_center_coordinates)

        self.grid_center_radioframe.pack(padx = 6, pady = 6, expand='yes', fill='both')
        Pmw.aligngrouptags(self.grid_center_radiogroups)


        self.center_x_frame = Tkinter.Frame(self.grid_center_coordinates.interior())
        self.center_x_label = Label(self.center_x_frame, text = 'X:')
        self.center_x_location = Entry(self.center_x_frame, textvariable = self.grid_center[0], bg='black', fg='yellow', width=10)
        self.center_x_scrollbar = Scrollbar(self.center_x_frame,orient='horizontal',command = self.center_x_changed)
        self.center_x_scrollbar.set('0.5','0.51')

        self.center_y_frame = Tkinter.Frame(self.grid_center_coordinates.interior())
        self.center_y_label = Label(self.center_y_frame, text = 'Y:')
        self.center_y_location = Entry(self.center_y_frame, textvariable = self.grid_center[1], bg='black', fg='yellow', width=10)
        self.center_y_scrollbar = Scrollbar(self.center_y_frame,orient='horizontal',command = self.center_y_changed)
        self.center_y_scrollbar.set('0.5','0.51')

        self.center_z_frame = Tkinter.Frame(self.grid_center_coordinates.interior())
        self.center_z_label = Label(self.center_z_frame, text = 'Z:')
        self.center_z_location = Entry(self.center_z_frame, textvariable = self.grid_center[2], bg='black', fg='yellow', width=10)
        self.center_z_scrollbar = Scrollbar(self.center_z_frame,orient='horizontal',command = self.center_z_changed)
        self.center_z_scrollbar.set('0.5','0.51')

        self.center_x_label.pack(side = LEFT)
        self.center_x_location.pack(side=LEFT)
        self.center_x_scrollbar.pack(side=LEFT)
        self.center_x_frame.pack(side=LEFT,padx=4,pady=1)

        self.center_y_label.pack(side = LEFT)
        self.center_y_location.pack(side=LEFT)
        self.center_y_scrollbar.pack(side=LEFT)
        self.center_y_frame.pack(side=LEFT,padx=4,pady=1)

        self.center_z_label.pack(side = LEFT)
        self.center_z_location.pack(side=LEFT)
        self.center_z_scrollbar.pack(side=LEFT)
        self.center_z_frame.pack(side=LEFT,padx=4,pady=1)

        self.show_box()

        self.main_window.show()
        self.status_bar.configure(text ="Version: %s" % __version__)
        #------------------------------------------------------------------
        ##################################################################


    def button_pressed(self, result):
        if result == 'Save Grid Information':
            if self.protein == 'target':
                target_file = open('user_target_dim.txt','w')
                target_file.write('%s %s %s %s %s %s'%(self.grid_center[0].get(),self.grid_center[1].get(),
                                                       self.grid_center[2].get(), self.size_x.get(),
                                                       self.size_y.get(), self.size_z.get()))
                target_file.close()
            elif self.protein == 'control':
                control_file = open('user_control_dim.txt', 'w')
                control_file.write('%s %s %s %s %s %s' % (self.grid_center[0].get(), self.grid_center[1].get(),
                                                         self.grid_center[2].get(), self.size_x.get(),
                                                         self.size_y.get(), self.size_z.get()))
                control_file.close()

        elif result == None:
            exit = tkMessageBox.askokcancel('Warning', 'Do really you wish to quit?')
            if exit:
                ### falta implementar el guardado del fichero de datos o si es posible los valores conectarlos al programa
                self.main_window.withdraw()



    #------------------------------------------------------------------
    # grid settings functions

    def calculate_grid_center(self):
        if self.grid_center_selection_mode.get() == GRID_CENTER_FROM_SELECTION:
            sel = self.grid_center_selection_user.get()
            if sel:
                stored.xyz = []
                cmd.iterate_state(1,sel,"stored.xyz.append([x,y,z])")
                xx = average(map(lambda a: a[0], stored.xyz))
                yy = average(map(lambda a: a[1], stored.xyz))
                zz = average(map(lambda a: a[2], stored.xyz))
                self.grid_center[0].set(round(xx,2))
                self.grid_center[1].set(round(yy,2))
                self.grid_center[2].set(round(zz,2))
            else:
                self.grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        # else:
        #     self.grid_center[0].set(self.data[1])
        #     self.grid_center[1].set(self.data[2])
        #     self.grid_center[2].set(self.data[3])
        #     self.size_x.set(self.data[4])
        #     self.size_y.set(self.data[5])
        #     self.size_z.set(self.data[6])
       
    def size_x_changed(self, *args):
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.size_x.get())+(float(x)-0.5)*2.0
            val = round(val_raw, 0)
        elif args[0] == "scroll":
            x = args[1]
            val = int(self.size_x.get())+int(x)
        if val < 0:
            val = 0
        else:
            val = val
        self.size_x.set(val)
        self.grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        self.show_box()
        
    def size_y_changed(self, *args):
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.size_y.get())+(float(x)-0.5)*2.0
            val = round(val_raw, 0)
        elif args[0] == "scroll":
            x = args[1]
            val = int(self.size_y.get())+int(x)
        if val < 0:
            val = 0
        else:
            val = val
        self.size_y.set(val)
        self.grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        self.show_box()

    def size_z_changed(self, *args):
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.size_z.get())+(float(x)-0.5)*2.0
            val = round(val_raw, 0)
        elif args[0] == "scroll":
            x = args[1]
            val = int(self.size_z.get())+int(x)
        if val < 0:
            val = 0
        else:
            val = val
        self.size_z.set(val)
        self.grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        self.show_box()

    def grid_center_from_selection_changed(self):
        self.grid_center_selection_mode.set(GRID_CENTER_FROM_SELECTION)
        self.show_box()
        self.grid_center_selection_user.clear()

        print GRID_CENTER_FROM_SELECTION, '1'

    def center_x_changed(self, *args):
        self.grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.grid_center[0].get())+(float(x)-0.5)*10.0
        elif args[0] == "scroll":
            x = args[1]
            val_raw=float(self.grid_center[0].get())+float(x)*0.1
        val = round(val_raw,1)
        self.grid_center[0].set(val)
        self.show_box()

    def center_y_changed(self, *args):
        self.grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.grid_center[1].get())+(float(x)-0.5)*10.0
        elif args[0] == "scroll":
            x = args[1]
            val_raw=float(self.grid_center[1].get())+float(x)*0.1
        val = round(val_raw,1)
        self.grid_center[1].set(val)
        self.show_box()

    def center_z_changed(self, *args):
        self.grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.grid_center[2].get())+(float(x)-0.5)*10.0
        elif args[0] == "scroll":
            x = args[1]
            val_raw=float(self.grid_center[2].get())+float(x)*0.1
        val = round(val_raw,1)
        self.grid_center[2].set(val)
        self.show_box()

    # def select_atoms_within_binding_site(self):
    #     m = cmd.get_model("polymer")
    #     xmin, xmax = self.box_coords[0]
    #     ymin, ymax = self.box_coords[1]
    #     zmin, zmax = self.box_coords[2]
    #     lst = filter(lambda a: a.coord[0] >= xmin and \
    #                  a.coord[0] <= xmax and \
    #                  a.coord[1] >= ymin and \
    #                  a.coord[1] <= ymax and \
    #                  a.coord[2] >= zmin and \
    #                  a.coord[2] <= zmax, m.atom)
    #     by_id = map(lambda a: a.id, lst)
    #     if len(by_id) > 1:
    #         cmd.select("binding_site", "ID %d" % by_id[0])
    #         for idx in by_id[1:]:
    #             cmd.select("binding_site", "binding_site or ID %d" % idx)
    #         self.status_bar.configure(text = "Selector 'binding_site' created with %d atoms" % len(by_id))
    #         self.import_selections()
        
    def show_box(self):
        self.calculate_grid_center()
        self.show_crisscross()        
        self.calculate_box()

    def hide_box(self):
        cmd.delete("box")
        cmd.delete("grid_center")
        self.box_is_on_display = False

    def show_crisscross(self):
        center = [float(self.grid_center[0].get()),
                  float(self.grid_center[1].get()),
                  float(self.grid_center[2].get())
                  ]
        cmd.delete("grid_center")
        self.crisscross(center[0], center[1], center[2], 0.5, "grid_center")
        
    def crisscross(self,x,y,z,d,name="crisscross"):
        
        obj = [
            LINEWIDTH, 3,
            
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

    def calculate_box(self):
        x = float(self.grid_center[0].get())
        y = float(self.grid_center[1].get())
        z = float(self.grid_center[2].get())
        xpts = int(self.size_x.get())
        ypts = int(self.size_y.get())
        zpts = int(self.size_z.get())
        spacing = float(self.grid_spacing.get())
        cylinder_size = float(self.box_display_cylinder_size)

        size = [xpts*spacing, ypts*spacing, zpts*spacing]
        xmax = x + size[0]/2.
        xmin = x - size[0]/2.
        ymax = y + size[1]/2.
        ymin = y - size[1]/2.
        zmax = z + size[2]/2.
        zmin = z - size[2]/2.
        box_edge_x = [xmin,xmax]
        box_edge_y = [ymin,ymax]
        box_edge_z = [zmin,zmax]
        self.box_coords  = [box_edge_x,box_edge_y,box_edge_z]
        cmd.delete('box')
        if self.box_display_mode == BOX_TYPE:
            self.display_box(self.box_coords,cylinder_size)
        # elif self.box_display_mode.get()==BOX_AS_WIREBOX:
        #     self.display_wire_box(self.box_coords)
        self.box_is_on_display = True

        

    def display_box(self, box, cylinder_size):
        view = cmd.get_view()
        name = "box"
        obj = []
        # build cgo object
        color = self.box_color
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
        axes = [[2.0,0.0,0.0],[0.0,2.0,0.0],[0.0,0.0,2.0]]
        xpos = [box[0][1]+(box[0][1]-box[0][0])/5.,box[1][0],box[2][0]]
        cyl_text(obj,plain,xpos,'X',0.10,axes=axes)
        ypos = [box[0][0],box[1][1]+(box[1][1]-box[1][0])/5,box[2][0]]
        cyl_text(obj,plain,ypos,'Y',0.10,axes=axes)
        zpos = [box[0][0],box[1][0],box[2][1]+(box[2][1]-box[2][0])/5]
        cyl_text(obj,plain,zpos,'Z',0.10,axes=axes)
        cmd.load_cgo(obj,name)
        cmd.set_view(view)



cmd.set_view((\
     1.000000000,    0.000000000,    0.000000000,\
     0.000000000,    1.000000000,    0.000000000,\
     0.000000000,    0.000000000,    1.000000000,\
     0.000000000,    0.000000000,  -50.000000000,\
     0.000000000,    0.000000000,    0.000000000,\
    40.000000000,  100.000000000,  -20.000000000 ))
cmd.set_view((\
     1.000000000,    0.000000000,    0.000000000,\
     0.000000000,    1.000000000,    0.000000000,\
     0.000000000,    0.000000000,    1.000000000,\
     0.000000000,    0.000000000,  -50.000000000,\
     0.000000000,    0.000000000,    0.000000000,\
    40.000000000,  100.000000000,  -20.000000000 ))
