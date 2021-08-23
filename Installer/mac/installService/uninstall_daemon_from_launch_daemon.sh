
TARGET_DIR=/Library/LaunchDaemons
PLIST_NAME=com.cyberpower.powerpanel-personal.daemon.plist

echo "remove daemon launch daemon plist"
sudo rm $TARGET_DIR/$PLIST_NAME

