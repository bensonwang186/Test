@echo off
IF "%2"=="true" (
    SET enable_develop_account='true'
)

IF "%2"=="false" (
    SET enable_develop_account='false'
)

IF "%1"=="demo" (
    call:assignCPS_demo
    goto exit
)

IF "%1"=="formal" (
    call:assignCPS_formal
    goto exit
)

:assignCPS_formal
 SET emq_host='iot.cyberpower.com'
 SET emq_port=8883
 SET website_server_host='iotapi.cyberpower.com'
 SET build_for=0
 SET mode=1
 goto genFile

:assignCPS_demo
 SET emq_host='iottest.cyberpower.com'
 SET emq_port=8883
 SET website_server_host='iotapitest.cyberpower.com'
 SET build_for=1
 SET mode=0
 goto genFile

:genFile
 FOR /F %%I IN ('git.exe rev-parse --short HEAD') DO SET build_version='%%I'
 
 echo EMQ_HOST = %emq_host% > buildConfig.py
 echo EMQ_PORT = %emq_port% >> buildConfig.py
 echo WEBSITE_SERVER_HOST = %website_server_host% >> buildConfig.py
 echo BUILD_FOR = %build_for% >> buildConfig.py
 echo MODE = %mode% >> buildConfig.py
 echo BUILD_VERSION = %build_version% >> buildConfig.py
 echo ENABLE_DEVELOP_ACCOUNT = %enable_develop_account% >> buildConfig.py
 move buildConfig.py ../../System/
 goto exit
 
:exit