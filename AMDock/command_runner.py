from PyQt5.QtCore import QProcess, pyqtSignal, pyqtSlot, QObject, QRunnable, QThreadPool, QThread
from queue import Queue, Empty
import sys, traceback

class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
        No data
    error
        `tuple` (exctype, value, traceback.format_exc() )
    result
        `object` data returned from processing, anything
    progress
        `int` indicating % progress
    """
    finished = pyqtSignal(tuple)
    error = pyqtSignal(tuple)
    result = pyqtSignal(str, object)
    state = pyqtSignal(int)
    started = pyqtSignal(str)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    finished
        No data
    error
        `tuple` (exctype, value, traceback.format_exc() )
    result
        `object` data returned from processing, anything
    progress
        `int` indicating % progress
    """
    def __init__(self):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.signals = WorkerSignals()
        self.fn = None
        self.args = None
        self.kwargs = None
        self.setAutoDelete(False)

    def insert_function(self, fn, args, callable_name):
        self.fn = fn
        self.args = args
        self.callable_name = callable_name

    @pyqtSlot()
    def run(self):
        """ Initialise the runner function with passed args, kwargs."""
        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.signals.state.emit(2)
            method_list = [func for func in dir(self.fn) if callable(getattr(self.fn, func)) and not func.startswith(
                "__")]
            if self.args[0] in method_list:
                result = getattr(self.fn, self.args[0])()
            else:
                result = self.fn(*self.args)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(self.callable_name, result)  # Return the result of the processing
        finally:
            exctype, value = sys.exc_info()[:2]
            self.signals.state.emit(0)
            self.signals.finished.emit((self.callable_name, value, exctype))


class PROCESS(QObject):
    queue_finished = pyqtSignal(int)
    prog_finished = pyqtSignal(tuple)
    stoped = pyqtSignal(int, int) # 1: start, 0: finished, 2: error | queue
    state = pyqtSignal(int, str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.finished.connect(self.emit_finished)
        self.process.stateChanged.connect(self.emit_state)
        self.process_type = 0 # 0 process, 1 runnable
        self.threadpool = QThreadPool()
        self.worker = Worker()
        self.worker.signals.state.connect(self.emit_state)
        self.queue = None

    def emit_state(self, state):
        self.state.emit(state, self.prog_name)

    def emit_finished(self, exitcode, exitstatus):
        self.prog_finished.emit((self.prog_name, exitcode, exitstatus))

    def set_queue(self, queue):
        self.queue = queue

    def start_process(self):
        try:
            obj = self.queue.get(False)
            self.prog_name = list(obj.keys())[0]
            if callable(list(obj.values())[0][0]):
                self.process_type = 1
                funct = list(obj.values())[0][0]
                args = list(obj.values())[0][1]
                self.worker.insert_function(funct, args, self.prog_name)
                self.threadpool.start(self.worker)
            else:
                self.process_type = 0
                self.process.start(list(obj.values())[0][0],list(obj.values())[0][1])
        except Empty:
            self.queue_finished.emit(self.queue.name)

    def force_finished(self):
        # for process (programs)
        self.stoped.emit(1, self.queue.name)
        if self.process_type == 0:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
        else:
            if self.threadpool.activeThreadCount():
                self.threadpool.clear()
                self.threadpool.waitForDone()
        with self.queue.mutex:
            self.queue.queue.clear()
        self.stoped.emit(0, self.queue.name)


class THREAD(QThread):
    def __init__(self, parent, text):
        super(THREAD, self).__init__(parent)
        self.out = text
        self.AMDock = parent

    def run(self):
        if not self.AMDock.project.prog in ['AutoDock Vina', 'AutoDock Vina B', 'AutoLigand', 'AutoLigand B']:
            if self.AMDock.log_level ==2:
                self.AMDock.log_widget.textedit.append(self.out)
        if self.AMDock.project.prog == 'AutoDock Vina':
            if self.AMDock.log_level == 2:
                if '*' in self.out:
                    cursor = self.AMDock.log_widget.textedit.textCursor()
                    cursor.movePosition(cursor.EndOfWord)
                    cursor.insertText(self.out)
                else:
                    cursor = self.AMDock.log_widget.textedit.textCursor()
                    cursor.movePosition(cursor.End)
                    cursor.insertText(self.out)
        elif self.AMDock.project.prog == 'AutoDock Vina B':
            if self.AMDock.log_level == 2:
                if '*' in self.out:
                    cursor = self.AMDock.log_widget.textedit.textCursor()
                    cursor.movePosition(cursor.EndOfWord)
                    cursor.insertText(self.out)
                else:
                    cursor = self.AMDock.log_widget.textedit.textCursor()
                    cursor.movePosition(cursor.End)
                    cursor.insertText(self.out)
