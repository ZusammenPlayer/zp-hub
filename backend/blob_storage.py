from minio import Minio
from minio.error import S3Error

class BlobStorage:
    def __init__(self, host, user, password):
        self.__client = Minio(host, access_key=user, secret_key=password)
    
    def put(self, filename, file_data, bucket):
        print('add to minio')

        # check if bucket exists
        found = self.__client.bucket_exists(bucket)

        if not found:
            self.__client.make_bucket(bucket)
        
        # upload to s3
        self.__client.put_object(bucket, filename, file_data)

