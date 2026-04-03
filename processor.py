import json
from config import Config
import logging
from itertools import chain

logger = logging.getLogger(__name__)


class MessageProcessor:
    def __init__(self):
        self.config = Config()
        self.required_keys = list(self.config.mandatory_keys)
        self.required_keys.extend(list(chain.from_iterable(self.config.other_keys)))

    def validate(self, message: dict) -> dict | None:
        try:
            assert message.get("Body"), (
                f"Message body not found for the message ID: {message['MessageId']}"
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
            logger.error(
                f"Invalid message body for the message ID: {message.get('MessageId')}: {e}"
            )
            return None
