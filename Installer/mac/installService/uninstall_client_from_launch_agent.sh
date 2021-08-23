
TARGET_DIR=/Library/LaunchAgents
PLIST_NAME=com.cyberpower.powerpanel-personal.client.plist

echo "remove client launch agent plist"
sudo rm $TARGET_DIR/$PLIST_NAME

