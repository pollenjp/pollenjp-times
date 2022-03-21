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
from pollenjp_times.utils import extract_slack_urls

# Local Library
from .base import SlackCallbackBase

logger = getLogger(__name__)


class TimesCallback(SlackCallbackBase):
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

        if subtype is None or subtype == "bot_message":
            self.message_event_none(event, message, say)
        else:
            logger.warning(f"event_message's subtype is not None: {subtype=}")

    def message_event_none(self, event: Dict[str, Any], message: Dict[str, Any], say: Say) -> None:
        if event["channel"] != self.src_channel_id:
            return

        message_txt: str = ""
        if (txt := message.get("text", None)) is not None:
            message_txt += txt
        attachments: Optional[Sequence[Union[Dict]]] = message.get("attachments", None)

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

        # replace code block
        # slack format
        #   ```def function():\n    pass```
        # discord format
        #   ```\ndef function():\n    pass\n```
        message_txt = message_txt.replace("```", "\n```\n```\n")

        content_list: List[str] = [
            r"```",
            f"{message_txt}",
            r"```",
        ]
        content_list += extract_slack_urls(text=message_txt)

        logger.info(f"{content_list}")

        discord_webhook_app: discord.webhook.sync.SyncWebhook
        for discord_webhook_app in self.discord_webhook_clients:
            discord_webhook_app.send(
                content="\n".join(content_list),
                username="pollenJP",
                avatar_url="https://i.gyazo.com/4d3a544918c1bebb5c02f37c7789f765.jpg",
            )
