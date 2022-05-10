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
from pollenjp_times.utils.slack import convert_slack_urls_to_discord
from pollenjp_times.utils.slack import get_a_conversation

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

        logger.info(f"{event=}")

        if self.__should_be_filtered(event=event, message=message):
            return

        self.message_event_none(event, message, say)

    def __should_be_filtered(self, event: Dict[str, Any], message: Dict[str, Any]) -> bool:
        if message.get("subtype") is not None:  # not a person
            return True
        if event["channel"] != self.src_channel_id or event["user"] != self.src_user_id:
            return True
        return False

    def message_event_none(self, event: Dict[str, Any], message: Dict[str, Any], say: Say) -> None:
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
                            "action_id": "action_transfer_send_button",
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "No"},
                            "style": "danger",
                            "value": "delete",
                            "action_id": "action_delete_original",
                        },
                    ],
                }
            ],
            user=event["user"],
        )

    def action_transfer_send_button(self, body: Dict[str, Any]) -> None:
        channel_id: str
        message_ts: str
        channel_id, message_ts = body["actions"][0]["value"].split("/")

        if self.src_channel_id != channel_id:
            return

        message: Dict[str, Any] = get_a_conversation(app=self.slack_app, channel_id=channel_id, ts=message_ts)
        logger.info(f"{message=}")

        message_txt: str = ""
        if (txt := message.get("text", None)) is not None:
            message_txt += txt

        client_model: SlackClientAppModel
        for client_model in self.slack_clients:
            client_model.app.client.chat_postMessage(
                channel=client_model.tgt_channel_id,
                text=message_txt,
                # as_user=False,
                # attachments=message.get("attachments", None),
                username="pollenJP",
                icon_url="https://i.gyazo.com/4d3a544918c1bebb5c02f37c7789f765.jpg",
            )

        content_list: List[str] = [
            f"{convert_slack_urls_to_discord(message_txt)}",
        ]

        logger.info(f"{content_list}")

        discord_webhook_app: discord.webhook.sync.SyncWebhook
        for discord_webhook_app in self.discord_webhook_clients:
            discord_webhook_app.send(
                content="\n".join(content_list),
                username="pollenJP",
                avatar_url="https://i.gyazo.com/4d3a544918c1bebb5c02f37c7789f765.jpg",
            )

        return
