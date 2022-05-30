# Standard Library
import re
from logging import NullHandler
from logging import getLogger
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Sequence
from typing import Union

# Third Party Library
import discord
from discord.embeds import Embed
from discord.embeds import EmptyEmbed
from slack_bolt.context.say.say import Say

# First Party Library
from pollenjp_times.types import MessageAttachmentModel
from pollenjp_times.types import SlackClientAppModel
from pollenjp_times.utils.slack import convert_slack_ts_to_datetime
from pollenjp_times.utils.slack import convert_text_slack2discord
from pollenjp_times.utils.slack import get_channel_from_channel_id

# Local Library
from .base import SlackCallbackBase

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class TwitterCallback(SlackCallbackBase):
    def __init__(
        self,
        *args: Any,
        src_channel_id: str,
        tgt_clients: Optional[List[SlackClientAppModel]] = None,
        discord_webhook_clients: Optional[List[discord.webhook.sync.SyncWebhook]] = None,
        filter_keyword: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.src_channel_id: str = src_channel_id
        self.slack_clients: List[SlackClientAppModel] = tgt_clients or []
        self.discord_webhook_clients: List[discord.webhook.sync.SyncWebhook] = discord_webhook_clients or []
        self.filter_pattern = (
            re.compile(
                f"{filter_keyword}",
                flags=re.IGNORECASE,
            )
            if filter_keyword is not None
            else None
        )

    def event_message(self, **kwargs: Any) -> None:
        event: Dict[str, Any] = kwargs["event"]
        message: Dict[str, Any] = kwargs["message"]
        say: Say = kwargs["say"]

        logger.info(f"{event=}")

        self._event_message(event, message, say)

    def _event_message(self, event: Dict[str, Any], message: Dict[str, Any], say: Say) -> None:
        if event["channel"] != self.src_channel_id:
            return

        content_list: List[str] = []
        if (message_txt := message.get("text", None)) is not None:
            content_list.append(convert_text_slack2discord(message_txt))

        attachments: Optional[Sequence[Union[Dict[str, Any]]]] = message.get("attachments", None)
        if attachments:
            for attachment in attachments:
                ms_attachment = MessageAttachmentModel(**attachment)
                if len(ms_attachment.text) > 0:
                    content_list.append(f"{ convert_text_slack2discord(ms_attachment.text).strip() }")
                if len(ms_attachment.pretext) > 0:
                    content_list.append(f"{ convert_text_slack2discord(ms_attachment.pretext).strip() }")

        if self.filter_pattern is not None:
            include_keyword: bool = False
            for txt in content_list:
                if self.filter_pattern.match(txt) is not None:
                    include_keyword = True
                    break
            if not include_keyword:
                return

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

        for discord_webhook_app in self.discord_webhook_clients:
            discord_webhook_app.send(content="\n".join(content_list))

        channel = get_channel_from_channel_id(self.slack_app, message.get("channel"))

        embeds: List[Embed] = []
        if attachments:
            for attachment in attachments:
                ms_attachment = MessageAttachmentModel(**attachment)
                if ms_attachment.ts is not None:
                    embed = Embed(
                        description=ms_attachment.text, timestamp=convert_slack_ts_to_datetime(ms_attachment.ts)
                    )
                else:
                    embed = Embed(description=ms_attachment.text)
                embed.set_author(
                    name=ms_attachment.author_name if ms_attachment.author_name is not None else EmptyEmbed,
                    url=f"{ms_attachment.author_link}" if ms_attachment.author_link is not None else EmptyEmbed,
                    icon_url=ms_attachment.author_icon if ms_attachment.author_icon is not None else EmptyEmbed,
                )
                embed.set_footer(
                    text=f"{channel.name}",
                    # icon_url=,
                )
                if ms_attachment.image_url is not None:
                    embed.set_image(url=ms_attachment.image_url)
                embeds.append(embed)

            for discord_webhook_app in self.discord_webhook_clients:
                discord_webhook_app.send(content="attachment", embeds=embeds)
