# This file is sa modification of AutoDock/AutoDock Vina plugin for pymol
# Autodock/Vina plugin is Copyright (C) 2009 by Daniel Seeliger (See the footer of the document )
# ================================================================
import Tkinter, Pmw
from Tkinter import *
import tkMessageBox
from pymol import cmd
from pymol.cgo import *
from pymol import stored
from numpy import *
from pymol.vfont import plain


def __init__(self):
    self.menuBar.addmenu('AMDock', 'Run the AMDock Plugin', tearoff=TRUE)
    self.menuBar.addmenuitem('AMDock', 'command',
                             'AMDock Plugin',
                             label='AMDock Box Builder',
                             command=lambda s=self: AMDockPlugin(s))
    #
    cmd.set("retain_order")  # keep atom ordering


__version__ = 2.0
BOX_TYPE = 'LINE'
GRID_CENTER_FROM_SELECTION = 0
GRID_CENTER_FROM_COORDINATES = 1
BOX_TYPE_B = 'LINE'
GRID_CENTER_FROM_SELECTION_B = 0
GRID_CENTER_FROM_COORDINATES_B = 1


# ==========================================================================
class AMDockPlugin:
    """  """

    def __init__(self, app):
        parent = app.root
        self.parent = parent
        self.target_data = [None, 0, 0, 0, 30, 30, 30]
        self.offtarget_data = [None, 0, 0, 0, 30, 30, 30]
        self.build = False
        self.read_data()
        self.saved = True
        # box display settings
        self.target_box_is_on_display = True
        self.offtarget_box_is_on_display = True
        self.box_display_cylinder_size = 0.2
        self.target_grid_center_selection_mode = IntVar()
        self.offtarget_grid_center_selection_mode = IntVar()


        # grid definition
        self.grid_spacing = 1.0

        self.target_grid_center = [DoubleVar(), DoubleVar(), DoubleVar()]
        self.target_grid_center[0].set(self.target_data[1])
        self.target_grid_center[1].set(self.target_data[2])
        self.target_grid_center[2].set(self.target_data[3])
        self.target_grid_size = [IntVar(), IntVar(), IntVar()]
        self.target_grid_size[0].set(self.target_data[4])
        self.target_grid_size[1].set(self.target_data[5])
        self.target_grid_size[2].set(self.target_data[6])
        self.offtarget_grid_center = [DoubleVar(), DoubleVar(), DoubleVar()]
        self.offtarget_grid_center[0].set(self.offtarget_data[1])
        self.offtarget_grid_center[1].set(self.offtarget_data[2])
        self.offtarget_grid_center[2].set(self.offtarget_data[3])
        self.offtarget_grid_size = [IntVar(), IntVar(), IntVar()]
        self.offtarget_grid_size[0].set(self.offtarget_data[4])
        self.offtarget_grid_size[1].set(self.offtarget_data[5])
        self.offtarget_grid_size[2].set(self.offtarget_data[6])
        self.target_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        self.offtarget_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES_B)

        # build main window
        self.main_window = Pmw.Dialog(parent,
                                      buttons=('Save Box Info',),
                                      title='PyMOL AMDock Plugin',
                                      command=self.check_for_exit)
        self.main_window.withdraw()
        Pmw.setbusycursorattributes(self.main_window.component('hull'))
        self.status_bar = Label(self.main_window.interior(),
                                relief='sunken',
                                font='times 10', anchor='w', fg='green', bg='black')
        self.status_bar.pack(side=BOTTOM, fill='x', expand=1, padx=0, pady=0)
        if self.target_data[0] and self.offtarget_data[0]:
            self.main_window.geometry('550x640')
        else:
            self.main_window.geometry('550x400')
        # self.main_window.bind('<Return>', self.button_pressed)

        # the title

        self.title_label = Tkinter.Label(self.main_window.interior(),
                                         text='PyMOL AMDock Plugin\n [ Assisted Molecular Docking For AutoDock4 and '
                                              'Autodock Vina ]\nFeel free to write us for any suggestions or errors '
                                              'you find\nhttps://groups.google.com/forum/#!forum/amdock\nThis '
                                              'plugin is based in Daniel Seeliger plugin.',
                                         background='navy',
                                         foreground='white',
                                         font='times 12'
                                         )
        self.title_label.pack(expand=0, fill='both', padx=4, pady=4)

        # Target group
        self.target_group = Pmw.Group(self.main_window.interior(), tag_text='Target')
        self.target_group.pack(fill='both', expand=0, padx=10, pady=5)
        if not self.target_data[0]:
            self.target_group.collapse()
        # Off-Target group
        self.offtarget_group = Pmw.Group(self.main_window.interior(), tag_text='Off-Target')
        self.offtarget_group.pack(fill='both', expand=0, padx=10, pady=5)
        if not self.offtarget_data[0]:
            self.offtarget_group.collapse()
        # Target GRID DEFINITION
        self.target_grid_group = Pmw.Group(self.target_group.interior(), tag_text='Grid Dimensions')
        self.target_grid_group.pack(fill='both', expand=0, padx=10, pady=5)
        # Off-Target GRID DEFINITION
        self.offtarget_grid_group = Pmw.Group(self.offtarget_group.interior(), tag_text='Grid Dimensions')
        self.offtarget_grid_group.pack(fill='both', expand=0, padx=10, pady=5)

        # n grid points entries target
        self.target_size_x_frame = Tkinter.Frame(self.target_grid_group.interior())
        self.target_size_x_label = Label(self.target_size_x_frame, text='X:')
        self.target_size_x_location = Entry(self.target_size_x_frame, textvariable=self.target_grid_size[0],
                                            bg='black', fg='yellow', width=7)
        self.target_size_x_scrollbar = Scrollbar(self.target_size_x_frame, orient='horizontal',
                                                 command=self.target_size_x_changed)
        self.target_size_x_scrollbar.set('0.5', '0.51')

        self.target_size_y_frame = Tkinter.Frame(self.target_grid_group.interior())
        self.target_size_y_label = Label(self.target_size_y_frame, text='Y:')
        self.target_size_y_location = Entry(self.target_size_y_frame, textvariable=self.target_grid_size[1], bg='black',
                                            fg='yellow', width=7)
        self.target_size_y_scrollbar = Scrollbar(self.target_size_y_frame, orient='horizontal',
                                                 command=self.target_size_y_changed)
        self.target_size_y_scrollbar.set('0.5', '0.51')

        self.target_size_z_frame = Tkinter.Frame(self.target_grid_group.interior())
        self.target_size_z_label = Label(self.target_size_z_frame, text='Z:')
        self.target_size_z_location = Entry(self.target_size_z_frame, textvariable=self.target_grid_size[2],
                                            bg='black', fg='yellow', width=7)
        self.target_size_z_scrollbar = Scrollbar(self.target_size_z_frame, orient='horizontal',
                                                 command=self.target_size_z_changed)
        self.target_size_z_scrollbar.set('0.5', '0.51')

        self.target_size_x_label.pack(side=LEFT)
        self.target_size_x_location.pack(side=LEFT)
        self.target_size_x_scrollbar.pack(side=LEFT)
        self.target_size_x_frame.pack(side=LEFT, padx=4, pady=1)

        self.target_size_y_label.pack(side=LEFT)
        self.target_size_y_location.pack(side=LEFT)
        self.target_size_y_scrollbar.pack(side=LEFT)
        self.target_size_y_frame.pack(side=LEFT, padx=4, pady=1)

        self.target_size_z_label.pack(side=LEFT)
        self.target_size_z_location.pack(side=LEFT)
        self.target_size_z_scrollbar.pack(side=LEFT)
        self.target_size_z_frame.pack(side=LEFT, padx=4, pady=1)

        Pmw.alignlabels([self.target_size_x_label,
                         self.target_size_y_label,
                         self.target_size_z_label
                         ])

        Pmw.alignlabels([self.target_size_x_location,
                         self.target_size_y_location,
                         self.target_size_z_location
                         ])
        # n grid points entries off-target
        self.offtarget_size_x_frame = Tkinter.Frame(self.offtarget_grid_group.interior())
        self.offtarget_size_x_label = Label(self.offtarget_size_x_frame, text='X:')
        self.offtarget_size_x_location = Entry(self.offtarget_size_x_frame, textvariable=self.offtarget_grid_size[0],
                                               bg='black', fg='yellow', width=7)
        self.offtarget_size_x_scrollbar = Scrollbar(self.offtarget_size_x_frame, orient='horizontal',
                                                    command=self.offtarget_size_x_changed)
        self.offtarget_size_x_scrollbar.set('0.5', '0.51')

        self.offtarget_size_y_frame = Tkinter.Frame(self.offtarget_grid_group.interior())
        self.offtarget_size_y_label = Label(self.offtarget_size_y_frame, text='Y:')
        self.offtarget_size_y_location = Entry(self.offtarget_size_y_frame, textvariable=self.offtarget_grid_size[1],
                                               bg='black', fg='yellow', width=7)
        self.offtarget_size_y_scrollbar = Scrollbar(self.offtarget_size_y_frame, orient='horizontal',
                                                    command=self.offtarget_size_y_changed)
        self.offtarget_size_y_scrollbar.set('0.5', '0.51')

        self.offtarget_size_z_frame = Tkinter.Frame(self.offtarget_grid_group.interior())
        self.offtarget_size_z_label = Label(self.offtarget_size_z_frame, text='Z:')
        self.offtarget_size_z_location = Entry(self.offtarget_size_z_frame, textvariable=self.offtarget_grid_size[2],
                                               bg='black', fg='yellow', width=7)
        self.offtarget_size_z_scrollbar = Scrollbar(self.offtarget_size_z_frame, orient='horizontal',
                                                    command=self.offtarget_size_z_changed)
        self.offtarget_size_z_scrollbar.set('0.5', '0.51')

        self.offtarget_size_x_label.pack(side=LEFT)
        self.offtarget_size_x_location.pack(side=LEFT)
        self.offtarget_size_x_scrollbar.pack(side=LEFT)
        self.offtarget_size_x_frame.pack(side=LEFT, padx=4, pady=1)

        self.offtarget_size_y_label.pack(side=LEFT)
        self.offtarget_size_y_location.pack(side=LEFT)
        self.offtarget_size_y_scrollbar.pack(side=LEFT)
        self.offtarget_size_y_frame.pack(side=LEFT, padx=4, pady=1)

        self.offtarget_size_z_label.pack(side=LEFT)
        self.offtarget_size_z_location.pack(side=LEFT)
        self.offtarget_size_z_scrollbar.pack(side=LEFT)
        self.offtarget_size_z_frame.pack(side=LEFT, padx=4, pady=1)

        Pmw.alignlabels([self.offtarget_size_x_label,
                         self.offtarget_size_y_label,
                         self.offtarget_size_z_label
                         ])

        Pmw.alignlabels([self.offtarget_size_x_location,
                         self.offtarget_size_y_location,
                         self.offtarget_size_z_location
                         ])

        # target display option buttons
        self.target_display_button_box = Pmw.ButtonBox(self.target_group.interior(), padx=1, pady=1,
                                                       orient='horizontal')
        self.target_display_button_box.add('Show Box', command=self.show_target_box)
        self.target_display_button_box.add('Hide Box', command=self.hide_target_box)
        self.target_display_button_box.add('Reset', command=self.reset_target)
        self.target_display_button_box.pack(side=TOP, expand=1, padx=3, pady=3)
        # off-target display option buttons
        self.offtarget_display_button_box = Pmw.ButtonBox(self.offtarget_group.interior(), padx=1, pady=1,
                                                          orient='horizontal')
        self.offtarget_display_button_box.add('Show Box', command=self.show_offtarget_box)
        self.offtarget_display_button_box.add('Hide Box', command=self.hide_offtarget_box)
        self.offtarget_display_button_box.add('Reset', command=self.reset_offtarget)
        self.offtarget_display_button_box.pack(side=TOP, expand=1, padx=3, pady=3)

        self.target_grid_center_radiogroups = []
        self.offtarget_grid_center_radiogroups = []

        self.target_grid_center_radioframe = Tkinter.Frame(self.target_group.interior())
        self.target_grid_center_pymol_selection = Pmw.Group(self.target_grid_center_radioframe,
                                                            tag_pyclass=Tkinter.Radiobutton,
                                                            tag_text='Calculate Grid Center by Selection',
                                                            tag_value=GRID_CENTER_FROM_SELECTION,
                                                            tag_variable=self.target_grid_center_selection_mode
                                                            )

        self.target_grid_center_pymol_selection.pack(fill='x', expand=1, side=TOP)

        self.target_grid_center_radiogroups.append(self.target_grid_center_pymol_selection)

        self.target_grid_center_selection_user = Pmw.EntryField(self.target_grid_center_pymol_selection.interior(),
                                                                labelpos='w',
                                                                label_text='Selection',
                                                                value='(all)',
                                                                command=self.target_grid_center_from_selection_changed
                                                                )
        self.target_grid_center_selection_user.pack(fill='x', padx=4, pady=1, expand=0)

        self.target_grid_center_coordinates = Pmw.Group(self.target_grid_center_radioframe,
                                                        tag_pyclass=Tkinter.Radiobutton,
                                                        tag_text='Grid Center Coordinates',
                                                        tag_value=GRID_CENTER_FROM_COORDINATES,
                                                        tag_variable=self.target_grid_center_selection_mode
                                                        )
        self.target_grid_center_coordinates.pack(fill='x', expand=1, side=TOP)

        self.target_grid_center_radiogroups.append(self.target_grid_center_coordinates)

        self.target_grid_center_radioframe.pack(padx=6, pady=6, expand='yes', fill='both')
        Pmw.aligngrouptags(self.target_grid_center_radiogroups)

        self.offtarget_grid_center_radioframe = Tkinter.Frame(self.offtarget_group.interior())
        self.offtarget_grid_center_pymol_selection = Pmw.Group(self.offtarget_grid_center_radioframe,
                                                               tag_pyclass=Tkinter.Radiobutton,
                                                               tag_text='Calculate Grid Center by Selection',
                                                               tag_value=GRID_CENTER_FROM_SELECTION_B,
                                                               tag_variable=self.offtarget_grid_center_selection_mode
                                                               )

        self.offtarget_grid_center_pymol_selection.pack(fill='x', expand=1, side=TOP)

        self.offtarget_grid_center_radiogroups.append(self.offtarget_grid_center_pymol_selection)

        self.offtarget_grid_center_selection_user = Pmw.EntryField(
            self.offtarget_grid_center_pymol_selection.interior(),
            labelpos='w',
            label_text='Selection',
            value='(all)',
            command=self.offtarget_grid_center_from_selection_changed
            )
        self.offtarget_grid_center_selection_user.pack(fill='x', padx=4, pady=1, expand=0)

        self.offtarget_grid_center_coordinates = Pmw.Group(self.offtarget_grid_center_radioframe,
                                                           tag_pyclass=Tkinter.Radiobutton,
                                                           tag_text='Grid Center Coordinates',
                                                           tag_value=GRID_CENTER_FROM_COORDINATES_B,
                                                           tag_variable=self.offtarget_grid_center_selection_mode
                                                           )
        self.offtarget_grid_center_coordinates.pack(fill='x', expand=1, side=TOP)

        self.offtarget_grid_center_radiogroups.append(self.offtarget_grid_center_coordinates)

        self.offtarget_grid_center_radioframe.pack(padx=6, pady=6, expand='yes', fill='both')
        Pmw.aligngrouptags(self.offtarget_grid_center_radiogroups)

        self.target_center_x_frame = Tkinter.Frame(self.target_grid_center_coordinates.interior())
        self.target_center_x_label = Label(self.target_center_x_frame, text='X:')
        self.target_center_x_location = Entry(self.target_center_x_frame, textvariable=self.target_grid_center[0],
                                              bg='black', fg='yellow', width=10)
        self.target_center_x_scrollbar = Scrollbar(self.target_center_x_frame, orient='horizontal',
                                                   command=self.target_center_x_changed)
        self.target_center_x_scrollbar.set('0.5', '0.51')

        self.target_center_y_frame = Tkinter.Frame(self.target_grid_center_coordinates.interior())
        self.target_center_y_label = Label(self.target_center_y_frame, text='Y:')
        self.target_center_y_location = Entry(self.target_center_y_frame, textvariable=self.target_grid_center[1], bg='black',
                                              fg='yellow', width=10)
        self.target_center_y_scrollbar = Scrollbar(self.target_center_y_frame, orient='horizontal',
                                                   command=self.target_center_y_changed)
        self.target_center_y_scrollbar.set('0.5', '0.51')

        self.target_center_z_frame = Tkinter.Frame(self.target_grid_center_coordinates.interior())
        self.target_center_z_label = Label(self.target_center_z_frame, text='Z:')
        self.target_center_z_location = Entry(self.target_center_z_frame, textvariable=self.target_grid_center[2], bg='black',
                                              fg='yellow', width=10)
        self.target_center_z_scrollbar = Scrollbar(self.target_center_z_frame, orient='horizontal',
                                                   command=self.target_center_z_changed)
        self.target_center_z_scrollbar.set('0.5', '0.51')

        self.target_center_x_label.pack(side=LEFT)
        self.target_center_x_location.pack(side=LEFT)
        self.target_center_x_scrollbar.pack(side=LEFT)
        self.target_center_x_frame.pack(side=LEFT, padx=4, pady=1)

        self.target_center_y_label.pack(side=LEFT)
        self.target_center_y_location.pack(side=LEFT)
        self.target_center_y_scrollbar.pack(side=LEFT)
        self.target_center_y_frame.pack(side=LEFT, padx=4, pady=1)

        self.target_center_z_label.pack(side=LEFT)
        self.target_center_z_location.pack(side=LEFT)
        self.target_center_z_scrollbar.pack(side=LEFT)
        self.target_center_z_frame.pack(side=LEFT, padx=4, pady=1)

        self.offtarget_center_x_frame = Tkinter.Frame(self.offtarget_grid_center_coordinates.interior())
        self.offtarget_center_x_label = Label(self.offtarget_center_x_frame, text='X:')
        self.offtarget_center_x_location = Entry(self.offtarget_center_x_frame,
                                                 textvariable=self.offtarget_grid_center[0],
                                                 bg='black', fg='yellow', width=10)
        self.offtarget_center_x_scrollbar = Scrollbar(self.offtarget_center_x_frame, orient='horizontal',
                                                      command=self.offtarget_center_x_changed)
        self.offtarget_center_x_scrollbar.set('0.5', '0.51')

        self.offtarget_center_y_frame = Tkinter.Frame(self.offtarget_grid_center_coordinates.interior())
        self.offtarget_center_y_label = Label(self.offtarget_center_y_frame, text='Y:')
        self.offtarget_center_y_location = Entry(self.offtarget_center_y_frame,
                                                 textvariable=self.offtarget_grid_center[1],
                                                 bg='black', fg='yellow', width=10)
        self.offtarget_center_y_scrollbar = Scrollbar(self.offtarget_center_y_frame, orient='horizontal',
                                                      command=self.offtarget_center_y_changed)
        self.offtarget_center_y_scrollbar.set('0.5', '0.51')

        self.offtarget_center_z_frame = Tkinter.Frame(self.offtarget_grid_center_coordinates.interior())
        self.offtarget_center_z_label = Label(self.offtarget_center_z_frame, text='Z:')
        self.offtarget_center_z_location = Entry(self.offtarget_center_z_frame,
                                                 textvariable=self.offtarget_grid_center[2],
                                                 bg='black', fg='yellow', width=10)
        self.offtarget_center_z_scrollbar = Scrollbar(self.offtarget_center_z_frame, orient='horizontal',
                                                      command=self.offtarget_center_z_changed)
        self.offtarget_center_z_scrollbar.set('0.5', '0.51')

        self.offtarget_center_x_label.pack(side=LEFT)
        self.offtarget_center_x_location.pack(side=LEFT)
        self.offtarget_center_x_scrollbar.pack(side=LEFT)
        self.offtarget_center_x_frame.pack(side=LEFT, padx=4, pady=1)

        self.offtarget_center_y_label.pack(side=LEFT)
        self.offtarget_center_y_location.pack(side=LEFT)
        self.offtarget_center_y_scrollbar.pack(side=LEFT)
        self.offtarget_center_y_frame.pack(side=LEFT, padx=4, pady=1)

        self.offtarget_center_z_label.pack(side=LEFT)
        self.offtarget_center_z_location.pack(side=LEFT)
        self.offtarget_center_z_scrollbar.pack(side=LEFT)
        self.offtarget_center_z_frame.pack(side=LEFT, padx=4, pady=1)

        self.show_target_box()

        self.main_window.show()
        self.status_bar.configure(text="Version: %s" % __version__)
        # ------------------------------------------------------------------
        ##################################################################
    def read_data(self):
        if os.path.exists('pymol_data.txt'):
            file = open('pymol_data.txt')
            for line in file:
                line = line.strip('\n')
                if line.startswith('target'):
                    self.target_data = line.split()
                elif line.startswith('off-target'):
                    self.offtarget_data = line.split()
            file.close()

    def reset_target(self):
        self.target_grid_center[0].set(self.target_data[1])
        self.target_grid_center[1].set(self.target_data[2])
        self.target_grid_center[2].set(self.target_data[3])
        self.target_grid_size[0].set(self.target_data[4])
        self.target_grid_size[1].set(self.target_data[5])
        self.target_grid_size[2].set(self.target_data[6])

        self.show_target_box()

    def reset_offtarget(self):
        self.offtarget_grid_center[0].set(self.offtarget_data[1])
        self.offtarget_grid_center[1].set(self.offtarget_data[2])
        self.offtarget_grid_center[2].set(self.offtarget_data[3])
        self.offtarget_grid_size[0].set(self.offtarget_data[4])
        self.offtarget_grid_size[1].set(self.offtarget_data[5])
        self.offtarget_grid_size[2].set(self.offtarget_data[6])

        self.show_offtarget_box()

    def save_info(self):
        savet = True
        saveo = True
        if [x.get() for x in self.target_grid_size]== [int(x) for x in self.target_data[4:]] and \
                [x.get() for x in self.target_grid_center]== [float(x) for x in self.target_data[1:4]]:
            savet = False
        if [x.get() for x in self.offtarget_grid_size]== [int(x) for x in self.offtarget_data[4:]] and \
                [x.get() for x in self.offtarget_grid_center]== [float(x) for x in self.offtarget_data[1:4]]:
            saveo = False
        if not savet and not savet:
            print('Nothing to save')
            return
        ofile = open('pymol_data.txt', 'w')
        if savet and saveo:
            info = 'AMDock INFO: {} {} {} {} {} {} {} {} {} {} {} {} {} {}'.format(self.target_data[0],
                                                                                   self.target_grid_center[0].get(),
                                                                                   self.target_grid_center[1].get(),
                                                                                   self.target_grid_center[2].get(),
                                                                                   self.target_grid_size[0].get(),
                                                                                   self.target_grid_size[1].get(),
                                                                                   self.target_grid_size[2].get(),
                                                                                   self.offtarget_data[0],
                                                                                   self.offtarget_grid_center[0].get(),
                                                                                   self.offtarget_grid_center[1].get(),
                                                                                   self.offtarget_grid_center[2].get(),
                                                                                   self.offtarget_grid_size[0].get(),
                                                                                   self.offtarget_grid_size[1].get(),
                                                                                   self.offtarget_grid_size[2].get()
                                                                                   )
            print(info)
            ofile.write('{} {} {} {} {} {} {}\n'.format(*info.split()[2:9]))
            ofile.write('{} {} {} {} {} {} {}\n'.format(*info.split()[9:]))
        elif savet:
            info = 'AMDock INFO: {} {} {} {} {} {} {}'.format(self.target_data[0],
                                                              self.target_grid_center[0].get(),
                                                              self.target_grid_center[1].get(),
                                                              self.target_grid_center[2].get(),
                                                              self.target_grid_size[0].get(),
                                                              self.target_grid_size[1].get(),
                                                              self.target_grid_size[2].get()
                                                              )
            print(info)
            ofile.write(info[13:] + '\n')
            if self.offtarget_data[0]:
                ofile.write('{} {} {} {} {} {} {}\n'.format(*self.offtarget_data))
        else:
            info = 'AMDock INFO: {} {} {} {} {} {} {}'.format(self.offtarget_data[0],
                                                              self.offtarget_grid_center[0].get(),
                                                              self.offtarget_grid_center[1].get(),
                                                              self.offtarget_grid_center[2].get(),
                                                              self.offtarget_grid_size[0].get(),
                                                              self.offtarget_grid_size[1].get(),
                                                              self.offtarget_grid_size[2].get()
                                                              )
            print(info)
            ofile.write(info[13:] + '\n')
            if self.target_data[0]:
                ofile.write('{} {} {} {} {} {} {}\n'.format(*self.target_data))

        ofile.close()
        self.read_data()

    def check_for_exit(self, btn):
        if btn == 'Save Box Info':
            self.save_info()
        else:
            if [x.get() for x in self.target_grid_size] != [int(x) for x in self.target_data[4:]] or \
                [x.get() for x in self.target_grid_center] != [float(x) for x in self.target_data[1:4]] or \
                [x.get() for x in self.offtarget_grid_size] != [int(x) for x in self.offtarget_data[4:]] or \
                [x.get() for x in self.offtarget_grid_center] != [float(x) for x in self.offtarget_data[1:4]]:
                res = tkMessageBox.askyesno('Warning', "Some changes have not been saved. Do you want to save "
                                                             "them before exit?")
                if res == YES:
                    self.save_info()

                    self.main_window.withdraw()
                elif res == NO:
                    self.main_window.withdraw()
                else:
                    return

            else:
                exit = tkMessageBox.askokcancel('Warning', 'Do really you wish to quit?')
                if exit:
                    self.main_window.withdraw()
            cmd.delete("Target_box")
            cmd.delete("T_grid_center")
            cmd.delete("Off-Target_box")
            cmd.delete("O_grid_center")
    # ------------------------------------------------------------------
    # grid settings functions

    def calculate_target_grid_center(self):
        if self.target_grid_center_selection_mode.get() == GRID_CENTER_FROM_SELECTION:
            sel = self.target_grid_center_selection_user.get()
            if sel:
                stored.xyz_target = []
                cmd.iterate_state(1, sel, "stored.xyz_target.append([x,y,z])")
                xx = average(map(lambda a: a[0], stored.xyz_target))
                yy = average(map(lambda a: a[1], stored.xyz_target))
                zz = average(map(lambda a: a[2], stored.xyz_target))
                self.target_grid_center[0].set(round(xx, 2))
                self.target_grid_center[1].set(round(yy, 2))
                self.target_grid_center[2].set(round(zz, 2))
            else:
                self.target_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)

    def calculate_offtarget_grid_center(self):
        if self.offtarget_grid_center_selection_mode.get() == GRID_CENTER_FROM_SELECTION_B:
            sel = self.offtarget_grid_center_selection_user.get()
            if sel:
                stored.xyz_offtarget = []
                cmd.iterate_state(1, sel, "stored.xyz_offtarget.append([x,y,z])")
                xx = average(map(lambda a: a[0], stored.xyz_offtarget))
                yy = average(map(lambda a: a[1], stored.xyz_offtarget))
                zz = average(map(lambda a: a[2], stored.xyz_offtarget))
                self.offtarget_grid_center[0].set(round(xx, 2))
                self.offtarget_grid_center[1].set(round(yy, 2))
                self.offtarget_grid_center[2].set(round(zz, 2))
            else:
                self.offtarget_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES_B)

    def target_size_x_changed(self, *args):
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.target_grid_size[0].get()) + (float(x) - 0.5) * 2.0
            val = round(val_raw, 0)
        elif args[0] == "scroll":
            x = args[1]
            val = int(self.target_grid_size[0].get()) + int(x)
        if val < 0:
            val = 0
        else:
            val = val
        self.target_grid_size[0].set(val)
        self.target_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        self.show_target_box()

    def offtarget_size_x_changed(self, *args):
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.offtarget_grid_size[0].get()) + (float(x) - 0.5) * 2.0
            val = round(val_raw, 0)
        elif args[0] == "scroll":
            x = args[1]
            val = int(self.offtarget_grid_size[0].get()) + int(x)
        if val < 0:
            val = 0
        else:
            val = val
        self.offtarget_grid_size[0].set(val)
        self.offtarget_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES_B)
        self.show_offtarget_box()

    def target_size_y_changed(self, *args):
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.target_grid_size[1].get()) + (float(x) - 0.5) * 2.0
            val = round(val_raw, 0)
        elif args[0] == "scroll":
            x = args[1]
            val = int(self.target_grid_size[1].get()) + int(x)
        if val < 0:
            val = 0
        else:
            val = val
        self.target_grid_size[1].set(val)
        self.target_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        self.show_target_box()

    def offtarget_size_y_changed(self, *args):
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.offtarget_grid_size[1].get()) + (float(x) - 0.5) * 2.0
            val = round(val_raw, 0)
        elif args[0] == "scroll":
            x = args[1]
            val = int(self.offtarget_grid_size[1].get()) + int(x)
        if val < 0:
            val = 0
        else:
            val = val
        self.offtarget_grid_size[1].set(val)
        self.offtarget_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES_B)
        self.show_offtarget_box()

    def target_size_z_changed(self, *args):
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.target_grid_size[2].get()) + (float(x) - 0.5) * 2.0
            val = round(val_raw, 0)
        elif args[0] == "scroll":
            x = args[1]
            val = int(self.target_grid_size[2].get()) + int(x)
        if val < 0:
            val = 0
        else:
            val = val
        self.target_grid_size[2].set(val)
        self.target_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        self.show_target_box()

    def offtarget_size_z_changed(self, *args):
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.offtarget_grid_size[2].get()) + (float(x) - 0.5) * 2.0
            val = round(val_raw, 0)
        elif args[0] == "scroll":
            x = args[1]
            val = int(self.offtarget_grid_size[2].get()) + int(x)
        if val < 0:
            val = 0
        else:
            val = val
        self.offtarget_grid_size[2].set(val)
        self.offtarget_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES_B)
        self.show_offtarget_box()

    def target_grid_center_from_selection_changed(self):
        self.target_grid_center_selection_mode.set(GRID_CENTER_FROM_SELECTION)
        self.show_target_box()
        self.target_grid_center_selection_user.clear()

    def offtarget_grid_center_from_selection_changed(self):
        self.offtarget_grid_center_selection_mode.set(GRID_CENTER_FROM_SELECTION_B)
        self.show_offtarget_box()
        self.offtarget_grid_center_selection_user.clear()

    def target_center_x_changed(self, *args):
        self.target_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.target_grid_center[0].get()) + (float(x) - 0.5) * 10.0
        elif args[0] == "scroll":
            x = args[1]
            val_raw = float(self.target_grid_center[0].get()) + float(x) * 0.1
        val = round(val_raw, 1)
        self.target_grid_center[0].set(val)
        self.show_target_box()

    def offtarget_center_x_changed(self, *args):
        self.offtarget_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES_B)
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.offtarget_grid_center[0].get()) + (float(x) - 0.5) * 10.0
        elif args[0] == "scroll":
            x = args[1]
            val_raw = float(self.offtarget_grid_center[0].get()) + float(x) * 0.1
        val = round(val_raw, 1)
        self.offtarget_grid_center[0].set(val)
        self.show_offtarget_box()

    def target_center_y_changed(self, *args):
        self.target_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.target_grid_center[1].get()) + (float(x) - 0.5) * 10.0
        elif args[0] == "scroll":
            x = args[1]
            val_raw = float(self.target_grid_center[1].get()) + float(x) * 0.1
        val = round(val_raw, 1)
        self.target_grid_center[1].set(val)
        self.show_target_box()

    def offtarget_center_y_changed(self, *args):
        self.offtarget_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES_B)
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.offtarget_grid_center[1].get()) + (float(x) - 0.5) * 10.0
        elif args[0] == "scroll":
            x = args[1]
            val_raw = float(self.offtarget_grid_center[1].get()) + float(x) * 0.1
        val = round(val_raw, 1)
        self.offtarget_grid_center[1].set(val)
        self.show_offtarget_box()

    def target_center_z_changed(self, *args):
        self.target_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES)
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.target_grid_center[2].get()) + (float(x) - 0.5) * 10.0
        elif args[0] == "scroll":
            x = args[1]
            val_raw = float(self.target_grid_center[2].get()) + float(x) * 0.1
        val = round(val_raw, 1)
        self.target_grid_center[2].set(val)
        self.show_target_box()

    def offtarget_center_z_changed(self, *args):
        self.offtarget_grid_center_selection_mode.set(GRID_CENTER_FROM_COORDINATES_B)
        if args[0] == "moveto":
            x = args[1]
            val_raw = float(self.offtarget_grid_center[2].get()) + (float(x) - 0.5) * 10.0
        elif args[0] == "scroll":
            x = args[1]
            val_raw = float(self.offtarget_grid_center[2].get()) + float(x) * 0.1
        val = round(val_raw, 1)
        self.offtarget_grid_center[2].set(val)
        self.show_target_box()

    def show_target_box(self):
        self.calculate_target_grid_center()
        self.show_target_crisscross()
        self.calculate_box(self.target_grid_center[0].get(), self.target_grid_center[1].get(),
                           self.target_grid_center[2].get(), self.target_grid_size[0].get(),
                           self.target_grid_size[1].get(), self.target_grid_size[2].get(), self.target_data[0])

    def hide_target_box(self):
        cmd.delete("Target_box")
        cmd.delete("T_grid_center")
        self.target_box_is_on_display = False

    def show_offtarget_box(self):
        self.calculate_offtarget_grid_center()
        self.show_offtarget_crisscross()
        self.calculate_box(self.offtarget_grid_center[0].get(), self.offtarget_grid_center[1].get(),
                           self.offtarget_grid_center[2].get(), self.offtarget_grid_size[0].get(),
                           self.offtarget_grid_size[1].get(), self.offtarget_grid_size[2].get(), self.offtarget_data[0])

    def hide_offtarget_box(self):
        cmd.delete("Off-Target_box")
        cmd.delete("O_grid_center")
        self.offtarget_box_is_on_display = False

    def show_target_crisscross(self):
        center = [float(self.target_grid_center[0].get()),
                  float(self.target_grid_center[1].get()),
                  float(self.target_grid_center[2].get())]
        cmd.delete("T_grid_center")
        self.crisscross(center[0], center[1], center[2], 0.5, "T_grid_center")

    def show_offtarget_crisscross(self):
        center = [float(self.offtarget_grid_center[0].get()),
                  float(self.offtarget_grid_center[1].get()),
                  float(self.offtarget_grid_center[2].get())]
        cmd.delete("O_grid_center")
        self.crisscross(center[0], center[1], center[2], 0.5, "O_grid_center")

    def crisscross(self, x, y, z, d, name="crisscross"):

        obj = [
            LINEWIDTH, 3,

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
        view = cmd.get_view()
        cmd.load_cgo(obj, name)
        cmd.set_view(view)

    def calculate_box(self, x, y, z, xpts, ypts, zpts, prot):
        spacing = self.grid_spacing
        cylinder_size = self.box_display_cylinder_size

        size = [xpts * spacing, ypts * spacing, zpts * spacing]
        xmax = x + size[0] / 2.
        xmin = x - size[0] / 2.
        ymax = y + size[1] / 2.
        ymin = y - size[1] / 2.
        zmax = z + size[2] / 2.
        zmin = z - size[2] / 2.
        box_edge_x = [xmin, xmax]
        box_edge_y = [ymin, ymax]
        box_edge_z = [zmin, zmax]
        box_coords = [box_edge_x, box_edge_y, box_edge_z]
        if prot == 'target':
            cmd.delete('Target_box')
            self.target_box_is_on_display = True
        else:
            cmd.delete('Off-Target_box')
            self.offtarget_box_is_on_display = True
        self.display_box(box_coords, cylinder_size, prot)

    def display_box(self, box, cylinder_size, prot):
        view = cmd.get_view()
        if prot == 'target':
            name = 'Target_box'
            color = [1.00 , 1.00 , 1.00]
        else:
            name = 'Off-Target_box'
            color = [0.50 , 0.78 , 0.50]
        obj = []
        # build cgo object
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
        axes = [[2.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 2.0]]
        xpos = [box[0][1] + (box[0][1] - box[0][0]) / 5., box[1][0], box[2][0]]
        cyl_text(obj, plain, xpos, 'X', 0.10, axes=axes)
        ypos = [box[0][0], box[1][1] + (box[1][1] - box[1][0]) / 5, box[2][0]]
        cyl_text(obj, plain, ypos, 'Y', 0.10, axes=axes)
        zpos = [box[0][0], box[1][0], box[2][1] + (box[2][1] - box[2][0]) / 5]
        cyl_text(obj, plain, zpos, 'Z', 0.10, axes=axes)
        cmd.load_cgo(obj, name)
        cmd.set_view(view)

# ----------------------------------------------------------------------
# Autodock/Vina plugin is Copyright (C) 2009 by Daniel Seeliger
#
#                        All Rights Reserved
#
# Permission to use, copy, modify, distribute, and distribute modified
# versions of this software and its documentation for any purpose and
# without fee is hereby granted, provided that the above copyright
# notice appear in all copies and that both the copyright notice and
# this permission notice appear in supporting documentation, and that
# the name of Daniel Seeliger not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# DANIEL SEELIGER DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS.  IN NO EVENT SHALL DANIEL SEELIGER BE LIABLE FOR ANY
# SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
# ----------------------------------------------------------------------
