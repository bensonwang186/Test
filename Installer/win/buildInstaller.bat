
REM remove build files
rd /s /q ..\..\build
rd /s /q ..\exe.win32-3.6
del ..\ppp_windows_2_1_6.exe

REM build cx_freeze
cd ..\..
py setup.py build
del .\build\exe.win32-3.6\Qt5Bluetooth.dll
del .\build\exe.win32-3.6\Qt5DBus.dll
del .\build\exe.win32-3.6\Qt5Designer.dll
del .\build\exe.win32-3.6\Qt5Help.dll
del .\build\exe.win32-3.6\Qt5Location.dll
del .\build\exe.win32-3.6\Qt5Multimedia.dll
del .\build\exe.win32-3.6\Qt5MultimediaWidgets.dll
del .\build\exe.win32-3.6\Qt5Nfc.dll
del .\build\exe.win32-3.6\Qt5OpenGL.dll
del .\build\exe.win32-3.6\Qt5Positioning.dll
del .\build\exe.win32-3.6\Qt5PrintSupport.dll
del .\build\exe.win32-3.6\Qt5Qml.dll
del .\build\exe.win32-3.6\Qt5Quick.dll
del .\build\exe.win32-3.6\Qt5QuickWidgets.dll
del .\build\exe.win32-3.6\Qt5Sensors.dll
del .\build\exe.win32-3.6\Qt5SerialPort.dll
del .\build\exe.win32-3.6\Qt5Sql.dll
del .\build\exe.win32-3.6\Qt5Svg.dll
del .\build\exe.win32-3.6\Qt5Test.dll
del .\build\exe.win32-3.6\Qt5WebChannel.dll
del .\build\exe.win32-3.6\Qt5WebEngine.dll
del .\build\exe.win32-3.6\Qt5WebEngineCore.dll
del .\build\exe.win32-3.6\Qt5WebEngineWidgets.dll
del .\build\exe.win32-3.6\Qt5WebSockets.dll
del .\build\exe.win32-3.6\Qt5WinExtras.dll
del .\build\exe.win32-3.6\Qt5Xml.dll
del .\build\exe.win32-3.6\Qt5XmlPatterns.dll
del .\build\exe.win32-3.6\imageformats\*.pdb
del .\build\exe.win32-3.6\platforms\*.pdb
del .\build\exe.win32-3.6\PyQt5\_QOpenGLFunctions_2_0.pyd
del .\build\exe.win32-3.6\PyQt5\_QOpenGLFunctions_2_1.pyd
del .\build\exe.win32-3.6\PyQt5\_QOpenGLFunctions_4_1_Core.pyd
del .\build\exe.win32-3.6\PyQt5\_QOpenGLFunctions_4_1_Core.pyd
del .\build\exe.win32-3.6\PyQt5\QAxContainer.pyd
del .\build\exe.win32-3.6\PyQt5\QtBluetooth.pyd
del .\build\exe.win32-3.6\PyQt5\QtDBus.pyd
del .\build\exe.win32-3.6\PyQt5\QtDesigner.pyd
del .\build\exe.win32-3.6\PyQt5\QtHelp.pyd
del .\build\exe.win32-3.6\PyQt5\QtLocation.pyd
del .\build\exe.win32-3.6\PyQt5\QtMultimedia.pyd
del .\build\exe.win32-3.6\PyQt5\QtMultimediaWidgets.pyd
del .\build\exe.win32-3.6\PyQt5\QtNfc.pyd
del .\build\exe.win32-3.6\PyQt5\QtOpenGL.pyd
del .\build\exe.win32-3.6\PyQt5\QtPositioning.pyd
del .\build\exe.win32-3.6\PyQt5\QtPrintSupport.pyd
del .\build\exe.win32-3.6\PyQt5\QtQml.pyd
del .\build\exe.win32-3.6\PyQt5\QtQuick.pyd
del .\build\exe.win32-3.6\PyQt5\QtQuickWidgets.pyd
del .\build\exe.win32-3.6\PyQt5\QtSensors.pyd
del .\build\exe.win32-3.6\PyQt5\QtSerialPort.pyd
del .\build\exe.win32-3.6\PyQt5\QtSql.pyd
del .\build\exe.win32-3.6\PyQt5\QtSvg.pyd
del .\build\exe.win32-3.6\PyQt5\QtTest.pyd
del .\build\exe.win32-3.6\PyQt5\QtWebChannel.pyd
del .\build\exe.win32-3.6\PyQt5\QtWebEngine.pyd
del .\build\exe.win32-3.6\PyQt5\QtWebEngineCore.pyd
del .\build\exe.win32-3.6\PyQt5\QtWebEngineWidgets.pyd
del .\build\exe.win32-3.6\PyQt5\QtWebSockets.pyd
del .\build\exe.win32-3.6\PyQt5\QtWinExtras.pyd
del .\build\exe.win32-3.6\PyQt5\QtXml.pyd
del .\build\exe.win32-3.6\PyQt5\QtXmlPatterns.pyd
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Bluetooth.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5DBus.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Designer.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Help.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Location.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Multimedia.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5MultimediaWidgets.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Nfc.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5OpenGL.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Positioning.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5PrintSupport.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Qml.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Quick.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5QuickWidgets.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Sensors.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5SerialPort.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Sql.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Svg.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Test.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5WebChannel.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5WebEngine.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5WebEngineCore.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5WebEngineWidgets.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5WebSockets.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5WinExtras.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5Xml.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5XmlPatterns.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5MultimediaQuick_p.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5QuickControls2.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5QuickParticles.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5QuickTemplates2.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\Qt5QuickTest.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\QtWebEngineProcess.exe
del .\build\exe.win32-3.6\PyQt5\Qt\bin\libGLESv2.dll
del .\build\exe.win32-3.6\PyQt5\Qt\bin\libEGL.dll
rmdir /s /q .\build\exe.win32-3.6\PyQt5\Qt\qml
rmdir /s /q .\build\exe.win32-3.6\PyQt5\Qt\plugins
rmdir /s /q .\build\exe.win32-3.6\PyQt5\Qt\resources
rmdir /s /q .\build\exe.win32-3.6\PyQt5\Qt\translations
del .\build\exe.win32-3.6\major\*.pyc
del .\build\exe.win32-3.6\Events\*.pyc
del .\build\exe.win32-3.6\Utility\*.pyc
del .\build\exe.win32-3.6\handler_refactor\*.pyc
del .\build\exe.win32-3.6\ClientHandler\*.pyc
del .\build\exe.win32-3.6\ClientModel\*.pyc
del .\build\exe.win32-3.6\model_Json\*.pyc
del .\build\exe.win32-3.6\controllers\*.pyc
del .\build\exe.win32-3.6\System\*.pyc
del .\build\exe.win32-3.6\Daemon.py
del .\build\exe.win32-3.6\major\*.c
del .\build\exe.win32-3.6\Events\*.c
del .\build\exe.win32-3.6\Utility\*.c
del .\build\exe.win32-3.6\handler_refactor\*.c
del .\build\exe.win32-3.6\ClientHandler\*.c
del .\build\exe.win32-3.6\ClientModel\*.c
del .\build\exe.win32-3.6\model_Json\*.c
del .\build\exe.win32-3.6\controllers\*.c
del .\build\exe.win32-3.6\System\*.c
del .\build\exe.win32-3.6\Daemon.c

