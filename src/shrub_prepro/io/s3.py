import s3fs


def get_s3_file(s3_path):
    """
    Open a file from S3 using s3fs.

    Args:
        s3_path (str): S3 path in format 's3://bucket/path/to/file'

    Returns:
        file-like object
    """
    fs = s3fs.S3FileSystem(anon=False)
    return fs.open(s3_path, "rb")
