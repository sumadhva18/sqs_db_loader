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
    database = os.getenv("POSTGRES_DB", "mydb")
    schema = os.getenv("POSTGRES_SCHEMA", "sqs")
    table_name = os.getenv("POSTGRES_TABLE_NAME", "messages")

    table_columns_datatype_map = {
        "id": "integer",
        "mail": "text",
        "name": "text",
        "departure": "text",
        "destination": "text",
        "start_timestamp": "timestamp",
        "end_timestamp": "timestamp",
    }
    primary_key = ("id", "departure", "destination", "start_timestamp")

    dsn = os.getenv("DATABASE_URL")
    queue_url = os.getenv("SQS_QUEUE_URL")

    def __post_init__(self):
        if not self.dsn:
            raise ValueError("Unable to find the postgres dsn url")

        if not self.queue_url:
            raise ValueError("Unable to find the SQS queue url")
