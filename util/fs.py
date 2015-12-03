import environment
import boto
import boto.s3.connection
import environment

conn = boto.connect_s3(
    aws_access_key_id = environment.ACCESS_KEY_ID,
    aws_secret_access_key = environment.SECRET_ACCESS_KEY,
)
bucket = conn.get_bucket('bencast')

def get_keys(d):
    return bucket.list(d + '/', '/')

