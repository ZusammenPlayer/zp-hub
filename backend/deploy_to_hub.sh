#! /bin/bash

DEPLOY_HOST=""$1

TS=`date +%s`

RELEASE_NAME="zp-hub-backend"$TS
RELEASE_FILE="releases/"$RELEASE_NAME".zip"

mkdir $RELEASE_NAME

cp -r src $RELEASE_NAME
rm -rf $RELEASE_NAME/src/__pycache__
rm -rf $RELEASE_NAME/src/handler/__pycache__
rm -rf $RELEASE_NAME/src/config.py
cp requirements.txt $RELEASE_NAME

zip -r $RELEASE_FILE $RELEASE_NAME

# cleanup
rm -rf $RELEASE_NAME

if [ -v "$DEPLOY_HOST"]; then
    rm -rf $RELEASE_NAME
    echo "release created"
    exit
fi

# copy release file to server
scp $RELEASE_FILE $DEPLOY_HOST:/opt/zp-hub/backend/releases

# define remote commands
CMD_REMOVE_LATEST="rm -rf /opt/zp-hub/backend/latest"
CMD_UNZIP_RELEASE="cd /opt/zp-hub/backend/releases;unzip /opt/zp-hub/backend/releases/"$RELEASE_NAME".zip"
CMD_CREATE_LATEST="ln -s /opt/zp-hub/backend/releases/"$RELEASE_NAME" /opt/zp-hub/backend/latest"
CMD_COPY_CONFIG="cp /opt/zp-hub/backend/config.py /opt/zp-hub/backend/latest/src"

# do the server side stuff
ssh $DEPLOY_HOST $CMD_REMOVE_LATEST
ssh $DEPLOY_HOST $CMD_UNZIP_RELEASE
ssh $DEPLOY_HOST $CMD_CREATE_LATEST
ssh $DEPLOY_HOST $CMD_COPY_CONFIG
