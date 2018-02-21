from PyQt4.QtCore import QProcess, pyqtSignal, QString
import sys, Queue, time

class Worker(QProcess):
    '''Implement the function Qprocess. Use Queue.Queue for the administration of the processes.'''
    prog_finished = pyqtSignal(str,int, str)
    prog_started = pyqtSignal(str)
    function_out = pyqtSignal(int)
    function_error = pyqtSignal(str)
    function_started = pyqtSignal()
    queue_finished = pyqtSignal(str,bool)
    # queue_stage = pyqtSignal(str,bool)
    def __init__(self):
        QProcess.__init__(self)

        # self.error.connect(self.error_str)
        self.started.connect(self.prog_start)
        self.function_out.connect(self.info)
        self.function_error.connect(self.error_str)
        self.function_started.connect(self.prog_start)
        self.finished.connect(self.info)
        self.setProcessChannelMode(QProcess.MergedChannels)
        self._error = '0'
    def init(self,q, qname):
        '''Entry of the queue'''
        self.queue = q
        self.queue_name = qname
        self.queue_finished.emit(self.queue_name,False)
    def error_str(self, err):
        self._error = err

    def info(self, int):
        '''Emit a signal when finishing the process with the name of the program, exit code and error if exist'''
        self.prog_finished.emit(self.prog_name,int, self._error)
    def prog_start(self):
        ''' Emit a Signal when beginning the process whit name of the program'''
        self.prog_started.emit(self.prog_name)

    def __del__(self):
        '''Finish the current process.'''
        self.terminate()
        if not self.waitForFinished(1000):
            self.kill()

    def start_process(self):
        '''Start the processes according to the order of queue.'''
        time.sleep(0.5)
        try:
            obj = self.queue.get(False)
            self.prog_name = obj.keys()[0]
            if 'function' in obj.keys()[0]:
                try:
                    self.function_started.emit()
                    apply(obj.values()[0][0],obj.values()[0][1])
                    self.function_out.emit(0)
                except:
                    self.function_error.emit(str(sys.exc_info()[1]))
                    self.function_out.emit(-9999999999)
            else:

                self.start(obj.values()[0][0],obj.values()[0][1])
            time.sleep(0.5)
        except Queue.Empty:
            self.queue_finished.emit(self.queue_name, True)


