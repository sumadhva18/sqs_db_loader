import logging
from consumer import SQSConsumer
from processor import MessageProcessor

logging.basicConfig(level=logging.INFO)


def main():
    sqs_consumer = SQSConsumer()
    processor = MessageProcessor()

    parsed_data = dict()

    while True:
        # Fetch the sqs messages
        sqs_data = sqs_consumer.poll()

        # Validate data
        for message in sqs_data:
            valid_data = processor.validate(message)

            if valid_data:
                parsed_data[message["MessageId"]] = valid_data


if __name__ == "__main__":
    main()
