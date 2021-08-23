import json
import os
import pathlib
import platform
import shutil
import subprocess
import sys
import RootDir
from System import settings

macOS_lib_include_files = [
    'ClientHandler', 'ClientModel', 'controllers',
    'Events', 'handler_refactor', 'major',
    'model_Json', 'System', 'Utility', 'views'
]

class updatePPP():
    def __init__(self):
        self.PROJECT_ROOT_PATH = RootDir.PROJECT_ROOT_PATH
        if platform.system() == 'Windows':
            self.installer_path = os.path.join(os.environ["ProgramFiles(x86)"], 'CyberPower PowerPanel Personal')
        elif platform.system() == 'Darwin':
            self.installer_path = '/Applications/CyberPower PowerPanel Personal/PowerPanel Personal.app/Contents/MacOS'
        self.download_update_file_folder = os.path.join(self.installer_path, 'update_file')
        self.backup_folder = os.path.join(self.installer_path, 'backup_ppp')

    def updateFile(self):
        try:
            self.backupLocalFile()
            now_version = '2.2.5'
            if 'm' in now_version:
                now_version = now_version.replace('m', '')
            if 'DEMO' in now_version:
                now_version = now_version.replace(' DEMO', '')

            PPP_VERSION_PATH_TABLE = 'PPP_VERSION_PATH_TABLE.jsona'
            with open(os.path.join(self.download_update_file_folder, PPP_VERSION_PATH_TABLE)) as file:
                VersionPathTable = json.load(file)

            for version in VersionPathTable['Versions']:
                if version['Version'] == now_version:
                    if platform.system() == 'Windows':
                        folder_name = 'PPP_UPDATE_TO_' + version['Next_Version'] + '_win'
                    elif platform.system() == 'Darwin':
                        folder_name = 'PPP_UPDATE_TO_' + version['Next_Version'] + '_mac'

                    self.copyUpdateFile(version['Next_Version'], folder_name)
                    now_version = version['Next_Version']

            self.dbMigrations()

            if platform.system() == 'Darwin':
                with open(os.path.join(self.installer_path, 'success'), 'w') as file:
                    file.write('success')

            self.startServiceAndProcess()

            if platform.system() == 'Windows':
                sys.exit(50)
            print("Update PPP success!!")

        except Exception:
            if platform.system() == 'Darwin':
                with open(os.path.join(self.installer_path, 'fail'), 'w') as file:
                    file.write('fail')
                for file in os.listdir(self.installer_path):
                    if 'backup_ppp' in file:
                        subprocess.Popen([os.path.join(self.installer_path, file, 'restorePPP')])
                        break
            elif platform.system() == 'Windows':
                sys.exit(100)

    def copyUpdateFile(self, next_version, folder_name):
        self.update_file_folder = os.path.join(self.download_update_file_folder, next_version, folder_name)
        if platform.system() == 'Windows':
            self.update_json = os.path.join(self.update_file_folder, folder_name.replace('_win', '') + '.json')
        elif platform.system() == 'Darwin':
            self.update_json = os.path.join(self.update_file_folder, folder_name.replace('_mac', '') + '.json')

        with open(self.update_json) as f:
            json_data = json.load(f)

        # update packages
        if 'packages' in os.listdir(self.update_file_folder):
            self.updatePackage()

        # if executables change, update python library
        self.updatePythonLibrary(self.update_file_folder)

        files = json_data['Files']
        for file in files:
            if platform.system() == 'Windows':
                if 'updatePPP.exe' in file['Dest'] or 'restorePPP.exe' in file['Dest']:
                    continue
            elif platform.system() == 'Darwin':
                if 'restorePPP' in file['Dest'] or 'restorePPP' in file['Dest']:
                    continue
            # R : Rename(ex:R094   help/english/index.html	help/english/index.htm)
            if file['Action'] == 'Rename':
                if '/' in file['Src']:
                    index = file['Src'].rindex('/')
                    src = file['Src'][index+1:]
                    if self.isMaclibFolderExist(file['Src']):
                        original_file_folder = os.path.join(self.installer_path, 'lib', file['Src'][:index])
                    else:
                        original_file_folder = os.path.join(self.installer_path, file['Src'][:index])
                else:
                    src = file['Src']
                    original_file_folder = os.path.join(self.installer_path)

                for original_file in os.listdir(original_file_folder):
                    if not os.path.isdir(original_file):
                        if src.split('.')[0] in original_file.split('.')[0]:
                            original_file_path = os.path.join(original_file_folder, original_file)
                            os.remove(original_file_path)

                Dest = os.path.join(self.update_file_folder, str(file['Dest']))
                src = Dest
                target = self.targetPath(file['Dest'])
                shutil.copy(src, target)

            # D : Delete(ex:D	test.py)
            elif file['Action'] == 'Delete':
                if '/' in file['Src']:
                    index = file['Src'].rindex('/')
                    src = file['Src'][index+1:]
                    if self.isMaclibFolderExist(file['Src']):
                        original_file_folder = os.path.join(self.installer_path, 'lib', file['Src'][:index])
                    else:
                        original_file_folder = os.path.join(self.installer_path, file['Src'][:index])
                else:
                    src = file['Src']
                    original_file_folder = os.path.join(self.installer_path)

                for original_file in os.listdir(original_file_folder):
                    if not os.path.isdir(original_file):
                        if src.split('.')[0] in original_file.split('.')[0]:
                            original_file = os.path.join(original_file_folder, original_file)
                            os.remove(original_file)

            # M : Modify(ex:M	help/english/index.htm)
            elif file['Action'] == 'Modify':
                original_file = os.path.join(self.installer_path, file['Dest'])
                if os.path.isfile(original_file):
                    os.remove(original_file)

                build_path = os.path.join(self.update_file_folder, file['Dest'])
                src = build_path
                target = self.targetPath(file['Dest'])
                shutil.copy(src, target)

            # A : Add(ex:A     help/english/index.html)
            elif file['Action'] == 'Add':
                build_path = os.path.join(self.update_file_folder, file['Dest'])
                src = build_path
                target = self.targetPath(file['Dest'])
                shutil.copy(src, target)

    def targetPath(self, file_path):
        if '/' in file_path:
            index = str(file_path).rindex('/')
            target = os.path.join(self.installer_path, str(file_path)[:index])
        else:
            target = os.path.join(self.installer_path)

        return target

    def isMaclibFolderExist(self, file_path):
        libExist = False
        if platform.system() == 'Darwin':
            if str(file_path).split('/')[0] in macOS_lib_include_files:
                libExist = True

        return libExist

    def updatePackage(self):
        packages_folder = os.path.join(self.update_file_folder, 'packages')

        for file in os.listdir(packages_folder):
            src = os.path.join(packages_folder, file)
            if os.path.isdir(src):
                if platform.system() == 'Darwin':
                    dest = os.path.join(self.installer_path, 'lib')
                elif platform.system() == 'Windows':
                    dest = os.path.join(self.installer_path)

                if file in os.listdir(dest):
                    shutil.rmtree(os.path.join(dest, file))
                shutil.copytree(src, os.path.join(dest, file))
            else:
                if platform.system() == 'Darwin':
                    dest = os.path.join(self.installer_path, 'lib')
                elif platform.system() == 'Windows':
                    dest = os.path.join(self.installer_path)

                if file in os.listdir(dest):
                    os.remove(os.path.join(dest, file))
                shutil.copy(src, dest)

    def stopServiceAndProcess(self):
        if platform.system() == 'Windows':
            kill_ppuser = 'taskkill /f /im \"ppuser.exe\"'
            kill_ppp = 'taskkill /f /im \"PowerPanel Personal.exe\"'
            stop_pppService = 'net stop \"PowerPanel Personal Service\"'
            os.system(kill_ppuser)
            os.system(kill_ppp)
            os.system(stop_pppService)

        elif platform.system() == 'Darwin':
            sys.exit(0)
            kill_ppp = 'killall PowerPanel\\ Personal'
            # kill_ppp = 'launchctl unload /Library/LaunchAgents/com.cyberpower.powerpanel-personal.client.plist'
            os.system(kill_ppp)

    def startServiceAndProcess(self):
        if platform.system() == 'Windows':
            start_pppService = 'net start \"PowerPanel Personal Service\"'
            os.system(start_pppService)

            # open_ppuser
            subprocess.Popen([os.path.join(self.installer_path, 'bin/ppuser.exe')])
            # open_ppp
            subprocess.Popen([os.path.join(self.installer_path, 'PowerPanel Personal.exe'), 'first'])

        elif platform.system() == 'Darwin':
            # open_ppp = 'open -a PowerPanel\\ Personal'
            # open_ppp = 'launchctl load /Library/LaunchAgents/com.cyberpower.powerpanel-personal.client.plist'
            subprocess.Popen([os.path.join(self.installer_path, 'PowerPanel Personal')])
            restart_pppService = 'sudo /bin/launchctl stop com.cyberpower.powerpanel-personal.daemon'
            # os.system(open_ppp)
            os.system(restart_pppService)

    def dbMigrations(self):
        if platform.system() == 'Windows':
            subprocess.Popen([os.path.join(self.installer_path, 'upgrades.exe')])

        elif platform.system() == 'Darwin':
            subprocess.Popen([os.path.join(self.installer_path, 'upgrades')])

    def backupLocalFile(self):
        self.stopServiceAndProcess()

        now_version = '2.2.5'
        if 'm' in now_version:
            now_version = now_version.replace('m', '')
        if 'DEMO' in now_version:
            now_version = now_version.replace(' DEMO', '')

        # check back_ppp folder exist
        backupFolderExist = False
        for file in os.listdir(self.installer_path):
            if 'backup_ppp' in file:
                backupFolderExist = True
                shutil.rmtree(os.path.join(self.installer_path, file))
                os.mkdir(self.backup_folder + now_version)
                break

        if not backupFolderExist:
            os.mkdir(self.backup_folder + now_version)

        no_backup_files = ['backup_ppp' + now_version, 'update_file']

        # create backup file
        for file in os.listdir(self.installer_path):
            if file in no_backup_files:
                continue
            else:
                src = os.path.join(self.installer_path, file)
                if os.path.isdir(os.path.join(self.installer_path, file)):
                    dest = os.path.join(self.backup_folder + now_version, file)
                    shutil.copytree(src, dest)
                else:
                    dest = self.backup_folder + now_version
                    shutil.copy(src, dest)

        print("Backup PPP success!!")

    def updatePythonLibrary(self, update_file_folder):
        if platform.system() == 'Windows':
            python_library = 'python36.zip'
            if python_library in os.listdir(update_file_folder):
                src = os.path.join(update_file_folder, python_library)
                dest = os.path.join(self.installer_path)
                if python_library in os.listdir(self.installer_path):
                    os.remove(os.path.join(self.installer_path, python_library))
                shutil.copy(src, dest)
        elif platform.system() == 'Darwin':
            python_library = 'library.zip'
            if python_library in os.listdir(update_file_folder):
                src = os.path.join(update_file_folder, python_library)
                dest = os.path.join(self.installer_path, 'lib')
                if python_library in os.listdir(os.path.join(self.installer_path, 'lib')):
                    os.remove(os.path.join(self.installer_path, 'lib', python_library))
                shutil.copy(src, dest)

