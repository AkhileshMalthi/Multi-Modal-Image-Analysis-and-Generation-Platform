import boto3
import os
from botocore.exceptions import NoCredentialsError

def get_s3_client():
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        return s3_client
    except NoCredentialsError:
        raise RuntimeError("AWS credentials not available")
    except Exception as e:
        raise RuntimeError(f"Error initializing S3 client: {e}")

BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

def upload_file_to_s3(file_obj, object_name):
    try:
        s3_client = get_s3_client()
        
        # Read file content into memory to allow retries
        file_content = file_obj.read()
        
        # Try uploading with public-read ACL first
        try:
            from io import BytesIO
            s3_client.upload_fileobj(
                BytesIO(file_content), 
                BUCKET_NAME, 
                object_name,
                ExtraArgs={'ACL': 'public-read'}
            )
            url = f"https://{BUCKET_NAME}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{object_name}"
            print(f"✓ Uploaded with public ACL: {object_name}")
            return url
        except Exception as acl_error:
            # If ACL fails (bucket blocks public access), upload without ACL and use presigned URL
            print(f"Public ACL not supported, using presigned URL: {acl_error}")
            from io import BytesIO
            s3_client.upload_fileobj(BytesIO(file_content), BUCKET_NAME, object_name)
            
            # Generate a presigned URL that's valid for 7 days
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': object_name},
                ExpiresIn=604800  # 7 days
            )
            print(f"✓ Uploaded with presigned URL: {object_name}")
            return url
            
    except NoCredentialsError:
           print("Credentials not available for S3 upload.")
           return None
    except Exception as e:
           print(f"Error uploading to S3: {e}")
           return None
    