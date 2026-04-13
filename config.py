import os
from dataclasses import dataclass


@dataclass
class Config:
    # SQS
    aws_region: str = os.getenv("AWS_REGION", "ap-south-1")
    max_messages: int = 10
    wait_time_seconds: int = 20
    visibility_timeout: int = 60

    # Other config
    poll_wait_time = 10

    # Input json keys
    mandatory_keys = ("id", "mail", "name", "surname")
    other_keys = [("route", "locations")]

    # Database
    database = "mydb"
    schema = "sqs"
    table_name = "messages"

    table_columns_datatype_map = {
        "id": "integer",
        "mail": "text",
        "name": "text",
        "departure": "text",
        "destination": "text",
        "start_date": "timestamp",
        "end_date": "timestamp",
    }
    primary_key = ("id", "departure", "destination")

    dsn = f"postgresql://myuser:secret@localhost:5432/{database}"

    def __post_init__(self):
        self.queue_url = os.getenv(
            "SQS_QUEUE_URL",
            f"http://{self.aws_region}.localhost.localstack.cloud:4566/000000000042/test-queue",
        )
