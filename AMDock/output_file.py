class OutputFile:
    def __init__(self, parent):
        self.AMDock = parent
        self.ofile = None

    def file_header(self, filename):
        self.ofile = open(filename, 'w')
        self.ofile.write('################################################################################\n'
                         '#            ___________          ___________          ___________             #\n'
                         '#           / __     __ \        /   _   _   \        /____ _    _\            #\n'
                         '#          /  \ \   / /  \      /   | |_| |   \      /|_  /|  \ | |\           #\n'
                         '#         /    \ \_/ /    \    /    |___  |    \    /  / /_| |\\\| | \          #\n'
                         '#        /      \___/      \  /       __|_|     \  /  /____|_| \__|  \         #\n'
                         '#        \      // \\\      /  \      // \\\      /  \      /_*_\      /         #\n'
                         '#         \    //   \\\    /    \    //   \\\    /    \    //   \\\    /          #\n'
                         '#          \  //     \\\  /      \  //     \\\  /      \  //     \\\  /           #\n'
                         '#           \//       \\\/        \//       \\\/        \//       \\\/            #\n'
                         '#            /_________\          /_________\          /_________\             #\n'
                         '#           Autodock Vina          Autodock4           AutodockZn              #\n'
                         '#    _____  __________________________________________________________         #\n'
                         '#    \    \ \    ______   __    __   _____                      _   __\        #\n'
                         '#     \    \ \  |  __  | |  \  /  | |  __  \   ______   ______ | | / / \       #\n'
                         '#      \    \ \ | |  | | |   \/   | | |  \  | |  __  | |  ____|| |/ /   \      #\n'
                         '#       \    \ \| |__| | | |\__/| | | |   | | | |  | | | |     |   /     \     #\n'
                         '#       /    / /|  __  | | |    | | | |   | | | |  | | | |     |   \     /     #\n'
                         '#      /    / / | |  | | | |    | | | |__/  | | |__| | | |____ | |\ \   /      #\n'
                         '#     /    / /  |_|  |_| |_|    |_| |______/  |______| |______||_| \_\ /       #\n'
                         '#    /____/ /_________________________________________________________/        #\n'
                         '#                                                                              #\n'
                         '################################################################################\n'
                         '                 ____________________________________________                   \n'
                         '                |'  + ('AMDock {}'.format(*self.AMDock.version.split()[0])
                                                 ).center(44) + '|                  \n'
                         '                |         Assisted Molecular Docking         |                  \n'
                         '                |      with AutoDock4 and AutoDock Vina      |                  \n'
                         '                |                                            |                  \n'
                         '                |          Mario S. Valdes-Tresanco          |                  \n'
                         '                |          Mario E. Valdes-Tresanco          |                  \n'
                         '                |           Pedro A. Valiente, PhD           |                  \n'
                         '                |            Ernesto Moreno, PhD             |                  \n'
                         '                | For help or suggestion, please contact us  |                  \n'
                         '                |       mariosergiovaldes145@gmail.com       |                  \n'
                         '                |____________________________________________|                  \n'
                         '\n\n')

    def out2file(self, info):
        self.ofile.write(info)

    def conclude(self):
        self.ofile.close()
