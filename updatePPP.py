import json
import os
import platform
import shutil
import subprocess
import sys
import pathlib
from datetime import datetime, timezone

if platform.system() == 'Darwin':
    from System import settings
    from model_Json import DBSession
    from model_Json.tables.Configuration import Configuration

macOS_lib_include_files = [
    'ClientHandler', 'ClientModel', 'controllers',
    'Events', 'handler_refactor', 'major',
    'model_Json', 'System', 'Utility', 'views'
]

PPP_INFO_PROPERTIES = 'log/PPPInfo.properties'
BY_INSTALLER_UPDATE_OR_RESTORATION = "By_Installer_Update_or_Restoration"
SOFTWARE_UPDATE_TYPE_VALUE_UPDATE = "Update"
SOFTWARE_UPDATE_TYPE_VALUE_RESTORE = "Restoration"
SOFTWARE_UPDATE_FROM_PPP_VERSION = "From_PPP_version"
SOFTWARE_UPDATE_TO_PPP_VERSION = "To_PPP_version"
SOFTWARE_UPDATE_RESULT = "Result"
SOFTWARE_UPDATE_RESULT_SUCCESS = "Success"
SOFTWARE_UPDATE_RESULT_FAILED = "Failed"
SOFTWARE_UPDATE_ERROR_MESSAGE = '(An error occurred while updating.)'

