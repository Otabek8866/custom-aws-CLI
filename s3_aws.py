import boto3
import logging
from botocore.exceptions import ClientError
import time
import os


# a file to upload to a bucket
def upload_file(s3_resource, bucket_name, file_path, file_name):
    try:
        data = open(file_path, 'rb')
        start = time.time()
        s3_resource.Bucket(bucket_name).put_object(Key=file_name, Body=data)
        end = time.time()

    except ClientError as e:
        print(e)
        logging.error(e)
        return 0

    return end-start


# function to download a file from a bucket
def download_file(s3_client, bucket_name, file_name):
    try:
        start = time.time()
        s3_client.download_file(bucket_name, file_name, file_name)
        end = time.time()

    except ClientError as e:
        print(e)
        logging.error(e)
        return 0

    return end-start


# delete a file from a bucket
def delete_file(s3_resource, bucket_name, file_name):
    try:
        s3_resource.Object(bucket_name, file_name).delete()

    except ClientError as e:
        print(e)
        logging.error(e)
        return False

    return True


# func to create a bucket
def create_bucket(s3_resource, bucket_name, region=None):
    success = True
    try:
        if region is None:
            s3_resource.create_bucket(Bucket=bucket_name)
        else:
            location = {'LocationConstraint': region}
            s3_resource.create_bucket(
                Bucket=bucket_name, CreateBucketConfiguration=location)

    except ClientError as e:
        success = False
        print(e)
        pass
        
    if success:
        print("Bucket created successfully")
    else:
        print("A problem occured while creating a bucket, please try again!")


# func to delete a bucket
def delete_bucket(s3_client, bucket_name):
    try:
        _ = s3_client.delete_bucket(Bucket=bucket_name)

    except ClientError as e:
        print(e)
        logging.error(e)
        return False

    return True


# func to empty a bucket
def empty_bucket(s3_resource, bucket_name):
    # Create bucket
    try:
        bucket = s3_resource.Bucket(bucket_name)
        bucket.objects.all().delete()

    except ClientError as e:
        print(e)
        logging.error(e)
        return False

    return True


# Printing the list of buckets
def print_content(s3_client, region_name=None):
    if region_name:
        i = 1
        for bucket in s3_client.list_buckets()["Buckets"], :
            if s3_client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint'] == region_name:
                print(bucket["Name"])
                i = i + 1
    else:
        i = 1
        for bucket in s3_client.list_buckets()["Buckets"]:
            print(i,":",bucket["Name"])
            i = i + 1
