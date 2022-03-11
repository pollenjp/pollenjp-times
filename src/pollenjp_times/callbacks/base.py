# Standard Library
from logging import getLogger
from typing import Any
from typing import Dict
from typing import List

# Third Party Library
from slack_bolt import App  # type: ignore

logger = getLogger(__name__)


class SlackCallbackBase:
    def __init__(self, *args: Any, slack_app: App, **kwargs: Any) -> None:
        self.slack_app: App = slack_app


class Callbacks:
    def __init__(self, callbacks: List[SlackCallbackBase]) -> None:
        self.callbacks = callbacks

    def _notify(self, function_name: str, /, **kwargs: Any) -> None:
        for c in self.callbacks:
            try:
                func = getattr(c, function_name)
            except AttributeError as e:
                logger.debug(f"{e=}")
            else:
                func(**kwargs)

    def event_message(self, **kwargs: Any) -> None:
        self._notify("event_message", **kwargs)

    def event_channel_created(self, **kwargs: Dict[str, Any]) -> None:
        self._notify("event_channel_created", **kwargs)

    def event_channel_rename(self, **kwargs: Dict[str, Any]) -> None:
        self._notify("event_channel_rename", **kwargs)

    def event_channel_archive(self, **kwargs: Dict[str, Any]) -> None:
        self._notify("event_channel_archive", **kwargs)

    def event_channel_unarchive(self, **kwargs: Dict[str, Any]) -> None:
        self._notify("event_channel_unarchive", **kwargs)

    def event_channel_deleted(self, **kwargs: Dict[str, Any]) -> None:
        self._notify("event_channel_deleted", **kwargs)

    def event_reaction_added(self, **kwargs: Dict[str, Any]) -> None:
        self._notify("event_reaction_added", **kwargs)

    def event_reaction_removed(self, **kwargs: Dict[str, Any]) -> None:
        self._notify("event_reaction_removed", **kwargs)