if __name__ == '__main__':

    # f = updatePPP()
    # f.stopServiceAndProcess()
    # f.startServiceAndProcess()
    # try:
    #     print('dsadas')
    #     os.remove(os.path.join('python_library'))
    # except Exception as e:
    #     aaa = str(e)
    #     print(aaa)
    #     print(e.message)
    win_include_files = [
        'bin', 'ClientHandler', 'ClientModel', 'controllers', 'Events', 'handler_refactor', 'help',
        'i18n', 'major', 'migrations', 'model_Json', 'resources', 'System', 'Utility', 'views',
        'alembic.ini', 'CountryTable.xml', 'd1.crt', 'd1.key', 'Daemon.cpython-36.pyc',
        'installMonitorSrv.bat', 'installService.bat', 'PowerPanel Personal.exe', 'ppped.exe', 'pppServiceMonitor.exe',
        'removeMonitorSrv.bat', 'rootCA.crt', 'RootDir.py', 'set_srv.bat', 'startClient.bat', 'startMonitorSrv.bat',
        'startService.bat', 'stopMonitorSrv.bat', 'stopService.bat', 'uninstall.exe', 'unstallService.exe',
        'upgrades.exe', 'WinService.py', 'updatePPP.exe', 'restorePPP.exe',
        'cx_Logging.cp36-win32.pyd', 'mfc140u.dll', 'MSVCP140.dll', 'perfmon.pyd', 'pyexpat.pyd', 'python3.dll',
        'python36.dll', 'python36.zip', 'pythoncom36.dll', 'pywintypes36.dll', 'Qt5Core.dll', 'Qt5Gui.dll',
        'Qt5Network.dll', 'Qt5Widgets.dll', 'select.pyd', 'servicemanager.pyd', 'sip.pyd', 'sqlite3.dll',
        'unicodedata.pyd', 'VCRUNTIME140.dll', 'win32api.pyd', 'win32event.pyd', 'win32evtlog.pyd', 'win32gui.pyd',
        'win32service.pyd', 'win32ui.pyd', 'win32wnet.pyd', 'winsound.pyd', '_asyncio.pyd', '_bz2.pyd',
        '_cffi_backend.cp36-win32.pyd', '_ctypes.pyd', '_ctypes_test.pyd', '_decimal.pyd', '_elementtree.pyd',
        '_hashlib.pyd', '_lzma.pyd', '_multiprocessing.pyd', '_overlapped.pyd', '_socket.pyd', '_sqlite3.pyd',
        '_ssl.pyd', '_testbuffer.pyd', '_testcapi.pyd', '_tkinter.pyd', '_win32sysloader.pyd'
    ]

    win_include_files_all = {'PyQt5.uic.widget-plugins', 'wsgiref', 'pywintypes36.dll', '_bz2.pyd', 'asyncio', '__pycache__', 'keyring', 'pythoncom36.dll', 'win32api.pyd', 'pyasn1', 'win32ui.pyd', 'markupsafe', 'mediaservice', 'win32gui.pyd', 'unicodedata.pyd', 'logging', '_testbuffer.pyd', '_ctypes.pyd', 'httplib2', 'python3.dll', 'certifi', '_elementtree.pyd', 'ctypes', 'tcl', 'Qt5Widgets.dll', 'cx_Logging.cp36-win32.pyd', '_ssl.pyd', 'pywin', 'select.pyd', 'Cython', 'mako', 'multiprocessing', 'alembic', 'bs4', 'pydoc_data', 'lib2to3', '_tkinter.pyd', 'Qt5Network.dll', '_sqlite3.pyd', 'pyximport', 'servicemanager.pyd', 'collections', 'pyfcm', '_testcapi.pyd', 'PyQt5', 'google', 'platforms', 'distutils', 'http', 'concurrent', 'json', 'pyasn1_modules', 'tk', 'winsound.pyd', 'requests', 'apiclient', 'perfmon.pyd', 'MSVCP140.dll', 'python36.zip', '_overlapped.pyd', 'imageformats', 'sqlite3.dll', 'urllib', '_hashlib.pyd', '_socket.pyd', 'pycparser', 'Qt5Gui.dll', '_asyncio.pyd', 'email', 'win32com', 'win32evtlog.pyd', 'sip.pyd', 'win32service.pyd', '_ctypes_test.pyd', 'importlib', 'uritemplate', 'sqlalchemy', 'cryptography', 'python36.dll', 'sqlite3', 'paho', 'rsa', '_cffi_backend.cp36-win32.pyd', 'pkg_resources', 'pyexpat.pyd', 'cffi', 'babel', 'idna', '_decimal.pyd', 'VCRUNTIME140.dll', 'dateutil', 'html', 'test', 'asn1crypto', 'win32wnet.pyd', '_multiprocessing.pyd', 'Qt5Core.dll', '_win32sysloader.pyd', 'encodings', '_lzma.pyd', 'requests_toolbelt', 'mfc140u.dll', 'win32event.pyd', 'googleapiclient', 'pytz', 'unittest', 'oauth2client', 'tkinter', 'urllib3', 'xml', 'adodbapi', 'chardet', 'xmlrpc', 'setuptools'}


    if platform.system() == 'Windows':
        installer_path = os.path.join(os.environ["ProgramFiles(x86)"], 'CyberPower PowerPanel Personal')
    elif platform.system() == 'Darwin':
        installer_path = '/Applications/CyberPower PowerPanel Personal/PowerPanel Personal.app/Contents/MacOS'

    # for file in os.listdir(r'C:\Users\benson.wang.CPS\Download s\build\build\exe.win32-3.6'):
    #     if file in win_include_files:
    #         if os.path.isdir(file):
    #             shutil.rmtree(os.path.join(r'C:\Users\benson.wang.CPS\Downloads\build\build\exe.win32-3.6', file))
    #         else:
    #             os.remove(os.path.join(r'C:\Users\benson.wang.CPS\Downloads\build\build\exe.win32-3.6', file))

    installer_pathaa = os.path.join(pathlib.Path().absolute(), "..")
    installer_pathbb = settings.PROJECT_ROOT_PATH
    aa = installer_pathaa
    bb = installer_pathbb