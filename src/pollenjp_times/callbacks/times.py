# Standard Library
from logging import NullHandler
from logging import getLogger
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Third Party Library
import discord
import requests
from pydantic import BaseModel
from slack_bolt.context.say.say import Say

# First Party Library
from pollenjp_times.types import SlackClientAppModel
from pollenjp_times.types import UserModel
from pollenjp_times.utils.slack import convert_text_slack2discord
from pollenjp_times.utils.slack import decode_text2dict
from pollenjp_times.utils.slack import encode_dict2text
from pollenjp_times.utils.slack import get_a_conversation
from pollenjp_times.utils.slack import get_user_data_from_user_id

# Local Library
from .base import SlackCallbackBase

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class ButtonValue(BaseModel):
    channel_id: str
    event_ts: Optional[str]
    message_ts: Optional[str]
    thread_ts: Optional[str] = None


class TimesCallback(SlackCallbackBase):
    def __init__(
        self,
        *args: Any,
        src_channel_id: str,
        src_user_id: str,
        tgt_clients: List[SlackClientAppModel],
        slack_webhook_clients: Optional[List[discord.webhook.sync.SyncWebhook]] = None,
        discord_webhook_clients: Optional[List[discord.webhook.sync.SyncWebhook]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.src_channel_id: str = src_channel_id
        self.src_user_id: str = src_user_id
        self.slack_clients: List[SlackClientAppModel] = tgt_clients
        self.slack_webhook_clients: List[str] = slack_webhook_clients or []
        self.discord_webhook_clients: List[discord.webhook.sync.SyncWebhook] = discord_webhook_clients or []

    def event_message(self, **kwargs: Any) -> None:
        event: Dict[str, Any] = kwargs["event"]
        message: Dict[str, Any] = kwargs["message"]
        say: Say = kwargs["say"]

        logger.info(f"{event=}")

        if not self.__is_target_message(event=event, message=message):
            return

        self.message_event_none(event, message, say)

    def __is_target_message(self, event: Dict[str, Any], message: Dict[str, Any]) -> bool:
        user_id: str = message["user"]
        if event["channel"] != self.src_channel_id or user_id != self.src_user_id:
            return False
        user: UserModel = get_user_data_from_user_id(app=self.slack_app, user_id=user_id)
        logger.info(f"{user=}")
        if user.is_bot:
            return False
        return True

    def message_event_none(self, event: Dict[str, Any], message: Dict[str, Any], say: Say) -> None:
        message_ts: Optional[str] = message.get("ts")
        if message_ts is None:
            raise RuntimeError(f"message_ts is not found: {message=}")

        button_value = ButtonValue(channel_id=self.src_channel_id, message_ts=message_ts, event_ts=message_ts)
        subtype: str
        if message.get("thread_ts") is not None:
            button_value.thread_ts = message["thread_ts"]

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
                            "value": encode_dict2text(button_value.dict(exclude_none=True)),
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
            user=message["user"],
        )

    def action_transfer_send_button(self, body: Dict[str, Any]) -> None:
        recieve_info: Dict[str, str] = decode_text2dict(body["actions"][0]["value"])
        button_value: ButtonValue = ButtonValue(**recieve_info)

        if self.src_channel_id != button_value.channel_id:
            return

        message: Dict[str, Any] = get_a_conversation(
            app=self.slack_app,
            channel_id=button_value.channel_id,
            ts=button_value.message_ts,
            is_reply=True if button_value.thread_ts is not None else False,
        )
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

        for webhook_url in self.slack_webhook_clients:
            requests.post(
                webhook_url,
                headers={
                    "Content-Type": "application/json",
                },
                json={
                    "text": message_txt,
                },
            )

        content_list: List[str] = [
            f"{convert_text_slack2discord(message_txt)}",
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
