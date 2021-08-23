#!/usr/bin/env bash
cd ../../resources
rm qt_resources.py
pyrcc5 -o qt_resources.py qt_resources.qrc