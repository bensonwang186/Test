import hashlib
import json
import os
import shutil
import subprocess
import sys
import traceback
import zipfile
import requests
import platform
import pytz

from pathlib import Path
from time import time, sleep
from datetime import datetime, timezone

from PyQt5.QtCore import QTimer

from Utility import Logger
from major import Command
from System import systemDefine, systemFunction, settings, buildConfig
from model_Json import DBSession
from model_Json.tables.Configuration import Configuration
from model_Json.UpdateStatusData import UpdateStatusData

REQUEST_TIMEOUT = 10
PPP_DOWNLOAD_FAILED = "downloading_failed"
PPP_UPDATE_SUCCESS = "updated_success"
PPP_UPDATE_FAILED = "updating_failed"
PPP_RESTORE_SUCCESS = "restored_success"
PPP_RESTORE_FAILED = "restoring_failed"
PPP_CLIENT_CHECKED = "client_checked"

PPP_INFO_PROPERTIES = 'log/PPPInfo.properties'
BY_INSTALLER_UPDATE_OR_RESTORATION = "By_Installer_Update_or_Restoration"
SOFTWARE_UPDATE_TYPE_VALUE_UPDATE = "Update"
SOFTWARE_UPDATE_TYPE_VALUE_RESTORE = "Restoration"
SOFTWARE_UPDATE_FROM_PPP_VERSION = "From_PPP_version"
SOFTWARE_UPDATE_TO_PPP_VERSION = "To_PPP_version"
SOFTWARE_UPDATE_RESULT = "Result"
SOFTWARE_UPDATE_RESULT_SUCCESS = "Success"
SOFTWARE_UPDATE_RESULT_FAILED = "Failed"
SOFTWARE_UPDATE_DOWNLOAD_ERROR_MESSAGE = '(An error occurred while downloading the updates.)'

