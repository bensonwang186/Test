import ftplib
import hashlib
import json
import os
import shutil
import subprocess
import zipfile
import platform
from io import BytesIO
from git import Repo
import RootDir

win_exclude_package_files = [
    '.install4j', '__pycache__', 'bin', 'ClientHandler', 'ClientModel', 'controllers', 'Events', 'handler_refactor',
    'help', 'i18n', 'major', 'migrations', 'model_Json', 'resources', 'System', 'Utility', 'views',
    'alembic.ini', 'CountryTable.xml', 'd1.crt', 'd1.key', 'Daemon.cpython-36.pyc',
    'installMonitorSrv.bat', 'installService.bat', 'PowerPanel Personal.exe', 'ppped.exe', 'pppServiceMonitor.exe',
    'removeMonitorSrv.bat', 'rootCA.crt', 'RootDir.py', 'set_srv.bat', 'startClient.bat', 'startMonitorSrv.bat',
    'startService.bat', 'stopMonitorSrv.bat', 'stopService.bat', 'uninstall.exe', 'unstallService.exe',
    'upgrades.exe', 'WinService.py', 'updatePPP.exe', 'restorePPP.exe',
    'python3.dll', 'python36.dll', 'VCRUNTIME140.dll', '_socket.pyd', '_lzma.pyd', 'select.pyd', '_bz2.pyd'
]

masOS_exclude_package_files = [
    'ClientHandler', 'ClientModel', 'controllers',
    'Events', 'handler_refactor', 'major',
    'model_Json', 'System', 'Utility', 'views', 'i18n'
]

macOS_lib_include_files = [
    'ClientHandler', 'ClientModel', 'controllers',
    'Events', 'handler_refactor', 'major',
    'model_Json', 'System', 'Utility', 'views'
]

win_executables_file = ['Client.py', 'Daemon.py', 'WinService.py', 'UninstallWinService.py', 'upgrades.py', 'updatePPP.py', 'restorePPP.py']
mac_executables_file = ['Client.py', 'Daemon.py', 'upgrades.py', 'updatePPP.py', 'restorePPP.py']

ftp_server = 'ftp.cyberpower.com.tw'
ftp_user = 'benson'
ftp_password = 'benson'

