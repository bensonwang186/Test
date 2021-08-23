#!/usr/bin/env bash
cd ../..

if [ $1 = 'true' ]
then
  python genUpdateFile.py
fi