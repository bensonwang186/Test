#!/bin/sh

assignCPS_formal(){ 
  emq_host="'iot.cyberpower.com'"
  emq_port=8883
  website_server_host="'iotapi.cyberpower.com'"
  build_for=0
  mode=1
}

assignCPS_demo(){
  emq_host="'iottest.cyberpower.com'"
  emq_port=8883
  website_server_host="'iotapitest.cyberpower.com'"
  build_for=1
  mode=0
}

if [ $1 = 'formal' ] 
then
  assignCPS_formal
elif [ $1 = 'demo' ]
then
  assignCPS_demo
fi

# first to clear content in buildConfig.py
build_version=$(git rev-parse --short HEAD)
build_version="'${build_version}'"

if [ $2 = 'true' ]
then
  enable_develop_account="'true'"
elif [ $2 = 'false' ]
then
  enable_develop_account="'false'"
fi

echo "EMQ_HOST = $emq_host" > ./buildConfig.py
echo "EMQ_PORT = $emq_port" >> ./buildConfig.py
echo "WEBSITE_SERVER_HOST = $website_server_host" >> ./buildConfig.py
echo "BUILD_FOR = $build_for" >> ./buildConfig.py
echo "MODE = $mode" >> ./buildConfig.py
echo "BUILD_VERSION = $build_version" >> ./buildConfig.py
echo "ENABLE_DEVELOP_ACCOUNT = $enable_develop_account" >> ./buildConfig.py
mv ./buildConfig.py ../../System/
