#!./bin/python

from PyQt4 import QtGui
import sys
from AMDock.splash_screen import SplashScreen
from AMDock.Docking_Program import AMDock
from AMDock.variables import Objects as ob

def run():
    if __name__ == "__main__":
        app = QtGui.QApplication(sys.argv)
        app.setStyle("cleanlooks")
        app.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(ob.app_icon)))
        app.setApplicationName('AMDock: Automatic Molecular Docking for AutoDock and AutoDock Vina')

        fapp = QtGui.QFont()
        fapp.setPointSize(11)
        fapp.setFamily('Times')
        app.setFont(fapp)

        splash = SplashScreen(QtGui.QPixmap(ob.splashscreen_path), app)
        main = AMDock()
        main.show()
        splash.finish(main)
        if splash.import_error():
            sys.exit(app.exec_())
        else:
            sys.exit(app.exit(1))
run()

