import boto3, botocore
from config import *
from app import app

s3 = boto3.client("s3",
                  aws_access_key_id=app.config["S3_KEY"],
                  aws_secret_access_key=app.config["S3_SECRET"])

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def upload_file_to_s3(file, bucket_name, acl="public-read"):

    try:

        s3.upload_fileobj(file,
                          bucket_name,
                          file.filename,
                          ExtraArgs={
                              "ACL": acl,
                              "ContentType": file.content_type
                          })

    except Exception as e:
        print("A possible error occurred: ", e)
        return e

    return "{}{}".format(app.config["S3_LOCATION"], file.filename)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS