#!/usr/bin/env bash
# please execute this script at path Personal/Installer/mac
#

# enter venv
echo "[INFO] Entering python venv..."
source ../../venv/bin/activate
echo "[INFO] Python venv python version:"
python --version


echo "[INFO] Remove modules PyQt5 and PyQt5-sip ..."
python3 -m pip uninstall -y PyQt5 PyQt5-commercial PyQt5-sip
python3 -m pip list


HOST=ftp.cyberpower.com.tw
USER=lisber
PASS=lisber
BUILD_ARCHIVE_PATH="build/Riverbank_PyQt/build/mac"
BUILD_ARCHIVE_FILE_NAME="PyQt5_commercial-5.12.2-5.12.3-cp35.cp36.cp37.cp38-abi3-macosx_10_6_intel.whl"

echo "[INFO] FTP get PyQt build archive"
ftp -nv $HOST << END_SCRIPT
quote user $USER
quote pass $PASS

binary

cd "$BUILD_ARCHIVE_PATH"
get "$BUILD_ARCHIVE_FILE_NAME"

quit
END_SCRIPT

echo "[INFO] Install PyQt commercial version..."
python3 -m pip install $BUILD_ARCHIVE_FILE_NAME

echo "[INFO] Show pip list to check..."
python3 -m pip list

