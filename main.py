import logging
from consumer import SQSConsumer
from processor import MessageProcessor

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


if __name__ == "__main__":
    main()
