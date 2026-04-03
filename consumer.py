import boto3
import logging
from typing import List
from config import Config

logger = logging.getLogger(__name__)


class SQSConsumer:
    def __init__(self):
        self.config = Config()
        self.sqs = boto3.client(
            "sqs",
            endpoint_url=self.config.queue_url,
            region_name=self.config.aws_region,
        )

    def poll(self) -> List[dict]:
        """
        Hits the sqs endpoint to get the messages available in the queue

        Returns:
            List[dict]: List of messages from the queue
        """
        logger.info(f"Reading messages from the queue {self.config.queue_url}")
        response = self.sqs.receive_message(
            QueueUrl=self.config.queue_url,
            MaxNumberOfMessages=self.config.max_messages,
            WaitTimeSeconds=self.config.wait_time_seconds,
            VisibilityTimeout=self.config.visibility_timeout,
        )
        return response.get("Messages", [])
