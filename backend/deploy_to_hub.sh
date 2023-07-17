#! /bin/bash

scp app.py zpadmin@zp-hub:/opt/zp-hub/backend
scp blob_storage.py zpadmin@zp-hub:/opt/zp-hub/backend
scp data_utils.py zpadmin@zp-hub:/opt/zp-hub/backend
scp zp_database.py zpadmin@zp-hub:/opt/zp-hub/backend
scp requirements.txt zpadmin@zp-hub:/opt/zp-hub/backend
