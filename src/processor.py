import json
from config import Config
import logging
from itertools import chain
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


class MessageProcessor:
    TRANSFORMATION_TEMPLATE = {
        "id": lambda message: message["id"],
        "mail": lambda message: message["mail"],
        "name": lambda message: f"{message['name']} {message['surname']}",
        "trip": lambda message: MessageProcessor._transform_trip(message),
    }

    def __init__(self):
        self.config = Config()
        self.required_keys = list(self.config.mandatory_keys)
        self.required_keys.extend(list(chain.from_iterable(self.config.other_keys)))

    def validate(self, message: dict) -> bool:
        """
        Validates whether all the required keys are present in the message

        :param message: Message to be validated
        :type message: dict
        :return: Returns True if the message is valid, otherwise False
        :rtype: bool
        """
        message_id = message.get("MessageId")
        try:
            assert message.get("Body"), (
                f"Message body not found for the message ID: {message_id}"
            )

            message_body = json.loads(message["Body"])
            message_body_keys = set(message_body.keys())
            mandatory_keys = self.config.mandatory_keys
            other_keys = self.config.other_keys

            for key in mandatory_keys:
                assert key in message_body_keys, f"Missing {key}"

            for key_pair in other_keys:
                assert message_body_keys.intersection(key_pair), (
                    f"Missing one of the keys {', '.join(key_pair)}"
                )

            return True
        except Exception as e:
            logger.error(f"Invalid message body for the message ID: {message_id}: {e}")
            return False

    @classmethod
    def _transform_trip(cls, message: dict) -> list[dict]:
        if message.get("route"):
            legs = message["route"]
            trip = []
            for leg in legs:
                start_timestamp = datetime.strptime(
                    leg["started_at"], "%d/%m/%Y %H:%M:%S"
                )
                end_timestamp = start_timestamp + timedelta(minutes=leg["duration"])
                trip.append(
                    {
                        "departure": leg["from"],
                        "destination": leg["to"],
                        "start_timestamp": start_timestamp.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "end_timestamp": end_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )
            return trip

        else:
            locations = sorted(
                message.get("locations", []), key=lambda x: x["timestamp"]
            )
            return [
                {
                    "departure": locations[0]["location"],
                    "destination": locations[-1]["location"],
                    "start_timestamp": datetime.fromtimestamp(
                        locations[0]["timestamp"], tz=timezone.utc
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "end_timestamp": datetime.fromtimestamp(
                        locations[-1]["timestamp"], tz=timezone.utc
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                }
            ]

    def transform(self, message: dict) -> dict | None:
        """
        Transforms the given message into below format

        ```
        {
            "id": 1,
            "mail": "aaa@gmail.com",
            "name": "AAA SSS",
            "trip": [
                {
                    "depaure": "A",
                    "destination": "D",
                    "start_timestamp": "2022-10-10 12:15:00",
                    "end_timestamp": "2022-10-10 13:55:00"
                }
            ]
        }
        ```

        :param message: The message to be transformed
        :type message: dict
        :return: The output in the above format, None is case of errors
        :rtype: dict | None
        """

        try:
            return {
                key: transform_fn(message)
                for key, transform_fn in self.TRANSFORMATION_TEMPLATE.items()
            }
        except Exception as e:
            logger.error(
                f"Invalid message body for the message ID: {message.get('id')}: {e}"
            )
            return None
