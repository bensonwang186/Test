import os
import platform
import shutil
import subprocess
import sys
import time
import pathlib
from datetime import datetime, timezone

if platform.system() == 'Darwin':
    from System import settings
    from model_Json import DBSession
    from model_Json.tables.Configuration import Configuration

PPP_INFO_PROPERTIES = 'log/PPPInfo.properties'
BY_INSTALLER_UPDATE_OR_RESTORATION = "By_Installer_Update_or_Restoration"
SOFTWARE_UPDATE_TYPE_VALUE_UPDATE = "Update"
SOFTWARE_UPDATE_TYPE_VALUE_RESTORE = "Restoration"
SOFTWARE_UPDATE_FROM_PPP_VERSION = "From_PPP_version"
SOFTWARE_UPDATE_TO_PPP_VERSION = "To_PPP_version"
SOFTWARE_UPDATE_RESULT = "Result"
SOFTWARE_UPDATE_RESULT_SUCCESS = "Success"
SOFTWARE_UPDATE_RESULT_FAILED = "Failed"

class restorePPP():
    def __init__(self, restore_from_version):
        self.installer_path = os.path.join(pathlib.Path().absolute(), '..')
        self.restore_from_version = restore_from_version
        self.restore_to_version = ''

    def restorePPP(self):
        try:
            for installer_file in os.listdir(self.installer_path):
                if 'backup_ppp' in installer_file:
                    self.restore_to_version = installer_file.replace('backup_ppp', '')
                    self.stopServiceAndProcess()
                    backup_folder = os.path.join(self.installer_path, installer_file)
                    for file in os.listdir(backup_folder):
                        src = os.path.join(backup_folder, file)
                        if os.path.isdir(src):
                            dest = os.path.join(self.installer_path, file)
                            if file in os.listdir(self.installer_path):
                                shutil.rmtree(dest)
                            shutil.copytree(src, dest)
                        else:
                            dest = self.installer_path
                            if file in os.listdir(dest):
                                os.remove(os.path.join(dest, file))
                            shutil.copy(src, dest)

                    time.sleep(10)
                    self.writeUpdateResult()
                    self.startServiceAndProcess()
                    print("Restore PPP success!!")
                    if platform.system() == 'Windows':
                        sys.exit(50)

        except Exception as e:
            self.genPPPInfoproperties(SOFTWARE_UPDATE_RESULT_FAILED, str(e))
            self.startServiceAndProcess()
            if platform.system() == 'Windows':
                sys.exit(100)

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

    def genPPPInfoproperties(self, restore_result, error_message):
        # run for update fail
        if self.restore_from_version == '':
            pass
        else:
            utc_time = datetime.now(timezone.utc).astimezone()
            current_time = utc_time.strftime('%Y-%m-%d %H:%M:%S')
            if 'log' not in os.listdir(self.installer_path):
                os.mkdir(os.path.join(self.installer_path, 'log'))

            with open(os.path.join(self.installer_path, PPP_INFO_PROPERTIES), 'w') as file:
                file.write('#' + current_time + '\n')
                file.write(BY_INSTALLER_UPDATE_OR_RESTORATION + '=' + SOFTWARE_UPDATE_TYPE_VALUE_RESTORE + '\n')
                file.write(SOFTWARE_UPDATE_RESULT + '=' + restore_result + '\n')
                file.write(SOFTWARE_UPDATE_FROM_PPP_VERSION + '=' + self.restore_from_version + '\n')
                file.write(SOFTWARE_UPDATE_TO_PPP_VERSION + '=' + self.restore_to_version + '\n')
                file.close()

        if not error_message == '':
            with open(os.path.join(self.installer_path, PPP_INFO_PROPERTIES), 'a') as file:
                file.write('Exception = ' + error_message + '\n')
                file.close()

    def writeUpdateResult(self):
        if platform.system() == 'Windows':
            self.genPPPInfoproperties(SOFTWARE_UPDATE_RESULT_SUCCESS, '')

        elif platform.system() == 'Darwin':
            with DBSession.db_session(settings.PPPE_DB) as session:
                configuration = session.query(Configuration).first()
                if configuration.updateResult == 'updateFail':
                    session.close()
                elif configuration.updateResult == None:
                    session.close()
                    PPPE_DB = "sqlite:///" + os.path.join(self.installer_path, 'assets/PPPE_Db.db')
                    with DBSession.db_session(PPPE_DB) as session:
                        configuration = session.query(Configuration).first()
                        configuration.updateResult = 'restoreSuccess'
                        session.commit()
                        session.close()
                    self.genPPPInfoproperties(SOFTWARE_UPDATE_RESULT_SUCCESS, '')

if __name__ == '__main__':
    restore_from_version = ''
    if sys.argv is not None and len(sys.argv) > 1:
        restore_from_version = sys.argv[1]

    f = restorePPP(restore_from_version)
    f.restorePPP()