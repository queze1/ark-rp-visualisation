from unittest.mock import Mock

import pandas as pd

from ark_rp_visualisation.core.data_loader import DataLoader
from ark_rp_visualisation.utils import s3


def test_r2_client_settings(monkeypatch):
    monkeypatch.setenv("AWS_ENDPOINT_URL", "https://account.r2.cloudflarestorage.com")
    monkeypatch.setenv("AWS_REGION", "auto")
    client = Mock()
    boto_client = Mock(return_value=client)
    monkeypatch.setattr(s3.boto3, "client", boto_client)

    assert s3.get_s3_storage_options() == {
        "client_kwargs": {
            "endpoint_url": "https://account.r2.cloudflarestorage.com",
            "region_name": "auto",
        }
    }
    assert s3.create_s3_client() is client
    boto_client.assert_called_once_with(
        "s3",
        endpoint_url="https://account.r2.cloudflarestorage.com",
        region_name="auto",
    )


def test_aws_defaults_do_not_add_client_settings(monkeypatch):
    monkeypatch.delenv("AWS_ENDPOINT_URL", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)
    boto_client = Mock()
    monkeypatch.setattr(s3.boto3, "client", boto_client)

    assert s3.get_s3_storage_options() == {}
    s3.create_s3_client()
    boto_client.assert_called_once_with("s3")


def test_load_s3_passes_r2_storage_options(monkeypatch):
    monkeypatch.setenv("AWS_ENDPOINT_URL", "https://account.r2.cloudflarestorage.com")
    monkeypatch.setenv("AWS_REGION", "auto")
    read_parquet = Mock(return_value=pd.DataFrame())
    monkeypatch.setattr(pd, "read_parquet", read_parquet)
    monkeypatch.setattr(
        "ark_rp_visualisation.core.data_loader.S3_URL", "s3://bucket/data.parquet"
    )

    DataLoader().load_s3()

    read_parquet.assert_called_once_with(
        "s3://bucket/data.parquet",
        storage_options={
            "client_kwargs": {
                "endpoint_url": "https://account.r2.cloudflarestorage.com",
                "region_name": "auto",
            }
        },
    )
