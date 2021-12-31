import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class SplashScreen(QSplashScreen):
    """
    Splash Screen
    Check necessary modules for AMDock
    """

    def __init__(self, image, app):
        QSplashScreen.__init__(self, image, Qt.WindowStaysOnTopHint)

        progress_bar = QProgressBar(self)
        progress_bar.setGeometry(QRect(50, 275, 630, 5))
        progress_bar.setTextVisible(False)

        text = QLabel(self)
        text.setGeometry(QRect(60, 280, 650, 25))
        text.setText('Loading modules...')
        self.show()
        self.setMask(image.mask())
        modules = ['AutoDockTools', 'MolKit', 'PyBabel', 'AMDock', 'mglutil', 'numpy', 'PyQt5']
        ml = 0
        self.non_loaded = []
        for i in modules:
            try:
                text.setText('Loading Module: %s... Done' % i)
                __import__(i)
            except ImportError:
                self.non_loaded.append(i)
                text.setText('Error... Cann\'t be loaded Module: %s' % i)
            time.sleep(0.2)
            ml += 12.5
            progress_bar.setValue(ml)
            app.processEvents()
        print(self.non_loaded)
        if len(self.non_loaded) != 0:
            text.setText('Some modules have not been loaded... Please check that program is not corrupted')
            time.sleep(5)
            app.processEvents()
        else:
            text.setText('Initialiting AMDock...')
            app.processEvents()
            time.sleep(2)

    def import_error(self):
        if len(self.non_loaded) == 0:
            return True
        else:
            return False
