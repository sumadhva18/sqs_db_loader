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

    def validate(self, message: dict) -> dict | None:
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

            return message_body
        except Exception as e:
            logger.error(f"Invalid message body for the message ID: {message_id}: {e}")
            return None

    @classmethod
    def _transform_trip(cls, message: dict) -> list[dict]:
        if message.get("route"):
            legs = message["route"]
            trip = []
            for leg in legs:
                start_date = datetime.strptime(leg["started_at"], "%d/%m/%Y %H:%M:%S")
                end_date = start_date + timedelta(minutes=leg["duration"])
                trip.append(
                    {
                        "departure": leg["from"],
                        "destination": leg["to"],
                        "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
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
                    "start_date": datetime.fromtimestamp(
                        locations[0]["timestamp"], tz=timezone.utc
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "end_date": datetime.fromtimestamp(
                        locations[-1]["timestamp"], tz=timezone.utc
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                }
            ]

    def transform(self, message: dict) -> dict | None:
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
