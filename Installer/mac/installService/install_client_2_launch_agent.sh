## create client plist under /Library/LaunchAgents

TARGET_DIR=/Library/LaunchAgents
PLIST_NAME=com.cyberpower.powerpanel-personal.client.plist
WORKING_DIR=$1

if [ -f $TARGET_DIR/$PLIST_NAME ]
then
    sudo rm $TARGET_DIR/$PLIST_NAME
fi

PLIST_CONTENT="<?xml version="1.0" encoding="UTF-8"?>\n"
PLIST_CONTENT+="<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n"
PLIST_CONTENT+="<plist version=\"1.0\">\n"
PLIST_CONTENT+="<dict>\n"
PLIST_CONTENT+="\t<key>Label</key>\n"
PLIST_CONTENT+="\t<string>com.cyberpower.powerpanel-personal.client</string>\n"
PLIST_CONTENT+="\t<key>WorkingDirectory</key>\n"
PLIST_CONTENT+="\t<string>$WORKING_DIR</string>\n"
PLIST_CONTENT+="\t<key>ProgramArguments</key>\n"
PLIST_CONTENT+="\t<array>\n"
PLIST_CONTENT+="\t\t<string>$WORKING_DIR/PowerPanel Personal</string>\n"
PLIST_CONTENT+="\t</array>\n"
PLIST_CONTENT+="\t<key>RunAtLoad</key>\n"
PLIST_CONTENT+="\t<true/>\n"
PLIST_CONTENT+="</dict>\n"
PLIST_CONTENT+="</plist>\n"

echo "create plist $TARGET_DIR/$PLIST_NAME, contents:\n"
echo $PLIST_CONTENT

echo $PLIST_CONTENT > $TARGET_DIR/$PLIST_NAME

