import platform
from tkinter import messagebox
from typing import Any, Callable
from PyQt5.QtCore import pyqtSlot,QRunnable,QThreadPool, QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from src.action_funcs import infoPopup

class WorkerSignals(QObject):
    finished = pyqtSignal()

class Worker(QRunnable):
    '''
    Worker thread
    '''
    task : Callable
    def __init__(self, func):
        super().__init__()
        self.task = func
        self.signals = WorkerSignals() 

    @pyqtSlot()
    def run(self):
        '''
        Your code goes in this function
        '''
        print("Thread start")
        self.task()     
        print("Thread complete")        
        self.signals.finished.emit()

class ThreadManager():
    __instance = None    
    threadpool :QThreadPool

    workerLoadingPopups : dict[Worker, Any]

    def startTask(self, taskFunc:Callable):
        worker = Worker(taskFunc)    
        self._promptLoading(worker)

        worker.signals.finished.connect(lambda work=worker: self.taskFinished(work))
        self.threadpool.start(worker)
    
    def startTaskWithCallbackTask(self, taskFunc:Callable, createFunc:Callable):
        worker = Worker(taskFunc)
        self._promptLoading(worker)
        worker.signals.finished.connect(lambda createF=createFunc, work=worker: self.preTaskFinished(createF,work))
        self.threadpool.start(worker)
            
    def _promptLoading(self, worker: Worker):
        if (platform.system() == "Windows"):
            self.workerLoadingPopups[worker] = infoPopup("Loading\nThis is slow on Windows...")
        else:
            self.workerLoadingPopups[worker] = infoPopup("Loading")

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance                      = super().__new__(cls)                        
            cls.__instance.threadpool           = QThreadPool()        
            cls.__instance.workerLoadingPopups  = dict[Worker, Any]()

        return cls.__instance    
    
    def preTaskFinished(self, mainContinuationTask: Callable, worker : Worker):
        print("Initiate continuation from main thread")
        loadbox: QMessageBox = self.workerLoadingPopups[worker]
        loadbox.accept()
        mainContinuationTask()

    def taskFinished(self, worker : Worker):
        loadbox: QMessageBox = self.workerLoadingPopups[worker]
        loadbox.accept()