class SoftwareUpdateHandler:

    def __init__(self, server):
        self.server = server
        # Client
        self.server.check_update_signal.connect(self.check_update_from_cloud)
        self.server.run_update_signal.connect(self.run_software_update)
        self.server.run_restore_signal.connect(self.run_software_restore)
        self.server.update_status_signal.connect(self.update_status)
        self.server.update_result_signal.connect(self.get_update_result)

        # Watch Dog
        self.server.watch_dog_software_result_signal.connect(self.set_update_result)

        self.VERSION_PATH_TABLE = 3
        self.VERSION_UPDATE_PROPERTIES = 4
        self.VERSION_UPDATE_FILE = 5

        self.UPDATE_FOLDER_NAME = os.path.join(settings.PROJECT_ROOT_PATH, "update_file")
        self._update_result_value = ""  # update or restore結果
        self._client_update_status_data = None  # 檢查更新的結果，初始化為None

        self.current_version = systemDefine.pppeVersion
        if 'm' in self.current_version:
            self.current_version = self.current_version.replace('m', '')
        if 'DEMO' in self.current_version:
            self.current_version = self.current_version.replace(' DEMO', '')

        self.installer_path = settings.PROJECT_ROOT_PATH
        self.active_checker()

    def check_update_from_cloud(self, show_dialog=True):
        print("check_update_from_cloud")
        model = UpdateStatusData("")
        model.show_dialog = show_dialog
        model.check_data = False

        # 檢查資料夾
        if not os.path.isdir(self.UPDATE_FOLDER_NAME):
            os.mkdir(self.UPDATE_FOLDER_NAME)

        # 從cloud拿取更新路徑表
        result = self.get_version_list_from_cloud()

        # 從讀取的json data拿到最新版本
        if result:
            data = self.get_updatable_versions(result)
            model.update_list = data
            model.check_data = True
            if len(data) > 0:
                model.last_version = data[-1]

            # 把檢查更新結果存起來
            self._client_update_status_data = model

        # 回傳資料給Client
        self.server.sendDataToClients(Command.TARGET_UPDATE_STATUS, model.to_json())

    def run_software_update(self, data):
        result = True

        try:
            json_str = json.dumps(data)
            model = UpdateStatusData(json_str)

            # 下載更新檔
            if result:
                result = self.download_update_file(model.update_list)

            # 解壓縮及檢查檔案
            if result:
                result = self.unzip_and_check_file(model.update_list)

            # 開始更新或更新失敗
            if result:
                if platform.system() == "Windows":
                    self.server.send_to_watch_dog(Command.TARGET_WATCH_DOG_SOFTWARE_UPDATE, self.current_version)
                elif platform.system() == "Darwin":
                    subprocess.Popen([os.path.join(self.installer_path, 'updatePPP'), self.current_version])
            else:
                self.genPPPInfoproperties(SOFTWARE_UPDATE_RESULT_FAILED, '')
                self.server.sendDataToClients(Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT, PPP_DOWNLOAD_FAILED)
        except Exception as e:
            Logger.LogIns().logger.error(traceback.print_exc())
            traceback.print_exc(file=sys.stdout)
            self.genPPPInfoproperties(SOFTWARE_UPDATE_RESULT_FAILED, str(e))
            self.server.sendDataToClients(Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT, PPP_DOWNLOAD_FAILED)

    def run_software_restore(self):
        Logger.LogIns().logger.info("SoftwareUpdateHandler run_software_update")
        # 避免一下子就進入還原動作，等到5秒後再執行
        sleep(5)
        if platform.system() == "Windows":
            self.server.send_to_watch_dog(Command.TARGET_WATCH_DOG_SOFTWARE_RESTORE, self.current_version)
        elif platform.system() == "Darwin":
            for file in os.listdir(self.installer_path):
                if 'backup_ppp' in file:
                    workingDir = os.path.join(self.installer_path, file)
                    subprocess.Popen([os.path.join(self.installer_path, file, 'restorePPP'), self.current_version], cwd=workingDir)
                    break

    def update_status(self):
        model = UpdateStatusData("")
        model.show_dialog = False
        model.check_data = False

        if self._client_update_status_data != None:
            model = self._client_update_status_data

        self.server.sendDataToClients(Command.TARGET_UPDATE_STATUS, model.to_json())

    def active_checker(self):
        # 開啟初始化時，先檢查更新一次
        self.check_update_from_cloud(False)

        # GMT/UTC +8 timezone
        time_zone = pytz.timezone('Asia/Taipei')
        utc_time = datetime.now(time_zone)
        day_time_sec = 24 * 60 * 60
        current_time_sec = utc_time.hour * 60 * 60 + utc_time.minute * 60 + utc_time.second
        timer_time_sec = day_time_sec - current_time_sec

        # 設定檢查更新的時間
        self.version_checker = QTimer()
        self.version_checker.timeout.connect(self.version_check)
        self.version_checker.start(timer_time_sec * 1000)

    def version_check(self):
        self.version_checker.stop()
        self.version_checker.start(24 * 60 * 60 * 1000)
        self.check_update_from_cloud(False)

    def set_update_result(self, value):
        if self._update_result_value == "":
            # 把結果存起來
            if value == Command.TARGET_WATCH_DOG_SOFTWARE_UPDATE_SUCCESS:
                self._update_result_value = PPP_UPDATE_SUCCESS
            elif value == Command.TARGET_WATCH_DOG_SOFTWARE_UPDATE_FAILED:
                self._update_result_value = PPP_UPDATE_FAILED
            elif value == Command.TARGET_WATCH_DOG_SOFTWARE_RESTORE_SUCCESS:
                self._update_result_value = PPP_RESTORE_SUCCESS
        if self._update_result_value == PPP_CLIENT_CHECKED:
            # 把結果直接傳給client
            if value == Command.TARGET_WATCH_DOG_SOFTWARE_UPDATE_SUCCESS:
                self.server.sendDataToClients(Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT, PPP_UPDATE_SUCCESS)
            elif value == Command.TARGET_WATCH_DOG_SOFTWARE_UPDATE_FAILED:
                self.server.sendDataToClients(Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT, PPP_UPDATE_FAILED)
            elif value == Command.TARGET_WATCH_DOG_SOFTWARE_RESTORE_SUCCESS:
                self.server.sendDataToClients(Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT, PPP_RESTORE_SUCCESS)

    def get_update_result(self):
        if platform.system() == 'Windows':
            if self._update_result_value == "" or self._update_result_value == PPP_CLIENT_CHECKED:
                self._update_result_value = PPP_CLIENT_CHECKED
            else:
                if self._update_result_value == PPP_UPDATE_SUCCESS:
                    self.server.sendDataToClients(Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT, PPP_UPDATE_SUCCESS)
                elif self._update_result_value == PPP_UPDATE_FAILED:
                    self.server.sendDataToClients(Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT, PPP_UPDATE_FAILED)
                elif self._update_result_value == PPP_RESTORE_SUCCESS:
                    self.server.sendDataToClients(Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT, PPP_RESTORE_SUCCESS)

                # Reset update Result
                self._update_result_value = ""

        elif platform.system() == 'Darwin':
            with DBSession.db_session(settings.PPPE_DB) as session:
                configuration = session.query(Configuration).first()
                if configuration.updateResult == 'updateSuccess':
                    configuration.updateResult = None
                    session.commit()
                    session.close()
                    self.server.sendDataToClients(Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT, PPP_UPDATE_SUCCESS)
                elif configuration.updateResult == 'updateFail':
                    configuration.updateResult = None
                    session.commit()
                    session.close()

                    for file in os.listdir(self.installer_path):
                        if 'backup_ppp' in file:
                            PPPE_DB = "sqlite:///" + os.path.join(self.installer_path, file, 'assets/PPPE_Db.db')
                            with DBSession.db_session(PPPE_DB) as session:
                                configuration = session.query(Configuration).first()
                                configuration.updateResult = None
                                session.commit()
                                session.close()
                    self.server.sendDataToClients(Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT, PPP_UPDATE_FAILED)
                elif configuration.updateResult == 'restoreSuccess':
                    configuration.updateResult = None
                    session.commit()
                    session.close()
                    self.server.sendDataToClients(Command.TARGET_SOFTWARE_UPDATE_DIALOG_RESULT, PPP_RESTORE_SUCCESS)

    def get_version_list_from_cloud(self):
        json_data = None
        new_json_data = {}
        count = 0

        while count < 2:
            try:
                url = systemDefine.SOFTWARE_UPDATE_URL
                request_data = self.get_request_json(self.VERSION_PATH_TABLE, "")
                with requests.post(url, json=request_data, timeout=REQUEST_TIMEOUT) as response:
                    if response.status_code == 200:
                        json_data = response.json()
                    else:
                        count += 1

                # 判斷是否為正機測試版本
                # true : 可取得所有更新檔
                # false : 無法取得有 Inactive 欄位的更新檔
                if buildConfig.ENABLE_DEVELOP_ACCOUNT == 'false':
                    new_json_data['Versions'] = []
                    for version in json_data["Versions"]:
                        if 'Inactive' not in version:
                            new_json_data['Versions'].append(version)
                elif buildConfig.ENABLE_DEVELOP_ACCOUNT == 'true':
                    new_json_data = json_data

                if new_json_data:
                    # 存更新路徑表
                    json_file_path = os.path.join(self.UPDATE_FOLDER_NAME, "PPP_VERSION_PATH_TABLE.json")
                    with open(json_file_path, mode="w", encoding="utf-8") as file:
                        json.dump(new_json_data, file, indent=4)
                    break
            except:
                break

        return new_json_data


    def download_update_file(self, version_list):
        # 檢查List不為None
        if version_list is None:
            return False

        for version in version_list:
            file_name = os.path.join(self.UPDATE_FOLDER_NAME, version + ".zip")
            count = 0

            while count < 2:
                try:
                    update_file_url = systemDefine.SOFTWARE_UPDATE_URL
                    json_propertise = self.get_request_json(self.VERSION_UPDATE_PROPERTIES, version)
                    json_update_file = self.get_request_json(self.VERSION_UPDATE_FILE, version)

                    # 取得更新檔的md5
                    with requests.post(update_file_url, json=json_propertise, timeout=REQUEST_TIMEOUT) as response:
                        response_text = response.text.replace(" ", "")
                        dl_check_sum = response_text[response_text.find("=") + 1:]

                    # 下載更新檔
                    with requests.post(update_file_url, json=json_update_file, timeout=REQUEST_TIMEOUT) as download_file:
                        open(file_name, 'wb').write(download_file.content)

                    # 檢查md5
                    cal_check_sum = self.calculation_file_md5(file_name)
                    if dl_check_sum.upper() != cal_check_sum.upper():
                        os.remove(file_name)
                        if count == 1:
                            return False
                    else:
                        # 下載及檢查成功
                        break
                except:
                    Logger.LogIns().logger.error(traceback.print_exc())
                    traceback.print_exc(file=sys.stdout)
                    return False
                count += 1

        return True

    def unzip_and_check_file(self, version_list):
        # 檢查List不為None
        if version_list is None:
            return False
        
        count = 0
        for version in version_list:
            while count < 2:
                try:
                    # 解壓縮
                    file = os.path.join(self.UPDATE_FOLDER_NAME, version + ".zip")
                    folder = os.path.join(self.UPDATE_FOLDER_NAME, version)

                    if platform.system() == "Windows":
                        update_folder_type = "PPP_UPDATE_TO_" + version + "_win"
                    elif platform.system() == "Darwin":
                        update_folder_type = "PPP_UPDATE_TO_" + version + "_mac"

                    json_file_path = os.path.join(folder, update_folder_type, "PPP_UPDATE_TO_" + version + ".json")
                    zip_file_path = os.path.join(folder, update_folder_type + ".zip")
                    zip_file_folder = os.path.join(folder, update_folder_type)

                    # 下載檔案解壓縮
                    with zipfile.ZipFile(file, mode="r") as zip_file:
                        zip_file.extractall(folder)

                    # 更新檔案解壓縮
                    with zipfile.ZipFile(zip_file_path, mode="r") as zip_file:
                        if platform.system() == "Windows":
                            zip_file.extractall(zip_file_folder)
                        elif platform.system() == "Darwin":
                            for file in zip_file.infolist():
                                path = os.path.join(zip_file_folder, file.filename)
                                zip_file.extract(file, zip_file_folder)
                                subprocess.call(['chmod', '755', path])

                    # 讀取更新檔案列表的json檔案
                    with open(json_file_path, mode="r", encoding="utf-8") as file:
                        json_data = json.load(file)

                    # 檢查檔案的MD5
                    check_result = True
                    file_list = json_data["Files"]
                    for file_info in file_list:
                        update_file_path = os.path.join(folder, update_folder_type, Path(file_info["Dest"]))
                        if os.path.isfile(update_file_path):
                            update_file_md5 = file_info["MD5"]
                            cal_md5 = self.calculation_file_md5(update_file_path)

                        if update_file_md5.upper() != cal_md5.upper():
                            check_result = False
                            break

                    # md5檢查結果
                    if check_result:
                        # Success
                        # 確認 updatePPP/restorePPP 是否有更新
                        if platform.system() == 'Windows':
                            if 'updatePPP.exe' in os.listdir(zip_file_folder):
                                os.remove(os.path.join(self.installer_path, 'updatePPP.exe'))
                                os.remove(os.path.join(self.installer_path, 'python36.zip'))
                                shutil.copy(os.path.join(zip_file_folder, 'updatePPP.exe'), self.installer_path)
                                shutil.copy(os.path.join(zip_file_folder, 'python36.zip'), self.installer_path)
                            if 'restorePPP.exe' in os.listdir(zip_file_folder):
                                os.remove(os.path.join(self.installer_path, 'restorePPP.exe'))
                                os.remove(os.path.join(self.installer_path, 'python36.zip'))
                                shutil.copy(os.path.join(zip_file_folder, 'restorePPP.exe'), self.installer_path)
                                shutil.copy(os.path.join(zip_file_folder, 'python36.zip'), self.installer_path)
                        elif platform.system() == 'Darwin':
                            if 'updatePPP' in os.listdir(zip_file_folder):
                                os.remove(os.path.join(self.installer_path, 'updatePPP'))
                                os.remove(os.path.join(self.installer_path, 'lib/library.zip'))
                                shutil.copy(os.path.join(zip_file_folder, 'updatePPP'), self.installer_path)
                                shutil.copy(os.path.join(zip_file_folder, 'library.zip'), os.path.join(self.installer_path, 'lib'))
                            if 'restorePPP' in os.listdir(zip_file_folder):
                                os.remove(os.path.join(self.installer_path, 'restorePPP'))
                                os.remove(os.path.join(self.installer_path, 'lib/library.zip'))
                                shutil.copy(os.path.join(zip_file_folder, 'restorePPP'), self.installer_path)
                                shutil.copy(os.path.join(zip_file_folder, 'library.zip'), os.path.join(self.installer_path, 'lib'))
                        break
                    else:
                        # Failed
                        if count == 1:
                            return False
                        count += 1
                except:
                    Logger.LogIns().logger.error(traceback.print_exc())
                    traceback.print_exc(file=sys.stdout)
                    return False
        return True

    def calculation_file_md5(self, file_name):
        # 檔案MD5
        with open(file_name, mode="rb") as cal_file:
            result = hashlib.md5(cal_file.read()).hexdigest()
        print(result)
        return result

    def get_updatable_versions(self, json_data):
        Logger.LogIns().logger.info("SoftwareUpdateHandler get_update_versions")

        update_list = []

        try:
            versions = json_data["Versions"]
            while True:
                found_version = ""
                for ver in versions:
                    if len(update_list) == 0:
                        search_version = self.current_version
                    else:
                        search_version = update_list[-1]

                    if ver["Version"] == search_version and ver["Next_Version"] != "":
                        found_version = ver["Next_Version"]
                        break

                # 找到的版本存起來或結束尋找
                if found_version != "":
                    update_list.append(found_version)
                else:
                    break
        except Exception as e:
            Logger.LogIns().logger.error(traceback.print_exc())
            traceback.print_exc(file=sys.stdout)

        return update_list

    def get_request_json(self, action, version):
        content = '{"otp":"","action":"' + str(action) + '","version":"' + str(version) + '"}'
        time_sec = int(time()) # Unix TimeStamp
        time_str = str(time_sec)

        hash_str = systemFunction.sha512Hash(time_str, content)
        hash_json = {
            "otp": hash_str,
            "action": str(action),
            "version": str(version)
        }
        return hash_json

    def genPPPInfoproperties(self, update_result, error_message):
        utc_time = datetime.now(timezone.utc).astimezone()
        now_time = utc_time.strftime('%Y-%m-%d %H:%M:%S')
        if 'log' not in os.listdir(self.installer_path):
            os.mkdir(os.path.join(self.installer_path, 'log'))

        update_from_version = self.current_version

        with open(os.path.join(self.UPDATE_FOLDER_NAME, "PPP_VERSION_PATH_TABLE.json")) as file:
            VersionPathTable = json.load(file)
        version_list = []
        for version in VersionPathTable['Versions']:
            version_list.append(version['Next_Version'])
        if len(version_list) > 1:
            update_to_version = version_list[len(version_list) - 1]
        else:
            update_to_version = version_list[0]

        with open(os.path.join(self.installer_path, PPP_INFO_PROPERTIES), 'w') as file:
            file.write('#' + now_time + '\n')
            file.write(BY_INSTALLER_UPDATE_OR_RESTORATION + '=' + SOFTWARE_UPDATE_TYPE_VALUE_UPDATE + '\n')
            if update_result == SOFTWARE_UPDATE_RESULT_FAILED:
                file.write(SOFTWARE_UPDATE_RESULT + '=' + update_result + SOFTWARE_UPDATE_DOWNLOAD_ERROR_MESSAGE + '\n')
            elif update_result == SOFTWARE_UPDATE_RESULT_SUCCESS:
                file.write(SOFTWARE_UPDATE_RESULT + '=' + update_result + '\n')
            file.write(SOFTWARE_UPDATE_FROM_PPP_VERSION + '=' + update_from_version + '\n')
            file.write(SOFTWARE_UPDATE_TO_PPP_VERSION + '=' + update_to_version + '\n')
            if not error_message == '':
                file.write('Exception = ' + error_message + '\n')
            file.close()