#!/usr/bin/env bash
# establish soft link of Qt Frameworks to cover cx_freeze bug. It detects environment path incorrectly. In its py, command 'otool -L' should be replaced by 'otool -l'.
# 
# Details as below:
# $ python setup.py build
# copying /Users/dev/workspace_PPP/Personal/venv/lib/python3.6/site-packages/PyQt5/QtCore.so -> build/build_macosx/lib/PyQt5/QtCore.so
# copying /Users/dev/workspace_PPP/Personal/venv/lib/QtCore.framework/Versions/5/QtCore -> build/build_macosx/lib/PyQt5/QtCore
# error: [Errno 2] No such file or directory: '/Users/dev/workspace_PPP/Personal/venv/lib/QtCore.framework/Versions/5/QtCore'
#
# please execute this script in project root path.
# by Lisber 2019/01
#

echo "cd ../../venv/lib"
cd ../../venv/lib
ln -sv python3.6/site-packages/PyQt5/Qt/lib/* .

