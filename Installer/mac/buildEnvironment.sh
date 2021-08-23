#!/usr/bin/env bash
# please execute this script at path Personal/Installer/mac
#

# create virtual environment
echo "[INFO] Creating python virtual environment..."
cd ../..
python3 -m virtualenv venv

# enter venv
echo "[INFO] Entering python venv..."
source venv/bin/activate
echo "[INFO] Python venv python version:"
python --version

# pip install modules
echo "[INFO] Installing python modules..."
python3 -m pip install -r requirements_mac.txt 

# setup cx_freeze
echo "[INFO] Building and installing cx_freeze dev lasted version..."
echo "[INFO] git clone cx-Freeze project..."
git clone https://github.com/anthony-tuininga/cx_Freeze.git
cd cx_Freeze/
echo "[INFO] Checkout to revision 9e06b761(lasted)..."
git checkout 9e06b761
echo "[INFO] Building cx-Freeze..."
python3 setup.py build
echo "[INFO] Installing cx-Freeze..."
python3 setup.py install
echo "[INFO] Check cx_freeze installation successfully"
python3 -m pip list | grep -i cx-freeze

# workaround for cx_freeze
echo "[INFO] Creating Qt framework soft links for workaround of cx_freeze."
cd ../Installer/mac
./cx_freeze_bug_workaround.sh

# print installed python modules
echo "[INFO] Print installed python modules..."
python3 -m pip list

