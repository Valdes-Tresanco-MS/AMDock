from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time

class SplashScreen(QSplashScreen):
    '''
    Splash Screen
    Check necessary modules for AMDock
    '''
    def __init__(self, image, app):
        QSplashScreen.__init__(self, image, Qt.WindowStaysOnTopHint)

        progressBar = QProgressBar(self)
        progressBar.setGeometry(QRect(50,275,630,5))
        progressBar.setTextVisible(False)

        text = QLabel(self)
        text.setGeometry(QRect(60,280,650,25))
        text.setText('Loading modules...')
        self.show()
        self.setMask(image.mask())
        # time.sleep(0.5)
        modules = ['AutoDockTools','MolKit', 'PyBabel', 'AMDock','mglutil', 'Support','numpy','PyQt4']
        programs = ['pdb2pqr', 'pymol', 'obabel']
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
            progressBar.setValue(ml)
            app.processEvents()
        if len(self.non_loaded) is not 0:
            text.setText('Some modules have not been loaded... Please check that program is not corrupted')
            app.processEvents()
            time.sleep(4)
        else:
            text.setText('Initialiting AMDock...')
            app.processEvents()
            time.sleep(2)

    def import_error(self):
        if len(self.non_loaded) is 0:
            return True
        else:
            return False

