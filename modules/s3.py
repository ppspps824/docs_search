import io

import boto3
import joblib
import streamlit as st


@st.cache_resource(show_spinner=False)
def get_client_bucket():
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=st.secrets["aws_access_key_id"],
        aws_secret_access_key=st.secrets["aws_secret_access_key"],
        region_name="ap-northeast-1",
    )

    bucket = s3.Bucket("vector-index")
    return bucket


def s3_upload(file):
    bucket = get_client_bucket()
    with io.BytesIO() as bf:
        joblib.dump(file, bf, compress=3)
        bf.seek(0)
        bucket.upload_fileobj(bf, "index.joblib")


def s3_get_index():
    bucket = get_client_bucket()
    with io.BytesIO() as f:
        bucket.download_fileobj("index.joblib", f)
        f.seek(0)
        result = joblib.load(f)

    return result
