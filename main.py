import logging
from consumer import SQSConsumer

logging.basicConfig(level=logging.INFO)


def main():
    sqs_consumer = SQSConsumer()
    while True:
        # Fetch the sqs messages
        sqs_data = sqs_consumer.poll()


if __name__ == "__main__":
    main()
