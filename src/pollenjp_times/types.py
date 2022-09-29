# Standard Library
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

# Third Party Library
from pydantic import BaseModel
from slack_bolt import App


class SlackClientAppModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    app: App
    tgt_channel_id: str


class UserModel(BaseModel):
    id: str
    name: str
    name_common: str  # real name, display name などから一番適切なものを格納
    icon_url: str
    is_bot: bool = False


class ChannelModel(BaseModel):
    id: str
    # is_channel: bool
    name: str
    # name_normalized: str
    # created: int
    # creator: str
    # is_shared: bool
    # is_org_shared: bool
    is_archived: bool = False


class ResponseMetadataModel(BaseModel):
    next_cursor: str = ""


class ConversationsModel(BaseModel):
    ok: bool
    response_metadata: ResponseMetadataModel
    channels: List[ChannelModel] = []


class MessageBlockModel(BaseModel):
    type: str
    block_id: str
    elements: List[Dict[str, Any]]


class MessageAttachmentModel(BaseModel):
    from_url: Optional[str] = None
    image_url: Optional[str] = None
    fallback: str = ""
    text: str = ""
    pretext: str = ""
    ts: Optional[float] = None
    author_icon: Optional[str] = None
    author_name: Optional[str] = None
    author_link: Optional[str] = None
