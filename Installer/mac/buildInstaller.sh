#!/usr/bin/env bash
# please execute this script at path Personal/Installer/mac
#

CYTHONIZE_BUILD_DIR="build/lib.macosx-10.6-intel-3.6"

# application bundle execution dir
APP_BUNDLE_DIR="build/PowerPanel Personal.app"
APP_EXE_DIR="$APP_BUNDLE_DIR/Contents/MacOS"


# enter venv
echo "[INFO] Entering python venv..."
source ../../venv/bin/activate
echo "[INFO] Python venv python version:"
python --version


# rebuild qt resource file
echo "[INFO] Compiling Qt resources file..."
./compile_qt_resources.sh


# back to project root
cd ../..

# remove build files
echo "[INFO] Clearing build files..."
rm -rf build
rm -rf Installer/PowerPanel\ Personal.app
rm Installer/ppp_macos_*.dmg


# i18n, gettext translation
echo "[INFO] Translating .po file to .mo with \"gettext\" AND delte .po file ..."
find i18n -iname *.po -exec bash -c 'MO_NAME=`echo $0 | sed s/.po/.mo/g`; echo "[INFO] msgfmt $0 -o $MO_NAME;"; msgfmt $0 -o $MO_NAME; echo "[INFO] Clear .po file $0"; rm $0;' {} \;


# cx_freeze build
echo "[INFO] Freezing PPP for MacOS application bundle..."
python setup.py bdist_mac


# correct Info.plist
echo "[INFO] Correct application bundle version info..."
cp -rp "build/PowerPanel Personal-0.1.app" "$APP_BUNDLE_DIR"
sed 's/PowerPanel Personal-0.1/PowerPanel Personal/g' "$APP_BUNDLE_DIR/Contents/Info.plist" > tmp.plist
mv tmp.plist "$APP_BUNDLE_DIR/Contents/Info.plist"


# cx_freeze workaround for library soundfile, copy its dependency files
echo "[INFO] Copy library soundfile dependency files for workaround of cx_freeze ..."
mv "$APP_EXE_DIR/_soundfile_data" "$APP_EXE_DIR/lib/"


# remove unnecessary library and files

# clear pyc files
echo "[INFO] Clearing cx_freeze .pyc files..."
rm "$APP_EXE_DIR"/lib/major/*.pyc
rm "$APP_EXE_DIR"/lib/Events/*.pyc
rm "$APP_EXE_DIR"/lib/Utility/*.pyc
rm "$APP_EXE_DIR"/lib/handler_refactor/*.pyc
rm "$APP_EXE_DIR"/lib/ClientHandler/*.pyc
rm "$APP_EXE_DIR"/lib/ClientModel/*.pyc
rm "$APP_EXE_DIR"/lib/model_Json/*.pyc
rm "$APP_EXE_DIR"/lib/controllers/*.pyc
rm "$APP_EXE_DIR"/lib/System/*.pyc


# ensure no .c files exist
echo "[INFO] Ensure no .c file exists..."
rm "$APP_EXE_DIR"/lib/major/*.c
rm "$APP_EXE_DIR"/lib/Events/*.c
rm "$APP_EXE_DIR"/lib/Utility/*.c
rm "$APP_EXE_DIR"/lib/handler_refactor/*.c
rm "$APP_EXE_DIR"/lib/ClientHandler/*.c
rm "$APP_EXE_DIR"/lib/ClientModel/*.c
rm "$APP_EXE_DIR"/lib/model_Json/*.c
rm "$APP_EXE_DIR"/lib/controllers/*.c
rm "$APP_EXE_DIR"/lib/System/*.c
rm "$APP_EXE_DIR"/Daemon.c


# cython compile
echo "[INFO] Cythonize..."
# clear __init__.py. it may caused cython crashed.
rm __init__.py
# link .so as executable instead of bundle.
#LDSHARED="/usr/bin/clang -undefined dynamic_lookup -g -arch x86_64" ARCHFLAGS="-arch x86_64" python pyd-setup_mac.py build
echo "[INFO] Compiling and Linking to .so bundle files..."
ARCHFLAGS="-arch x86_64" python pyd-setup_mac.py build


echo "[INFO] Installing cythonize .so files..."
cp -a "$CYTHONIZE_BUILD_DIR"/major/*.so  "$APP_EXE_DIR"/lib/major/
cp -a "$CYTHONIZE_BUILD_DIR"/Events/*.so  "$APP_EXE_DIR"/lib/Events/
cp -a "$CYTHONIZE_BUILD_DIR"/Utility/*.so  "$APP_EXE_DIR"/lib/Utility/
cp -a "$CYTHONIZE_BUILD_DIR"/handler_refactor/*.so  "$APP_EXE_DIR"/lib/handler_refactor/
cp -a "$CYTHONIZE_BUILD_DIR"/ClientHandler/*.so  "$APP_EXE_DIR"/lib/ClientHandler/
cp -a "$CYTHONIZE_BUILD_DIR"/ClientModel/*.so  "$APP_EXE_DIR"/lib/ClientModel/
cp -a "$CYTHONIZE_BUILD_DIR"/model_Json/*.so  "$APP_EXE_DIR"/lib/model_Json/
cp -a "$CYTHONIZE_BUILD_DIR"/controllers/*.so  "$APP_EXE_DIR"/lib/controllers/
cp -a "$CYTHONIZE_BUILD_DIR"/System/*.so  "$APP_EXE_DIR"/lib/System/

# delete po file


echo "[INFO] Moving application bundle..."
mv "$APP_BUNDLE_DIR" Installer/

echo "[INFO] Build PPP installer..."
/Applications/install4j.app/Contents/Resources/app/bin/install4jc ./Installer/pppe.install4j -m macosFolder
