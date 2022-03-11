# Third Party Library
from pydantic import BaseModel
from slack_bolt import App  # type: ignore


class SlackClientAppModel(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    app: App
    tgt_channel_id: str