class genUpdateFile():
    def __init__(self, previous_commit, current_commit):
        self.PROJECT_ROOT_PATH = RootDir.PROJECT_ROOT_PATH
        self.update_file_folder = 'update_file'
        self.win_buildFile_path = os.path.join(self.PROJECT_ROOT_PATH, 'build/exe.win32-3.6')
        self.macOS_exe_buildFile_path = os.path.join(self.PROJECT_ROOT_PATH, 'build/PowerPanel Personal-0.1.app/Contents/MacOS')
        self.macOS_lib_buildFile_path = os.path.join(self.PROJECT_ROOT_PATH, 'build/lib.macosx-10.6-intel-3.6')
        self.repo = Repo(self.PROJECT_ROOT_PATH)

        self.previous_tag = None
        self.current_tag = None
        # previous commit
        if previous_commit == '':
            self.previous_tag = subprocess.check_output(['git', 'describe', '--tags', '--abbrev=0', 'HEAD~1']).strip().decode('ascii')
            for tag in self.repo.tags:
                if str(tag) == self.previous_tag:
                    self.previous_commit = tag.commit
                    break
        else:
            self.previous_commit = previous_commit

        if self.previous_tag == None:
            self.previous_version = str(self.previous_commit)[0:7]
        else:
            self.previous_version = str(self.previous_tag)

        # current commit
        if current_commit == '':
            self.current_commit = self.repo.head.object.hexsha
        else:
            self.current_commit = current_commit

        for tag in self.repo.tags:
            if str(tag.commit) == self.current_commit:
                self.current_tag = str(tag)
                break

        if self.current_tag == None:
            self.current_version = str(self.current_commit)[0:7]
        else:
            self.current_version = str(self.current_tag)

    def genUpdateFile(self):
        diff_file = self.repo.git.diff(self.previous_commit, self.current_commit, **{'name-status': True})
        diff = diff_file.split("\n")

        if self.update_file_folder in os.listdir(self.PROJECT_ROOT_PATH):
            shutil.rmtree(os.path.join(self.PROJECT_ROOT_PATH, self.update_file_folder))
        os.mkdir(os.path.join(self.PROJECT_ROOT_PATH, self.update_file_folder))

        if self.current_tag == None:
            diff_folder_name = "PPP_UPDATE_TO_" + self.current_version
        else:
            diff_folder_name = "PPP_UPDATE_TO_" + self.current_version.replace('Release_', '')

        diff_folder_dir = os.path.join(self.update_file_folder, diff_folder_name)
        os.mkdir(diff_folder_dir)

        self.copyBuildFile(diff_folder_dir, diff_folder_name, diff)

        # if requirements_win or requirements_mac change
        self.getPackageData(self.repo, diff_folder_dir)

        if diff_folder_name + ".zip" in os.listdir(self.update_file_folder):
            os.remove(os.path.join(self.update_file_folder, diff_folder_name + ".zip"))

        self.zip_dir(diff_folder_dir)

        shutil.rmtree(os.path.join(self.PROJECT_ROOT_PATH, diff_folder_dir))

        self.uploadUpdateFileToFtp(self.repo, diff_folder_name)

        print("Generate update_file success!!")

    def copyBuildFile(self, diff_folder_dir, diff_folder_name, diff):
        data = {'Version': diff_folder_name}
        data['Files'] = []
        if platform.system() == 'Windows':
            buildFile_path = self.win_buildFile_path
        elif platform.system() == 'Darwin':
            buildFile_path = self.macOS_exe_buildFile_path

        for s in diff:
            file_path = str(s).split("\t")

            # R : Rename(ex:R094   help/english/index.html	help/english/index.htm)
            if 'R' in file_path[0]:
                buildFile = self.getBuildFile(diff_folder_dir, buildFile_path, file_path[2])
                if buildFile is not '':
                    if '/' in file_path[2]:
                        index = str(file_path[2]).rindex('/')
                        if self.isMaclibFolderExist(file_path[2]):
                            target_folder = os.path.join(diff_folder_dir, 'lib', file_path[2][:index])
                        else:
                            target_folder = os.path.join(diff_folder_dir, file_path[2][:index])
                    else:
                        target_folder = diff_folder_dir

                    shutil.copy(buildFile, target_folder)
                    new_file_path = file_path[1] + ';' + file_path[2]
                    self.genJsonFile(buildFile, target_folder, new_file_path, data, 'Rename')

            # D : Delete(ex:D   test.py)
            elif 'D' in file_path[0]:
                if 'tests' not in file_path and 'Installer' not in file_path:
                    pass
                else:
                    self.genJsonFile('', '', file_path[1], data, 'Delete')

            # A : Add(ex:A	test.py)
            elif 'A' in file_path[0]:
                buildFile = self.getBuildFile(diff_folder_dir, buildFile_path, file_path[1])
                if buildFile is not '':
                    if '/' in file_path[1]:
                        index = str(file_path[1]).rindex('/')
                        if self.isMaclibFolderExist(file_path[1]):
                            target_folder = os.path.join(diff_folder_dir, 'lib', file_path[1][:index])
                        else:
                            target_folder = os.path.join(diff_folder_dir, file_path[1][:index])
                    else:
                        target_folder = diff_folder_dir

                    shutil.copy(buildFile, target_folder)
                    self.genJsonFile(buildFile, target_folder, file_path[1], data, 'Add')

            # M : Modify(ex:M	test.py)
            elif 'M' in file_path[0]:
                buildFile = self.getBuildFile(diff_folder_dir, buildFile_path, file_path[1])
                if buildFile is not '':
                    if '/' in file_path[1]:
                        index = str(file_path[1]).rindex('/')
                        if self.isMaclibFolderExist(file_path[1]):
                            target_folder = os.path.join(diff_folder_dir, 'lib', file_path[1][:index])
                        else:
                            target_folder = os.path.join(diff_folder_dir, file_path[1][:index])
                    else:
                        target_folder = diff_folder_dir

                    shutil.copy(buildFile, target_folder)
                    self.genJsonFile(buildFile, target_folder, file_path[1], data, 'Modify')

        # if executables change, update python library
        for s in diff:
            index = str(s).index('\t')+1
            file_name = str(s)[index:]
            if platform.system() == 'Windows':
                if file_name in win_executables_file:
                    shutil.copy(os.path.join(buildFile_path, 'python36.zip'), diff_folder_dir)
                    break
            elif platform.system() == 'Darwin':
                if file_name in mac_executables_file:
                    shutil.copy(os.path.join(buildFile_path, 'lib/library.zip'), diff_folder_dir)
                    break

        # get buildConfig.py
        if platform.system() == 'Windows':
            shutil.copy(os.path.join(buildFile_path, 'System/buildConfig.cp36-win32.pyd'), diff_folder_dir)
        elif platform.system() == 'Darwin':
            shutil.copy(os.path.join(self.macOS_lib_buildFile_path, 'System/buildConfig.cpython-36m-darwin.so'), diff_folder_dir)

        with open(os.path.join(diff_folder_dir, diff_folder_name + '.json'), 'w') as outfile:
            outfile.write(json.dumps(data, indent=4))

    def getBuildFile(self, diff_folder_dir, buildFile_path, file_path):
        # build folder don't exist 'tests', 'Installer' folder
        if 'tests' not in file_path and 'Installer' not in file_path:
            self.genBuildFileFolder(diff_folder_dir, file_path)

        if '/' in file_path:
            index = str(file_path).rindex('/')
            if self.isMaclibFolderExist(file_path):
                if str(file_path).split('/')[0] == 'views':
                    build_filefolder = os.path.join(buildFile_path, 'lib', str(file_path)[:index])
                else:
                    build_filefolder = os.path.join(self.macOS_lib_buildFile_path, str(file_path)[:index])
            else:
                build_filefolder = os.path.join(buildFile_path, str(file_path)[:index])
            filename = str(file_path)[index+1:]
        else:
            build_filefolder = buildFile_path
            filename = file_path

        buildFile = ''
        # build folder don't exist 'tests', 'Installer' folder
        if 'tests' not in file_path and 'Installer' not in file_path:
            if os.path.isdir(build_filefolder):
                for file in os.listdir(build_filefolder):
                    if '.py' in filename:
                        if filename == 'Client.py':
                            if platform.system() == 'Windows':
                                buildFile = os.path.join(build_filefolder, 'PowerPanel Personal.exe')
                            elif platform.system() == 'Darwin':
                                buildFile = os.path.join(build_filefolder, 'PowerPanel Personal')
                            break
                        elif filename == 'WinService.py':
                            if platform.system() == 'Windows':
                                buildFile = os.path.join(build_filefolder, 'ppped.exe')
                                break
                        elif filename == 'Daemon.py':
                            if platform.system() == 'Windows':
                                buildFile = os.path.join(build_filefolder, 'ppped.exe')
                            elif platform.system() == 'Darwin':
                                buildFile = os.path.join(build_filefolder, 'daemon')
                            break
                        elif filename == 'UninstallWinService.py':
                            if platform.system() == 'Windows':
                                buildFile = os.path.join(build_filefolder, 'unstallService.exe')
                                break
                        elif filename == 'upgrades.py':
                            if platform.system() == 'Windows':
                                buildFile = os.path.join(build_filefolder, 'upgrades.exe')
                            elif platform.system() == 'Darwin':
                                buildFile = os.path.join(build_filefolder, 'upgrades')
                            break
                        elif filename == 'updatePPP.py':
                            if platform.system() == 'Windows':
                                buildFile = os.path.join(build_filefolder, 'updatePPP.exe')
                            elif platform.system() == 'Darwin':
                                buildFile = os.path.join(build_filefolder, 'updatePPP')
                            break
                        elif filename == 'restorePPP.py':
                            if platform.system() == 'Windows':
                                buildFile = os.path.join(build_filefolder, 'restorePPP.exe')
                            elif platform.system() == 'Darwin':
                                buildFile = os.path.join(build_filefolder, 'restorePPP')
                            break
                        elif 'migrations' in build_filefolder:
                            buildFile = os.path.join(build_filefolder, filename)
                            break
                        elif 'i18n' in build_filefolder:
                            if '.py' in file:
                                if filename.split('.py')[0] in file:
                                    buildFile = os.path.join(build_filefolder, file)
                                    break
                        else:
                            if platform.system() == 'Windows':
                                if ('.pyc' in file) or ('.pyd' in file):
                                    if filename.split('.py')[0] in file:
                                        buildFile = os.path.join(build_filefolder, file)
                                        break
                            elif platform.system() == 'Darwin':
                                if '.so' in file:
                                    if filename.split('.py')[0] in file:
                                        buildFile = os.path.join(build_filefolder, file)
                                        break
                                elif ('.pyc' in file) or ('.pyd' in file):
                                    if filename.split('.py')[0] in file:
                                        buildFile = os.path.join(build_filefolder, file)
                                        break

                    elif filename == 'messages.po':
                        buildFile = os.path.join(build_filefolder, 'messages.mo')
                        break
                    elif filename == 'qt_resources.qrc':
                        if platform.system() == 'Darwin':
                            buildFile = os.path.join(build_filefolder, filename.replace('.qrc', '.py'))
                            break
                    elif filename == file:
                        if filename == 'pppServiceMonitor.exe':
                            continue
                        else:
                            buildFile = os.path.join(build_filefolder, filename)
                        break
        return buildFile


    def genFileMD5(self, target_folder, Dest):
        if '/' in Dest:
            index = str(Dest).rindex('/')
            file_path = os.path.join(target_folder, Dest[index+1:])
        else:
            file_path = os.path.join(target_folder, Dest)

        m = hashlib.md5()
        with open(file_path, "rb") as f:
            buf = f.read()
            m.update(buf)
            f.close()
        return m.hexdigest()

    def isMaclibFolderExist(self, file_path):
        libExist = False
        if platform.system() == 'Darwin':
            if str(file_path).split('/')[0] in macOS_lib_include_files:
                libExist = True

        return libExist

    def genJsonFile(self, buildFile, target_folder, file_path, data, action):
        Dest = ''
        if action is not 'Delete':
            if platform.system() == 'Windows':
                Dest = buildFile[len(self.win_buildFile_path) + 1:].replace('\\', '/')
            elif platform.system() == 'Darwin':
                if self.isMaclibFolderExist(file_path):
                    if file_path.split('/')[0] == 'views':
                        Dest = os.path.join(buildFile[len(self.macOS_exe_buildFile_path) + 1:])
                    else:
                        Dest = os.path.join('lib', buildFile[len(self.macOS_lib_buildFile_path) + 1:])
                else:
                    Dest = buildFile[len(self.macOS_exe_buildFile_path) + 1:]

        if action is 'Add':
            MD5 = self.genFileMD5(target_folder, Dest)
            data['Files'].append({
                'Src': file_path,
                'Dest': Dest,
                'Action': action,
                'MD5': MD5
            })
        elif action is 'Modify':
            MD5 = self.genFileMD5(target_folder, Dest)
            data['Files'].append({
                'Src': file_path,
                'Dest': Dest,
                'Action': action,
                'MD5': MD5
            })
        elif action is 'Delete':
            data['Files'].append({
                'Src': file_path,
                'Dest': '',
                'Action': action,
                'MD5': ''
            })
        elif action is 'Rename':
            MD5 = self.genFileMD5(target_folder, Dest)
            data['Files'].append({
                'Src': str(file_path).split(';')[0],
                'Dest': Dest,
                'Action': action,
                'MD5': MD5
            })

    def zip_dir(self, diff_folder_dir):
        if platform.system() == 'Windows':
            zf = zipfile.ZipFile(diff_folder_dir + "_win.zip", "w")
        elif platform.system() == 'Darwin':
            zf = zipfile.ZipFile(diff_folder_dir + "_mac.zip", "w")

        for original_dir, subdirs, files in os.walk(diff_folder_dir):
            if original_dir is diff_folder_dir:
                for subdir in subdirs:
                    zf.write(os.path.join(original_dir, subdir), subdir)
                for file in files:
                    zf.write(os.path.join(original_dir, file), file)
            else:
                if platform.system() == 'Windows':
                    new_dir = str(original_dir).replace(diff_folder_dir + '\\', '')
                elif platform.system() == 'Darwin':
                    new_dir = str(original_dir).replace(diff_folder_dir + '/', '')

                for subdir in subdirs:
                    zf.write(os.path.join(original_dir, subdir), os.path.join(new_dir, subdir))
                for file in files:
                    zf.write(os.path.join(original_dir, file), os.path.join(new_dir, file))
        zf.close()

    def genBuildFileFolder(self, diff_folder_dir, file_path):
        if '/' in file_path:
            split_file_path = str(file_path).split('/')
            folder_s = ''
            for i in range(0, len(split_file_path)-1):
                if i == 0:
                    if self.isMaclibFolderExist(file_path):
                        if not os.path.isdir(os.path.join(diff_folder_dir, 'lib')):
                            os.mkdir(os.path.join(diff_folder_dir, 'lib'))
                        folder_s = os.path.join('lib', split_file_path[i])
                    else:
                        folder_s = split_file_path[i]
                    if not os.path.isdir(os.path.join(diff_folder_dir, folder_s)):
                        os.mkdir(os.path.join(diff_folder_dir, folder_s))
                else:
                    folder_s += '/' + split_file_path[i]
                    if not os.path.isdir(os.path.join(diff_folder_dir, folder_s)):
                        os.mkdir(os.path.join(diff_folder_dir, folder_s))


    def getPackageData(self, repo, diff_folder_dir):
        if platform.system() == 'Windows':
            file = "requirements_win.txt"
        elif platform.system() == 'Darwin':
            file = "requirements_mac.txt"

        # get previous_version
        for commit in repo.iter_commits():
            if str(commit) == str(self.previous_commit):
                previous_content = (commit.tree / file).data_stream.read().strip().decode('ascii')
                break

        for commit in repo.iter_commits():
            if str(commit) == str(self.current_commit):
                current_content = (commit.tree / file).data_stream.read().strip().decode('ascii')
                break

        if current_content == previous_content:
            isPackageChange = False
        else:
            isPackageChange = True

        if isPackageChange:
            pre_package = []
            for content in str(previous_content).split('\n'):
                if '==' in content:
                    s_content = content.split('==')
                    pre_package.append(s_content[0])
                elif '>=' in content:
                    s_content = content.split('>=')
                    pre_package.append(s_content[0])
                else:
                    pre_package.append(content)

            cur_package = []
            for content in str(current_content).split('\n'):
                if '==' in content:
                    s_content = content.split('==')
                    cur_package.append(s_content[0])
                elif '>=' in content:
                    s_content = content.split('>=')
                    cur_package.append(s_content[0])
                else:
                    cur_package.append(content)

            if pre_package == cur_package:
                PackageStatus = 'Update'
            else:
                PackageStatus = 'Add'

            packages_folder = os.path.join(diff_folder_dir, 'packages')
            if packages_folder not in os.listdir(diff_folder_dir):
                os.mkdir(packages_folder)

            if PackageStatus == 'Update':
                if platform.system() == 'Windows':
                    win_buildFile_path = self.win_buildFile_path
                    packages = set(os.listdir(win_buildFile_path)) - set(win_exclude_package_files)

                    for package in packages:
                        src = os.path.join(win_buildFile_path, package)
                        dest = os.path.join(packages_folder, package)
                        if os.path.isdir(src):
                            shutil.copytree(src, dest)
                        else:
                            shutil.copy(src, dest)

                elif platform.system() == 'Darwin':
                    macOS_buildFile_path = self.macOS_exe_buildFile_path
                    macOS_lib_buildFile_path = os.path.join(macOS_buildFile_path, 'lib')

                    macOS_lib_packages = set(os.listdir(macOS_lib_buildFile_path)) - set(masOS_exclude_package_files)
                    for package in macOS_lib_packages:
                        src = os.path.join(macOS_lib_buildFile_path, package)
                        dest = os.path.join(packages_folder, package)
                        if os.path.isdir(src):
                            shutil.copytree(src, dest)
                        else:
                            shutil.copy(src, dest)

            elif PackageStatus == 'Add':
                ftp_relesse_include_file_folder = '/build/PPP/update_file/RELEASE_INCLUDE_FILE'
                myFTP = ftplib.FTP(ftp_server, ftp_user, ftp_password)
                if platform.system() == 'Windows':
                    include_FileList = self.previous_version + '_IncludeFile_win.txt'
                elif platform.system() == 'Darwin':
                    include_FileList = self.previous_version + '_IncludeFile_mac.txt'

                ftp_file = os.path.join(ftp_relesse_include_file_folder, self.previous_version, include_FileList)
                r = BytesIO()
                myFTP.retrbinary('RETR ' + ftp_file, r.write)

                last_release_include_files = []
                file_list = r.getvalue().strip().decode('ascii')
                if platform.system() == 'Windows':
                    s_file_list = file_list.split('\r\n')
                elif platform.system() == 'Darwin':
                    s_file_list = file_list.split('\n')

                for file in s_file_list:
                    last_release_include_files.append(file)

                if platform.system() == 'Windows':
                    win_buildFile_path = self.win_buildFile_path

                    packages = set(os.listdir(win_buildFile_path)) - set(last_release_include_files)
                    for package in packages:
                        src = os.path.join(win_buildFile_path, package)
                        dest = os.path.join(packages_folder, package)
                        if os.path.isdir(src):
                            shutil.copytree(src, dest)
                        else:
                            shutil.copy(src, dest)

                elif platform.system() == 'Darwin':
                    macOS_buildFile_path = self.macOS_exe_buildFile_path
                    macOS_lib_buildFile_path = os.path.join(macOS_buildFile_path, 'lib')

                    macOS_lib_packages = set(os.listdir(macOS_lib_buildFile_path)) - set(last_release_include_files)
                    for package in macOS_lib_packages:
                        src = os.path.join(macOS_lib_buildFile_path, package)
                        dest = os.path.join(packages_folder, package)
                        if os.path.isdir(src):
                            shutil.copytree(src, dest)
                        else:
                            shutil.copy(src, dest)

    def uploadFileFTP(self, myFTP, update_file_folder, update_file_path, ftp_dest):
        myFTP.cwd(ftp_dest)
        if update_file_path in myFTP.nlst():
            myFTP.delete(update_file_path)

        fileObject = open(os.path.join(update_file_folder, update_file_path), "rb")
        ftpCommand = "STOR %s" % update_file_path

        # Transfer the file in binary mode
        ftpResponseMessage = myFTP.storbinary(ftpCommand, fp=fileObject)
        print(ftpResponseMessage)

    def uploadUpdateFileToFtp(self, repo, diff_folder_name):
        win_diff_folder_zipName = diff_folder_name + '_win.zip'
        mac_diff_folder_zipName = diff_folder_name + '_mac.zip'

        update_file_folder = os.path.join(self.PROJECT_ROOT_PATH, self.update_file_folder)
        ftp_update_file_folder = '/build/PPP/update_file'
        ftp_release_include_file_folder = '/build/PPP/update_file/RELEASE_INCLUDE_FILE'
        ftp_diff_folder = os.path.join(ftp_update_file_folder, diff_folder_name)

        myFTP = ftplib.FTP(ftp_server, ftp_user, ftp_password)
        myFTP.cwd('/build/PPP')
        if 'update_file' not in myFTP.nlst():
            myFTP.mkd(ftp_update_file_folder)

        myFTP.cwd(ftp_update_file_folder)
        if diff_folder_name not in myFTP.nlst():
            myFTP.mkd(ftp_diff_folder)

        if platform.system() == 'Windows':
            self.uploadFileFTP(myFTP, update_file_folder, win_diff_folder_zipName, ftp_diff_folder)
        elif platform.system() == 'Darwin':
            self.uploadFileFTP(myFTP, update_file_folder, mac_diff_folder_zipName, ftp_diff_folder)

        myFTP.cwd(ftp_update_file_folder)
        if 'RELEASE_INCLUDE_FILE' not in myFTP.nlst():
            myFTP.mkd(ftp_release_include_file_folder)
        myFTP.cwd(ftp_release_include_file_folder)
        self.genReleaseIncludeFile(myFTP, update_file_folder, ftp_release_include_file_folder)

        myFTP.cwd(ftp_diff_folder)
        if win_diff_folder_zipName in myFTP.nlst() and mac_diff_folder_zipName in myFTP.nlst():
            if platform.system() == 'Windows':
                ftp_file = mac_diff_folder_zipName
                download_path = os.path.join(update_file_folder, mac_diff_folder_zipName)
                with open(download_path, 'wb') as file:
                    myFTP.retrbinary('RETR %s' % ftp_file, file.write)

            elif platform.system() == 'Darwin':
                ftp_file = win_diff_folder_zipName
                download_path = os.path.join(update_file_folder, win_diff_folder_zipName)
                with open(download_path, 'wb') as file:
                    myFTP.retrbinary('RETR %s' % ftp_file, file.write)

            zf = zipfile.ZipFile(os.path.join(update_file_folder, diff_folder_name + ".zip"), "w")
            zf.write(os.path.join(update_file_folder, win_diff_folder_zipName), win_diff_folder_zipName)
            zf.write(os.path.join(update_file_folder, mac_diff_folder_zipName), mac_diff_folder_zipName)
            zf.close()

            if platform.system() == 'Windows':
                os.remove(os.path.join(update_file_folder, mac_diff_folder_zipName))
            elif platform.system() == 'Darwin':
                os.remove(os.path.join(update_file_folder, win_diff_folder_zipName))

            myFTP.cwd(ftp_diff_folder)
            for file in myFTP.nlst():
                myFTP.delete(file)
            myFTP.rmd(ftp_diff_folder)

            m = hashlib.md5()
            with open(os.path.join(update_file_folder, diff_folder_name + '.zip'), 'rb') as f:
                buf = f.read()
                m.update(buf)
                f.close()
            with open(os.path.join(update_file_folder, diff_folder_name + '.properties'), 'w') as f:
                f.write('checksum = ' + m.hexdigest())

            myFTP.cwd(ftp_update_file_folder)
            PPP_VERSION_PATH_TABLE = 'PPP_VERSION_PATH_TABLE.json'
            if PPP_VERSION_PATH_TABLE not in myFTP.nlst():
                data = {}
                data['Versions'] = []
                data['Versions'].append({
                    'Version': '2.3.0',
                    'Next_Version': diff_folder_name.replace('PPP_UPDATE_TO_', '')
                })
                with open(os.path.join(update_file_folder, PPP_VERSION_PATH_TABLE), 'w') as outfile:
                    outfile.write(json.dumps(data, indent=4))
            else:
                download_path = os.path.join(update_file_folder, PPP_VERSION_PATH_TABLE)
                with open(download_path, 'wb') as file:
                    myFTP.retrbinary('RETR %s' % PPP_VERSION_PATH_TABLE, file.write)

                with open(download_path) as f:
                    json_data = json.load(f)

                for data in json_data['Versions']:
                    previous_version = data['Next_Version']

                json_data['Versions'].append({
                    'Version': previous_version,
                    'Next_Version': diff_folder_name.replace('PPP_UPDATE_TO_', '')
                })

                myFTP.delete(os.path.join(ftp_update_file_folder, PPP_VERSION_PATH_TABLE))
                with open(os.path.join(update_file_folder, PPP_VERSION_PATH_TABLE), 'w') as outfile:
                    outfile.write(json.dumps(json_data, indent=4))

            # upload diff_folder_name.zip to ftp (Ex: PPP_UPDATE_TO_2.2.5.zip)
            self.uploadFileFTP(myFTP, update_file_folder, diff_folder_name + '.zip', ftp_update_file_folder)
            # upload diff_folder_name properties to ftp (Ex: PPP_UPDATE_TO_2.2.5.properties)
            self.uploadFileFTP(myFTP, update_file_folder, diff_folder_name + '.properties', ftp_update_file_folder)
            # upload PPP_VERSION_PATH_TABLE to ftp (Ex: PPP_VERSION_PATH_TABLE.json)
            self.uploadFileFTP(myFTP, update_file_folder, PPP_VERSION_PATH_TABLE, ftp_update_file_folder)

    def genReleaseIncludeFile(self, myFTP, update_file_folder, ftp_release_include_file_folder):
        if platform.system() == 'Windows':
            include_file = self.current_version + '_IncludeFile_win.txt'
            buildFile_path = self.win_buildFile_path
        elif platform.system() == 'Darwin':
            include_file = self.current_version + '_IncludeFile_mac.txt'
            buildFile_path = os.path.join(self.macOS_exe_buildFile_path, 'lib')

        with open(os.path.join(update_file_folder, include_file), 'w') as f:
            for file in os.listdir(buildFile_path):
                f.write(file + '\n')
            f.close()

        myFTP.cwd(ftp_release_include_file_folder)
        release_version_folder = os.path.join(ftp_release_include_file_folder, self.current_version)
        if self.current_version not in myFTP.nlst():
            myFTP.mkd(release_version_folder)

        self.uploadFileFTP(myFTP, update_file_folder, include_file, release_version_folder)

if __name__ == '__main__':

    previous_commit = ''
    current_commit = ''

    # print("Generate Update File")
    # print("Please enter current commit(ex: 3ed72998762658bd0ea59e4c49ce4909a752793a)")
    # current_commit = input()
    # print("Please enter previous commit(ex: 248a67b2e9d9ac4449fb1373e2cb138413d1b352)")
    # previous_commit = input()

    f = genUpdateFile(previous_commit, current_commit)
    f.genUpdateFile()
