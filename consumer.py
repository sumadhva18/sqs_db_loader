import boto3
import logging
from typing import List
from config import Config

logger = logging.getLogger(__name__)


class SQSConsumer:
    def __init__(self):
        self.config = Config()

        self.queue_url = self.config.queue_url
        self.aws_region = self.config.aws_region
        self.max_messages = self.config.max_messages
        self.wait_time_seconds = self.config.wait_time_seconds
        self.visibility_timeout = self.config.visibility_timeout

        self.sqs = boto3.client(
            "sqs",
            endpoint_url=self.queue_url,
            region_name=self.aws_region,
        )

    def poll(self) -> List[dict]:
        """
        Hits the sqs endpoint to get the messages available in the queue

        Returns:
            List[dict]: List of messages from the queue
        """
        logger.info(f"Reading messages from the queue {self.queue_url}")
        response = self.sqs.receive_message(
            QueueUrl=self.queue_url,
            MaxNumberOfMessages=self.max_messages,
            WaitTimeSeconds=self.wait_time_seconds,
            VisibilityTimeout=self.visibility_timeout,
        )
        return response.get("Messages", [])

    def delete_message(self, *receipt_handle_ids) -> None:
        """
        Deletes the message associated with the provided receipt handle id

        :param receipt_handle_ids: Receipt IDs to be deleted
        """
        for receipt_handle_id in receipt_handle_ids:
            self.sqs.delete_message(
                QueueUrl=self.config.queue_url, ReceiptHandle=receipt_handle_id
            )
            logger.info("Deleted Receipt Handle ID: %s", receipt_handle_id)
