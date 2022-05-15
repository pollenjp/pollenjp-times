# Standard Library
import datetime
import re
from logging import NullHandler
from logging import getLogger
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

# Third Party Library
from slack_bolt import App  # type: ignore # implicit reexport
from slack_sdk.web.slack_response import SlackResponse

# First Party Library
from pollenjp_times.types import ChannelModel
from pollenjp_times.types import ConversationsModel
from pollenjp_times.types import UserModel

logger = getLogger(__name__)
logger.addHandler(NullHandler())


def encode_dict2text(d: Dict[Any, Any], values_separator: str = "/", key_val_separator: str = ":") -> str:
    return f"{values_separator}".join([f"{key}{key_val_separator}{val}" for key, val in d.items()])


def decode_text2dict(text: str, values_separator: str = "/", key_val_separator: str = ":") -> Dict[str, str]:
    values: List[str] = text.split(values_separator)
    key_val_list: List[List[str]] = [single_value.split(key_val_separator) for single_value in values]
    return {key: val for (key, val) in key_val_list}


def extract_slack_urls(text: str) -> List[str]:
    """
    extract urls from slack message text

    example:
        Input: "へー\n<https://example.com>\n<https://example.com|https://example.com>"
        Output: ["https://example.com", "https://example.com"]
    """
    slack_urls: List[str] = re.findall(pattern=r"<.*>", string=text)
    urls: List[str] = []
    for slack_url in slack_urls:
        match = re.match(r"<(?P<url>.*)\|.*>", slack_url)
        if match is None:
            url = slack_url[1:-1]
        else:
            url = match.groupdict()["url"]
        urls.append(url)
    return urls


