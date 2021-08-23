import win32serviceutil
import WinService
if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(WinService.PySvc, argv=['WinService.py', "remove"])