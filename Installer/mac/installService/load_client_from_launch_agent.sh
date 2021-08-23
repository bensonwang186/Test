
TARGET_DIR=/Library/LaunchAgents
PLIST_NAME=com.cyberpower.powerpanel-personal.client.plist

## launchctl for launch agents; sudo launchctl for launch daemon
echo "launchctl load $TARGET_DIR/$PLIST_NAME"
launchctl setenv argv first
launchctl load $TARGET_DIR/$PLIST_NAME