REM cython compile
py pyd-setup_win.py build
copy .\build\lib.win32-3.6\%1\major\*.pyd .\build\exe.win32-3.6\major\
copy .\build\lib.win32-3.6\%1\Events\*.pyd .\build\exe.win32-3.6\Events\
copy .\build\lib.win32-3.6\%1\Utility\*.pyd .\build\exe.win32-3.6\Utility\
copy .\build\lib.win32-3.6\%1\handler_refactor\*.pyd .\build\exe.win32-3.6\handler_refactor\
copy .\build\lib.win32-3.6\%1\ClientHandler\*.pyd .\build\exe.win32-3.6\ClientHandler\
copy .\build\lib.win32-3.6\%1\model_Json\*.pyd .\build\exe.win32-3.6\model_Json\
copy .\build\lib.win32-3.6\%1\ClientModel\*.pyd .\build\exe.win32-3.6\ClientModel\
copy .\build\lib.win32-3.6\%1\controllers\*.pyd .\build\exe.win32-3.6\controllers\
copy .\build\lib.win32-3.6\%1\System\*.pyd .\build\exe.win32-3.6\System\

py -m py_compile Daemon.py
copy .\__pycache__\Daemon.cpython-36.pyc .\build\exe.win32-3.6\
REM copy .\build\lib.win32-3.6\%1\Daemon.cp36-win32.pyd .\build\exe.win32-3.6\


REM delete po file
del .\build\exe.win32-3.6\i18n\cs_CZ\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\de_DE\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\en_US\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\es_ES\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\fr_CA\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\fr_FR\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\hu_HU\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\it_IT\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\ja_JP\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\pl\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\ru\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\sl\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\zh_CN\LC_MESSAGES\messages.po
del .\build\exe.win32-3.6\i18n\zh_TW\LC_MESSAGES\messages.po

mkdir .\build\exe.win32-3.6\__pycache__
xcopy .\build\exe.win32-3.6 .\Installer\exe.win32-3.6 /e /i /h

REM generate installer
cd Installer
"C:\Program Files\install4j7\bin\install4jc.exe" pppe.install4j -m windows