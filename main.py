import json
import logging
from consumer import SQSConsumer
from processor import MessageProcessor
from db import DatabaseLoader

logging.basicConfig(level=logging.INFO)


def main():
    sqs_consumer = SQSConsumer()
    processor = MessageProcessor()

    parsed_msgs = dict()
    transformed_msgs = dict()

    while True:
        # Fetch the sqs messages
        sqs_data = sqs_consumer.poll()

        # Validate data
        for message in sqs_data:
            is_valid_data = processor.validate(message)

            if is_valid_data:
                parsed_msgs[message["ReceiptHandle"]] = json.loads(message["Body"])
            else:
                sqs_consumer.delete_message(message["ReceiptHandle"])

        # Transform data
        for receipt_handle_id, message in parsed_msgs.items():
            transformed_data = processor.transform(message)

            if transformed_data:
                transformed_msgs[receipt_handle_id] = transformed_data

        data_to_be_loaded = list()

        for value in transformed_msgs.values():
            data_to_be_loaded.append(value)

        # Load the data
        if data_to_be_loaded:
            with DatabaseLoader() as db_loader:
                db_loader.ensure_table()
                db_loader.load(data_to_be_loaded)

        # Delete the loaded messages from queue
        if transformed_msgs:
            sqs_consumer.delete_message(*transformed_msgs.keys())


if __name__ == "__main__":
    main()
