#!/usr/bin/env bash
# please execute this script at path Personal/Installer/mac
#

echo "[INFO] uploading ppp .dmg file ..."

cd ..

HOST=ftp.cyberpower.com.tw
USER=lisber
PASS=lisber
FOLDER_NAME=`date +%Y%m%d_%H%M`
INSTALLER_FILE=`find . -iname ppp_*.dmg`
MD5_FILE=md5sums


ftp -nv $HOST << END_SCRIPT
quote user $USER
quote pass $PASS

binary

cd build/PPP/
mkdir $FOLDER_NAME
cd $FOLDER_NAME
put "$INSTALLER_FILE"
put "$MD5_FILE"

quit
END_SCRIPT
exit 0
