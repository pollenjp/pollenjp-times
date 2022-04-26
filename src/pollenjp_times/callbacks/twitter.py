# Standard Library
from logging import getLogger
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

# Third Party Library
import discord
from slack_bolt.context.say.say import Say

# First Party Library
from pollenjp_times.types import SlackClientAppModel
from pollenjp_times.utils.slack import convert_slack_urls_to_discord

# Local Library
from .base import SlackCallbackBase

logger = getLogger(__name__)


class TwitterCallback(SlackCallbackBase):
    def __init__(
        self,
        *args: Any,
        src_channel_id: str,
        tgt_clients: List[SlackClientAppModel],
        discord_webhook_clients: Optional[List[discord.webhook.sync.SyncWebhook]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.src_channel_id: str = src_channel_id
        self.slack_clients: List[SlackClientAppModel] = tgt_clients
        self.discord_webhook_clients: List[discord.webhook.sync.SyncWebhook] = discord_webhook_clients or []

    def event_message(self, **kwargs: Any) -> None:
        event: Dict[str, Any] = kwargs["event"]
        message: Dict[str, Any] = kwargs["message"]
        say: Say = kwargs["say"]

        subtype = message.get("subtype", None)

        logger.info(f"{event=}")

        if subtype == "bot_message":  # if a bot
            self.message_event_bot(event, message, say)
        else:
            logger.warning(f"event_message's subtype is not 'bot_message': {subtype=}")

    def message_event_bot(self, event: Dict[str, Any], message: Dict[str, Any], say: Say) -> None:
        if event["channel"] != self.src_channel_id:
            return

        message_txt: str = ""
        if (txt := message.get("text", None)) is not None:
            message_txt += txt
        attachments: Optional[Sequence[Union[Dict[str, Any]]]] = message.get("attachments", None)

        client_model: SlackClientAppModel
        for client_model in self.slack_clients:
            client_model.app.client.chat_postMessage(
                channel=client_model.tgt_channel_id,
                text=message_txt,
                # as_user=False,
                attachments=attachments,
                username="pollenJP",
                icon_url="https://i.gyazo.com/4d3a544918c1bebb5c02f37c7789f765.jpg",
            )

        # replace escape characters
        message_txt = message_txt.replace("&amp", "&")
        message_txt = message_txt.replace("&lt;", "<")
        message_txt = message_txt.replace("&gt;", ">")

        content_list: List[str] = [
            f"{convert_slack_urls_to_discord(message_txt)}",
        ]

        # get 0th attachment's text
        if attachments is not None and len(attachments) > 0:
            content_list += [
                f"{convert_slack_urls_to_discord(attachments[0]['text'])}",
            ]

        logger.info(f"{content_list}")
        discord_content: str = "\n".join(content_list)

        discord_webhook_app: discord.webhook.sync.SyncWebhook
        for discord_webhook_app in self.discord_webhook_clients:
            discord_webhook_app.send(
                content=discord_content if len(discord_content) > 0 else "No text",
                username="pollenJP",
                avatar_url="https://i.gyazo.com/4d3a544918c1bebb5c02f37c7789f765.jpg",
            )
