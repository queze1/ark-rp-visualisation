"""Configuration helpers for S3-compatible object storage."""

import os

import boto3


def get_s3_client_kwargs() -> dict[str, str]:
    kwargs = {}
    if endpoint_url := os.getenv("AWS_ENDPOINT_URL"):
        kwargs["endpoint_url"] = endpoint_url
    if region_name := os.getenv("AWS_REGION"):
        kwargs["region_name"] = region_name
    return kwargs


def get_s3_storage_options() -> dict[str, dict[str, str]]:
    client_kwargs = get_s3_client_kwargs()
    return {"client_kwargs": client_kwargs} if client_kwargs else {}


def create_s3_client():
    return boto3.client("s3", **get_s3_client_kwargs())
