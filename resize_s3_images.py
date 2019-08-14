import os
import boto3
import botocore
import PIL
from PIL import Image
from io import BytesIO

s3 = boto3.resource('s3')


def is_resized_image_exists(bucket_name, key, size):
    try:
        s3.Object(bucket_name=bucket_name, key='{size}_{key}'.format(size=size, key=key)).load()
    except botocore.exceptions.ClientError:
        return None


def resize_image(bucket_name, key, size):
    size_split = size.split('x')
    try:
        s3.Object(bucket_name=bucket_name, key=key).load()
        is_resized_image_exists(bucket_name, key, size)
    except botocore.exceptions.ClientError:
        return None
    obj = s3.Object(bucket_name=bucket_name, key=key)
    obj_body = obj.get()['Body'].read()
    img = Image.open(BytesIO(obj_body))
    img = img.resize((int(size_split[0]), int(size_split[1])), PIL.Image.ANTIALIAS)
    buffer = BytesIO()
    img.convert('RGB').save(buffer, 'JPEG')
    buffer.seek(0)
    resized_key='{size}_{key}'.format(size=size, key=key)
    obj = s3.Object(bucket_name=bucket_name, key=resized_key)
    obj.put(Body=buffer, ContentType='image/jpeg')
    return "https://{bucket}.s3.amazonaws.com/{resized_key}".format(bucket=bucket_name, resized_key=resized_key)


def lambda_handler(event, context):
    key = event['queryStringParameters'].get('key', None)
    size = event['queryStringParameters'].get('size', None)

    image_s3_url = resize_image(os.environ['BUCKET_NAME'], key, size)

    return {
        'statusCode': 301,
        'body': image_s3_url
    }
