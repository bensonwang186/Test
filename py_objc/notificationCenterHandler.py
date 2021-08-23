import objc
import libdispatch

from Cocoa import NSObject
from AppKit import NSWorkspace, NSWorkspaceWillSleepNotification, NSWorkspaceDidWakeNotification, NSApplication
from Foundation import NSLog, NSThread, NSRunLoopCommonModes, NSRunLoop, NSTimer
from Utility import Logger
from PyObjCTools import AppHelper
import threading
import datetime, os, RootDir

class AppDelegate(NSObject):
    model = objc.ivar()
    delegateDone = objc.ivar()

    def setModel_(self, inModel):
        self.model = inModel

    def setDelegateDone_(self, flag):
        self.delegateDone = flag

    def testLog_(self, msg):
        NSLog("***print log++++++++***")
        msg = "[{0}]: message: {1}".format(str(datetime.datetime.now()), str(msg))

        debugFile = os.path.join(RootDir.PROJECT_ROOT_PATH, "nxdebug.txt")
        if not os.path.isfile(debugFile):
            with open(debugFile, 'w'):  # create a empty file
                pass

        with open(debugFile, 'r') as file:
            contents = file.readlines()

        index = len(contents) + 1
        contents.insert(index, (msg + "\n"))

        with open(debugFile, 'w') as file:
            contents = "".join(contents)
            file.write(contents)

    def delegateFunc(self):
        NSLog("***INTO  delegateFunc Start***")
        workspace = NSWorkspace.sharedWorkspace()
        notificationCenter = workspace.notificationCenter()
        notificationCenter.addObserver_selector_name_object_(
            self,
            self.receiveSleepNotification_,
            NSWorkspaceWillSleepNotification,
            None
        )
        notificationCenter.addObserver_selector_name_object_(
            self,
            self.receiveWakeNotification_,
            NSWorkspaceDidWakeNotification,
            None
        )

        # AppHelper.runConsoleEventLoop(installInterrupt=True)
        self.startLoop()
        NSLog("***INTO delegateFunc End***")

    def receiveSleepNotification_(self, notification):
        NSLog("receiveSleepNotification: %@", notification)
        NSLog("***daemon TEST Sleep (Begin)***")
        # self.model.dohibernate()
        self.testLog_("INTO SLEEP")
        NSLog("***daemon TEST Sleep (End)***")

    def receiveWakeNotification_(self, notification):
        NSLog("receiveWakeNotification: %@", notification)
        NSLog("***NSLOG TEST daemon wake (Begin)***")
        # self.model.dohibernateResume()
        self.testLog_("INTO WAKEUP")
        NSLog("***NSLOG TEST daemon wake (End)***")

    def createQueue(self):
        NSLog("***Dispatch Queue Start***")
        queue = libdispatch.dispatch_queue_create(b'EventLoopQueue', libdispatch.DISPATCH_QUEUE_SERIAL)
        # queue = libdispatch.dispatch_get_global_queue(2, 0)
        # queue = libdispatch.dispatch_get_main_queue()
        # libdispatch.dispatch_async(queue, self.delegateFunc)

        # libdispatch.dispatch_main()
        libdispatch.dispatch_async(queue, self.delegateFunc)
        # libdispatch.dispatch_async(queue, self.startLoop)

        NSLog("***Dispatch Queue End***")

    def startLoop(self):
        NSLog("***startLoop Start***")

        try:
            AppHelper.runConsoleEventLoop(installInterrupt=True)
        except Exception as e:
            NSLog("***startLoop error***")

        NSLog("***startLoop End***")

    def createThread(self):
        NSLog("***NS Thred Start***")
        # t = NSThread.alloc().initWithTarget_selector_object_(self, self.delegateFunc, "zero")
        # t.start()
        # AppHelper.runConsoleEventLoop(installInterrupt=True, mode=NSRunLoopCommonModes)

        NSThread.detachNewThreadSelector_toTarget_withObject_(self.delegateFunc, self, None)
        NSLog("***NS Thred End***")

class EventLoopThread(threading.Thread):
    def __init__(self):
        super(EventLoopThread, self).__init__()
        self.setDaemon(True)
        self.should_stop = False

    def run(self):
        NSLog('Starting event loop on background thread')
        AppHelper.runConsoleEventLoop(installInterrupt=True)

    def stop(self):
        NSLog('Stop the event loop')
        AppHelper.stopEventLoop()


if __name__ == '__main__':

    NSLog("***NSLOG INTO MAIN***")
    import platform
    if platform.system() == 'Darwin':

        # event_loop_thread = EventLoopThread()
        # event_loop_thread.start()
        app = AppDelegate.alloc().init()
        # app.createQueue()
        app.createThread()
        # app.threadStart()
        # app.delegateFunc()
        # app.startLoop()
        # AppHelper.stopEventLoop()

        # event_loop_thread.start()
        # event_loop_thread.stop()

        import time
        for i in range(1,100):
            NSLog("t1 count: %@", i)
            time.sleep(1)







