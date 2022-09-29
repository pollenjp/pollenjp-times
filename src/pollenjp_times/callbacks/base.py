# Standard Library
import abc
import traceback
import typing as t
from logging import NullHandler
from logging import getLogger

# Third Party Library
import discord
from slack_bolt import App

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class Sender:
    @abc.abstractmethod
    def send(self, text: str) -> None:
        ...


class DiscordWebhookSender(Sender):
    def __init__(self, webhook_url: str) -> None:
        self.app: discord.webhook.sync.SyncWebhook = discord.webhook.sync.SyncWebhook.from_url(webhook_url)

    def send(self, text: str) -> None:
        self.app.send(content=text)


class SlackCallbackBase:
    def __init__(self, *args: t.Any, slack_app: App, **kwargs: t.Any) -> None:
        self.slack_app: App = slack_app
        self.bot_id: str = t.cast(str, self.slack_app.client.auth_test()["user_id"])

    def event_message(self, **kwargs: t.Any) -> None:
        pass

    def event_channel_created(self, **kwargs: t.Any) -> None:
        pass

    def event_channel_rename(self, **kwargs: t.Any) -> None:
        pass

    def event_channel_archive(self, **kwargs: t.Any) -> None:
        pass

    def event_channel_unarchive(self, **kwargs: t.Any) -> None:
        pass

    def event_channel_deleted(self, **kwargs: t.Any) -> None:
        pass

    def event_reaction_added(self, **kwargs: t.Any) -> None:
        pass

    def event_reaction_removed(self, **kwargs: t.Any) -> None:
        pass

    def action_transfer_send_button(self, body: t.Dict[str, t.Any]) -> None:
        pass


class Callbacks:
    def __init__(self, callbacks: t.List[SlackCallbackBase], error_sender: t.Optional[Sender] = None) -> None:
        self.callbacks = callbacks
        self.error_sender = error_sender

    def _notify(self, function_name: str, /, **kwargs: t.Any) -> None:
        for c in self.callbacks:
            try:
                func = getattr(c, function_name)
            except Exception as e:
                logger.error(f"{e}", exc_info=True)
                if self.error_sender is not None:
                    err_msg_list: t.List[str] = [
                        r"```",
                        f"{traceback.format_exc()}",
                        f"{e}",
                        r"```",
                    ]
                    err_msg = "\n".join(err_msg_list)
                    self.error_sender.send(err_msg)
                raise e

            else:
                func(**kwargs)

    def event_message(self, **kwargs: t.Any) -> None:
        self._notify("event_message", **kwargs)

    def event_channel_created(self, **kwargs: t.Any) -> None:
        self._notify("event_channel_created", **kwargs)

    def event_channel_rename(self, **kwargs: t.Any) -> None:
        self._notify("event_channel_rename", **kwargs)

    def event_channel_archive(self, **kwargs: t.Any) -> None:
        self._notify("event_channel_archive", **kwargs)

    def event_channel_unarchive(self, **kwargs: t.Any) -> None:
        self._notify("event_channel_unarchive", **kwargs)

    def event_channel_deleted(self, **kwargs: t.Any) -> None:
        self._notify("event_channel_deleted", **kwargs)

    def event_reaction_added(self, **kwargs: t.Any) -> None:
        self._notify("event_reaction_added", **kwargs)

    def event_reaction_removed(self, **kwargs: t.Any) -> None:
        self._notify("event_reaction_removed", **kwargs)

    def action_transfer_send_button(self, **kwargs: t.Any) -> None:
        self._notify("action_transfer_send_button", **kwargs)