def convert_text_slack2discord(text: str) -> str:
    """
    extract urls from slack message text

    example:
        Input:
            "<@U123456>はー\n<#hoge-ch|C123456>ひー\nふー\n<https://example.com>へー\n<https://example.com|https://example.com>"
        Output:
            "`@ U123456`\n`#hoge-ch`\nへー\n https://example.com \n https://example.com "
    """

    # replace escape characters
    text = text.replace("&amp", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")

    # replace code block
    # slack format
    #   ```def function():\n    pass```
    # discord format
    #   ```\ndef function():\n    pass\n```
    text = text.replace("```", "\n```\n")

    text = re.sub(r"<@(\S+?)>", r"`@ \1`", text)  # user mention
    text = re.sub(r"<#(\S+?)\|(\S+?)>", r"`#\1`", text)  # channel mention
    text = re.sub(r"<(\S+?)\|(\S+?)>", r" [\2](\1) ", text)  # url with label
    text = re.sub(r"<(\S+?)>", r" \1 ", text)  # url

    return text


def get_channels(app: App) -> List[ChannelModel]:
    channels: List[ChannelModel] = []
    cursor = None
    while True:
        conversations_response: SlackResponse = app.client.conversations_list(cursor=cursor)
        conversations: ConversationsModel = ConversationsModel(
            **{
                key: conversations_response.get(key)  # type: ignore # Call to untyped function "get" in typed context
                for key in ["ok", "channels", "response_metadata"]
                if key in conversations_response
            },
        )
        if not conversations.ok:
            logger.warning(f"Failed to get conversations: {conversations=}")
            break
        channels += conversations.channels
        logger.debug(f"{channels=}")
        cursor = conversations.response_metadata.next_cursor
        if cursor == "":
            break
    return channels


def get_joined_channels(app: App) -> List[ChannelModel]:
    channels: List[ChannelModel] = []
    cursor = None
    while True:
        conversations_response: SlackResponse = app.client.users_conversations(cursor=cursor)
        conversations: ConversationsModel = ConversationsModel(
            **{
                key: conversations_response.get(key)  # type: ignore # Call to untyped function "get" in typed context
                for key in ["ok", "channels", "response_metadata"]
                if key in conversations_response
            },
        )
        if not conversations.ok:
            logger.warning(f"Failed to get conversations: {conversations=}")
            break
        channels += conversations.channels
        logger.debug(f"{channels=}")
        cursor = conversations.response_metadata.next_cursor
        if cursor == "":
            break
    return channels


def invite_existing_channels(app: App) -> None:

    channel: ChannelModel

    joined_channel_ids: Set[str] = set(channel.id for channel in get_joined_channels(app))

    for channel in get_channels(app):
        if channel.id in joined_channel_ids:
            continue
        if channel.is_archived:
            logger.info(f"{channel.id=}, {channel.name=} is archived.")
            continue
        logger.info(f"{channel.id=}, {channel.name=}")
        try:
            app.client.conversations_join(channel=channel.id)
        except Exception as e:
            logger.info(f"Failed to join to a channel: {channel.name}", exc_info=True)
            raise e


def convert_slack_ts_to_datetime(timestamp: Union[float, str]) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(int(float(timestamp)))


def get_user_data_from_user_id(app: App, user_id: Optional[str]) -> UserModel:
    """<https://api.slack.com/methods/users.info>

    Args:
        app (App): _description_
        user_id (Optional[str]): _description_

    Raises:
        RuntimeError: _description_
        RuntimeError: _description_

    Returns:
        UserModel: _description_
    """
    if user_id is None:
        raise RuntimeError("user_id is None")

    user_info: SlackResponse = app.client.users_info(user=user_id)
    user_data: Dict[str, Any] = user_info.get("user")  # type: ignore # Call to untyped function "get" in typed context
    if user_data is None:
        raise RuntimeError("user_data is None")
    logger.debug(f"{user_data=}")

    image_tag_names: List[str] = [
        "image_48",  # most common
        "image_24",
        "image_32",
        "image_72",
        "image_192",
        "image_512",
    ]
    user_icon_url: str = ""
    if (user_profile := user_data.get("profile")) is not None:
        for image_name in image_tag_names:
            if (url := user_profile.get(image_name)) is not None:
                user_icon_url = url
                break
    name_common: str = user_profile.get("display_name") or user_profile.get("real_name") or "No Name"
    user: UserModel = UserModel(
        id=user_id,
        name=user_data["name"],
        name_common=name_common or user_data["name"],
        is_bot=False,
        icon_url=user_icon_url,
    )
    logger.debug(f"{user=}")
    return user


def get_bot_data_from_bot_id(app: App, bot_id: Optional[str]) -> UserModel:
    if bot_id is None:
        raise RuntimeError("bot_id is None")

    bot_info: SlackResponse = app.client.bots_info(bot=bot_id)
    bot_data: Dict[str, Any] = bot_info.get("bot")  # type: ignore # Call to untyped function "get" in typed context
    if bot_data is None:
        raise RuntimeError("bot_data is None")

    image_tag_names: List[str] = [
        "image_48",  # most common
        "image_24",
        "image_32",
        "image_72",
        "image_192",
        "image_512",
    ]
    if (bot_icons := bot_data.get("icons")) is None:
        raise RuntimeError("failed to get bot_icons")
    icon_url: str = ""
    for image_name in image_tag_names:
        if (url := bot_icons.get(image_name)) is not None:
            icon_url = url
            break

    bot: UserModel = UserModel(
        id=bot_id,
        name=bot_data["name"],
        name_common=bot_data["name"],
        is_bot=True,
        icon_url=icon_url,
    )
    logger.debug(f"{bot=}")
    return bot


def get_channel_from_channel_id(app: App, channel_id: Optional[str]) -> ChannelModel:
    # get channel info
    if not channel_id:
        raise RuntimeError("channel_id is not found")
    channel_info: SlackResponse = app.client.conversations_info(channel=channel_id)
    channel: ChannelModel = ChannelModel(
        **channel_info.get("channel")  # type: ignore # Call to untyped function "get" in typed context
    )
    logger.info(f"{channel=}")
    return channel


def get_chat_permanent_link(app: App, channel_id: str, message_ts: str) -> str:
    # get message's permanent link
    permanent_link_info: SlackResponse = app.client.chat_getPermalink(channel=channel_id, message_ts=message_ts)
    if not permanent_link_info.get("ok"):  # type: ignore # Call to untyped function "get" in typed context
        raise RuntimeError("permanent_link_info is not found")
    permanent_link: Optional[str] = permanent_link_info.get("permalink")  # type: ignore
    if permanent_link is None:
        raise RuntimeError("permanent_link is not found")
    logger.info(f"{permanent_link=}")
    return permanent_link


def get_a_conversation(app: App, channel_id: str, ts: Optional[str] = None, is_reply: bool = False) -> Dict[str, Any]:
    # get conversation
    response: SlackResponse
    if not is_reply:
        response = app.client.conversations_history(
            channel=channel_id,
            inclusive=True,
            oldest=ts,
            limit=1,
        )
    else:
        if ts is None:
            raise RuntimeError("ts is None")
        response = app.client.conversations_replies(
            channel=channel_id,
            ts=ts,
            inclusive=True,
            oldest=ts,
            limit=1,
        )
    if response is None or len(response["messages"]) == 0:
        raise RuntimeError(f"conversation_res is empty: {response=}")
    logger.debug(f"{response.data=}")
    return response.data["messages"][0]  # type: ignore
