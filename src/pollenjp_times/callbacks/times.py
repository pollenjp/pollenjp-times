# Standard Library
from logging import getLogger
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Third Party Library
import discord
from slack_bolt.context.say.say import Say

# First Party Library
from pollenjp_times.types import SlackClientAppModel

# Local Library
from .base import SlackCallbackBase

logger = getLogger(__name__)


class TimesCallback(SlackCallbackBase):
    def __init__(
        self,
        *args: Any,
        src_channel_id: str,
        src_user_id: str,
        tgt_clients: List[SlackClientAppModel],
        discord_webhook_clients: Optional[List[discord.webhook.sync.SyncWebhook]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.src_channel_id: str = src_channel_id
        self.src_user_id: str = src_user_id
        self.slack_clients: List[SlackClientAppModel] = tgt_clients
        self.discord_webhook_clients: List[discord.webhook.sync.SyncWebhook] = discord_webhook_clients or []

    def event_message(self, **kwargs: Any) -> None:
        event: Dict[str, Any] = kwargs["event"]
        message: Dict[str, Any] = kwargs["message"]
        say: Say = kwargs["say"]

        subtype = message.get("subtype", None)

        logger.info(f"{event=}")

        if subtype is None:  # if a person
            self.message_event_none(event, message, say)
        else:
            logger.warning(f"event_message's subtype is not None: {subtype=}")

    def message_event_none(self, event: Dict[str, Any], message: Dict[str, Any], say: Say) -> None:
        if event["channel"] != self.src_channel_id or event["user"] != self.src_user_id:
            return

        message_ts: Optional[str] = message.get("ts")
        if message_ts is None:
            raise RuntimeError(f"message_ts is not found: {message=}")

        self.slack_app.client.chat_postEphemeral(
            channel=self.src_channel_id,
            text="test message for postEphemeral",
            blocks=[
                {
                    "type": "actions",
                    "block_id": "actionblock789",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Send"},
                            "style": "primary",
                            "value": f"{self.src_channel_id}/{message_ts}",  # '/' is separater
                            "action_id": "transfer_button_send",
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "No"},
                            "style": "danger",
                            "value": "delete",
                            "action_id": "transfer_button_delete",
                        },
                    ],
                }
            ],
            user=event["user"],
        )
