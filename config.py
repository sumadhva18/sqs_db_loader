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

    def __post_init__(self):
        self.queue_url = os.getenv(
            "SQS_QUEUE_URL",
            f"http://{self.aws_region}.localhost.localstack.cloud:4566/000000000042/test-queue",
        )
