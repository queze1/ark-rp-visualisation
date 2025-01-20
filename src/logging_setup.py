import logging
import os

import boto3
from dotenv import load_dotenv

load_dotenv(override=True)


S3_LOG_PATH = dict(Bucket=os.getenv("S3_BUCKET"), Key="app.log")


class S3Handler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.s3_client = boto3.client("s3")
        self.logs = self._load_logs()

    def _load_logs(self) -> str:
        try:
            response = self.s3_client.get_object(**S3_LOG_PATH)
            logs = response["Body"].read().decode("utf-8")
        except self.s3_client.exceptions.NoSuchKey:
            logs = ""
        return logs

    def _upload_logs(self):
        self.s3_client.put_object(
            Body=self.logs.encode("utf-8"),
            **S3_LOG_PATH,
        )

    def emit(self, record: logging.LogRecord) -> None:
        try:
            log_entry = self.format(record)
            if self.logs:
                self.logs += f"\n{log_entry}"
            else:
                # Skip leading newline on first entry
                self.logs = log_entry
            self._upload_logs()
        except Exception:
            self.handleError(record)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )

        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Add S3 handler
        s3_handler = S3Handler()
        s3_handler.setLevel(logging.INFO)
        s3_handler.setFormatter(formatter)
        logger.addHandler(s3_handler)

    return logger
