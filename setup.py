# -*- coding: utf-8 -*-

# A simple setup script for creating a Windows service. See the comments in the
# Config.py and ServiceHandler.py files for more information on how to set this
# up.
#
# Installing the service is done with the option --install <Name> and
# uninstalling the service is done with the option --uninstall <Name>. The
# value for <Name> is intended to differentiate between different invocations
# of the same service code -- for example for accessing different databases or
# using different configuration files.

import os
import platform

from cx_Freeze import Executable
from cx_Freeze import setup as cx_setup

from System import settings


if os.name == 'nt':
    appIconImage = os.path.join(settings.IMAGE_PATH, "pppe.ico")

    options = {
        'build_exe': {
            "packages": [
                'alembic', 'logging', 'ctypes',
                'sqlalchemy', 'IPy', 'smtplib',
                'httplib2', 'oauth2client',
                'email.mime.multipart',
                'email.mime.text', 'apiclient',
                'encodings', 'PyQt5', 'asyncio',
                'sqlite3', 'json', 'hashlib',
                'win32service', 'win32serviceutil',
                'win32event', 'win32timezone', 'site', 'cryptography', 'cffi', 'idna', 'winsound',
                'paho', 'pyfcm', 'requests', 'wmi', "bitstring", "configparser", 'babel'],
            'includes': [
                'cx_Logging'],
            'include_files': [
                os.path.join('C:\Program Files (x86)\Python36-32', 'DLLs', 'sqlite3.dll'),
                'alembic.ini', 'migrations',
                'resources', 'i18n', 'bin', 'CountryTable.xml', 'WinService.py', "startService.bat",
                "stopService.bat", "startClient.bat", "help", "RootDir.py", "Daemon.py", "set_srv.bat",
                "startMonitorSrv.bat","stopMonitorSrv.bat","installMonitorSrv.bat","removeMonitorSrv.bat","pppServiceMonitor.exe",
                "d1.crt","d1.key", "rootCA.crt"
            ],
            'include_msvcr': True
        }
    }
#elif os.name == 'posix':
elif platform.system() == 'Darwin':
    appIconImage = os.path.join(settings.IMAGE_PATH, "pppe.icns")

    options = {
        'build_exe': {
            'packages': [
                'alembic', 'logging', 'ctypes',
                'sqlalchemy', 'IPy', 'smtplib',
                'httplib2', 'oauth2client',
                'email.mime.multipart',
                'email.mime.text', 'apiclient',
                'encodings', 'PyQt5', 'asyncio',
                'sqlite3', 'json', 'hashlib', 'site', 'cryptography', 'cffi', 'idna',
                'soundfile', 'sounddevice', 'numpy', 'paho', 'pyfcm', 'requests', 'bitstring', "configparser", "objc", 'babel'
            ],
            'include_files': [
                'alembic.ini', 'migrations',
                'resources', 'i18n', 'bin', 'CountryTable.xml',
                'help', 'RootDir.py',
                'Installer/mac/installService',
                'venv/lib/python3.6/site-packages/_soundfile_data/',
                "d1.crt","d1.key", "rootCA.crt"
                #os.path.join(PYTHON_INSTALL_DIR, 'libssl.1.0.0.dylib'),

            ]
        },
        'bdist_mac': {
            'iconfile': appIconImage
        }
    }


if os.name == 'nt':
    executables = [
        Executable('WinService.py', targetName='ppped.exe'),
        Executable('UninstallWinService.py', targetName='unstallService.exe'),
        Executable('Client.py', targetName='PowerPanel Personal.exe', icon=appIconImage, base="Win32GUI"),
        # Executable('Client.py', targetName='pppe_client.exe'),
        Executable('upgrades.py', targetName='upgrades.exe'),
        Executable('updatePPP.py', targetName='updatePPP.exe'),
        Executable('restorePPP.py', targetName='restorePPP.exe')
    ]
#elif os.name == 'posix':
elif platform.system() == 'Darwin':
    executables = [
        # MacOS app would execute first executable while double click execution
        Executable('Client.py', targetName='PowerPanel Personal'),
        Executable('Daemon.py', targetName='daemon'),
        Executable('upgrades.py', targetName='upgrades'),
        Executable('updatePPP.py', targetName='updatePPP'),
        Executable('restorePPP.py', targetName='restorePPP')
    ]

cx_setup(name='PowerPanel Personal',
    version='0.1',
    description='',
    executables=executables,
    options=options
)
