
TARGET_DIR=/Library/LaunchDaemons
PLIST_NAME=com.cyberpower.powerpanel-personal.daemon.plist

## launchctl for launch agents; sudo launchctl for launch daemon
echo "sudo launchctl unload $TARGET_DIR/$PLIST_NAME"
sudo launchctl unload $TARGET_DIR/$PLIST_NAME
