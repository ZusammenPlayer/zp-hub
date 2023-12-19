#! /bin/bash

DEPLOY_HOST=""$1

npm run build

scp -r dist $DEPLOY_HOST:/opt/zp-hub/frontend/