class updatePPP():
    def __init__(self, update_from_version):
        self.installer_path = os.path.join(pathlib.Path().absolute())
        self.download_update_file_folder = os.path.join(self.installer_path, 'update_file')
        self.backup_folder = os.path.join(self.installer_path, 'backup_ppp')
        self.update_from_version = update_from_version
        if 'm' in self.update_from_version:
            self.update_from_version = self.update_from_version.replace('m', '')
        if 'DEMO' in self.update_from_version:
            self.update_from_version = self.update_from_version.replace(' DEMO', '')
        self.update_to_version = ''

    def updateFile(self):
        try:
            self.backupLocalFile()
            current_version = self.update_from_version
            PPP_VERSION_PATH_TABLE = 'PPP_VERSION_PATH_TABLE.json'
            with open(os.path.join(self.download_update_file_folder, PPP_VERSION_PATH_TABLE)) as file:
                VersionPathTable = json.load(file)

            version_list = []
            for version in VersionPathTable['Versions']:
                version_list.append(version['Next_Version'])
            if len(version_list) > 1:
                self.update_to_version = version_list[len(version_list) - 1]
            else:
                self.update_to_version = version_list[0]

            for version in VersionPathTable['Versions']:
                if version['Version'] == current_version:
                    if platform.system() == 'Windows':
                        folder_name = 'PPP_UPDATE_TO_' + version['Next_Version'] + '_win'
                    elif platform.system() == 'Darwin':
                        folder_name = 'PPP_UPDATE_TO_' + version['Next_Version'] + '_mac'

                    self.copyUpdateFile(version['Next_Version'], folder_name)
                    current_version = version['Next_Version']

            self.dbMigrations()
            self.writeUpdateResult(SOFTWARE_UPDATE_RESULT_SUCCESS, '')
            self.startServiceAndProcess()
            print("Update PPP success!!")
            if platform.system() == 'Windows':
                sys.exit(50)

        except Exception as e:
            self.writeUpdateResult(SOFTWARE_UPDATE_RESULT_FAILED, str(e))
            if platform.system() == 'Windows':
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

        # update buildConfig.py
        self.updateBuildConfig(self.update_file_folder)

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

                if os.path.exists(original_file_folder):
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
            kill_ppp = 'killall PowerPanel\\ Personal'
            os.system(kill_ppp)

    def startServiceAndProcess(self):
        if platform.system() == 'Windows':
            start_pppService = 'net start \"PowerPanel Personal Service\"'
            os.system(start_pppService)

            # open_ppuser
            subprocess.Popen([os.path.join(self.installer_path, 'bin/ppuser.exe')])
            # open_ppp (Clint UI will open by watch dog)
            #subprocess.Popen([os.path.join(self.installer_path, 'PowerPanel Personal.exe'), 'first'])

        elif platform.system() == 'Darwin':
            open_ppp = 'open -a PowerPanel\\ Personal --args first'
            restart_pppService = '/bin/launchctl stop com.cyberpower.powerpanel-personal.daemon'
            os.system(open_ppp)
            os.system(restart_pppService)

    def dbMigrations(self):
        if platform.system() == 'Windows':
            subprocess.Popen([os.path.join(self.installer_path, 'upgrades.exe')])

        elif platform.system() == 'Darwin':
            subprocess.Popen([os.path.join(self.installer_path, 'upgrades')])

    def backupLocalFile(self):
        self.stopServiceAndProcess()
        # check back_ppp folder exist
        current_version = self.update_from_version
        backupFolderExist = False
        for file in os.listdir(self.installer_path):
            if 'backup_ppp' in file:
                backupFolderExist = True
                shutil.rmtree(os.path.join(self.installer_path, file))
                os.mkdir(self.backup_folder + current_version)
                break

        if not backupFolderExist:
            os.mkdir(self.backup_folder + current_version)

        no_backup_files = ['backup_ppp' + current_version, 'update_file', 'log', 'pppServiceMonitor.exe']

        # create backup file
        for file in os.listdir(self.installer_path):
            if file in no_backup_files:
                continue
            else:
                src = os.path.join(self.installer_path, file)
                if os.path.isdir(os.path.join(self.installer_path, file)):
                    dest = os.path.join(self.backup_folder + current_version, file)
                    shutil.copytree(src, dest)
                else:
                    dest = self.backup_folder + current_version
                    shutil.copy(src, dest)

        print("Backup PPP success!!")

    def updatePythonLibrary(self, update_file_folder):
        if platform.system() == 'Windows':
            python_library = 'python36.zip'
            if python_library in os.listdir(update_file_folder):
                src = os.path.join(update_file_folder, python_library)
                dest = self.installer_path
                os.remove(os.path.join(dest, python_library))
                shutil.copy(src, dest)
        elif platform.system() == 'Darwin':
            python_library = 'library.zip'
            if python_library in os.listdir(update_file_folder):
                src = os.path.join(update_file_folder, python_library)
                dest = os.path.join(self.installer_path, 'lib')
                os.remove(os.path.join(dest, python_library))
                shutil.copy(src, dest)

    def updateBuildConfig(self, update_file_folder):
        if platform.system() == 'Windows':
            buildConfig = 'buildConfig.cp36-win32.pyd'
            if buildConfig in os.listdir(update_file_folder):
                src = os.path.join(update_file_folder, buildConfig)
                dest = os.path.join(self.installer_path, 'System')
                os.remove(os.path.join(dest, buildConfig))
                shutil.copy(src, dest)
        elif platform.system() == 'Darwin':
            buildConfig = 'buildConfig.cpython-36m-darwin.so'
            if buildConfig in os.listdir(update_file_folder):
                src = os.path.join(update_file_folder, buildConfig)
                dest = os.path.join(self.installer_path, 'lib/System')
                os.remove(os.path.join(dest, buildConfig))
                shutil.copy(src, dest)

    def genPPPInfoproperties(self, update_result, error_message):
        utc_time = datetime.now(timezone.utc).astimezone()
        current_time = utc_time.strftime('%Y-%m-%d %H:%M:%S')
        if 'log' not in os.listdir(self.installer_path):
            os.mkdir(os.path.join(self.installer_path, 'log'))

        with open(os.path.join(self.installer_path, PPP_INFO_PROPERTIES), 'w') as file:
            file.write('#' + current_time + '\n')
            file.write(BY_INSTALLER_UPDATE_OR_RESTORATION + '=' + SOFTWARE_UPDATE_TYPE_VALUE_UPDATE + '\n')
            if update_result == SOFTWARE_UPDATE_RESULT_FAILED:
                file.write(SOFTWARE_UPDATE_RESULT + '=' + update_result + SOFTWARE_UPDATE_ERROR_MESSAGE + '\n')
            elif update_result == SOFTWARE_UPDATE_RESULT_SUCCESS:
                file.write(SOFTWARE_UPDATE_RESULT + '=' + update_result + '\n')
            file.write(SOFTWARE_UPDATE_FROM_PPP_VERSION + '=' + self.update_from_version + '\n')
            file.write(SOFTWARE_UPDATE_TO_PPP_VERSION + '=' + self.update_to_version + '\n')
            if not error_message == '':
                file.write('Exception = ' + error_message + '\n')
            file.close()

    def writeUpdateResult(self, update_result, error_message):
        if update_result == SOFTWARE_UPDATE_RESULT_SUCCESS:
            self.genPPPInfoproperties(SOFTWARE_UPDATE_RESULT_SUCCESS, '')

            if platform.system() == 'Darwin':
                with DBSession.db_session(settings.PPPE_DB) as session:
                    configuration = session.query(Configuration).first()
                    configuration.updateResult = 'updateSuccess'
                    session.commit()
                    session.close()

        elif update_result == SOFTWARE_UPDATE_RESULT_FAILED:
            self.genPPPInfoproperties(SOFTWARE_UPDATE_RESULT_FAILED, error_message)

            if platform.system() == 'Darwin':
                for file in os.listdir(self.installer_path):
                    if 'backup_ppp' in file:
                        PPPE_DB = "sqlite:///" + os.path.join(self.installer_path, file, 'assets/PPPE_Db.db')
                        with DBSession.db_session(PPPE_DB) as session:
                            configuration = session.query(Configuration).first()
                            configuration.updateResult = 'updateFail'
                            session.commit()
                            session.close()
                        workingDir = os.path.join(self.installer_path, file)
                        subprocess.Popen([os.path.join(self.installer_path, file, 'restorePPP')], cwd=workingDir)
                        break

if __name__ == '__main__':
    update_from_version = ''
    if sys.argv is not None and len(sys.argv) > 1:
        update_from_version = sys.argv[1]

    f = updatePPP(update_from_version)
    f.updateFile()