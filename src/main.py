# Standard Library
import argparse
import typing as t
from dataclasses import dataclass
from dataclasses import field
from logging import NullHandler
from logging import getLogger
from logging.config import dictConfig
from pathlib import Path

# Third Party Library
import discord
import yaml
from omegaconf import OmegaConf
from slack_bolt.adapter.socket_mode.builtin import SocketModeHandler
from slack_bolt.app.app import App
from slack_bolt.context.say.say import Say
from slack_sdk import WebhookClient  # type: ignore # implicit reexport disabled

# First Party Library
from pollenjp_times.callbacks import TimesCallback
from pollenjp_times.callbacks import TwitterCallback
from pollenjp_times.callbacks.base import Callbacks
from pollenjp_times.callbacks.base import SlackCallbackBase
from pollenjp_times.types import SlackClientAppModel

logger = getLogger(__name__)
logger.addHandler(NullHandler())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="pollenjp times arguements")
    parser.add_argument(
        "--config",
        type=lambda x: Path(x).expanduser(),
        default=Path(__file__).parents[1] / "config" / "main.yaml",
        help="config file path",
    )
    return parser.parse_args()


def load_logging_conf(filepath: Path) -> None:
    with open(filepath, mode="rt") as f:
        dictConfig(yaml.safe_load(f))


@dataclass
class SlackHost:
    bot_user_oauth_token: str
    app_level_token: str


@dataclass
class TimesCallbackSlackClientsConfig:
    bot_user_oauth_token: str
    channel_id: str


@dataclass
class CallbackClientsConfig:
    slack: t.List[TimesCallbackSlackClientsConfig] = field(default_factory=list)
    discord: t.List[str] = field(default_factory=list)  # webhook url


@dataclass
class TimesCallbackConfig:
    host_channel_id: str
    host_user_id: str
    clients: CallbackClientsConfig


@dataclass
class TwitterCallbackConfig:
    host_channel_id: str
    host_user_id: str
    clients: CallbackClientsConfig


@dataclass
class TimesAppConfig:
    host: SlackHost
    times_callback: t.List[TimesCallbackConfig] = field(default_factory=list)
    twitter_callback: t.List[TwitterCallbackConfig] = field(default_factory=list)


@dataclass
class ConfigModel:
    times_app: TimesAppConfig


def main() -> None:
    args: argparse.Namespace = parse_args()

    load_logging_conf(Path(__file__).parents[1] / "config" / "logging.conf.yaml")

    conf: ConfigModel = t.cast(
        ConfigModel,
        OmegaConf.merge(
            OmegaConf.structured(ConfigModel),
            OmegaConf.load(args.config),
        ),
    )
    logger.info(f"{conf=}")

    times_app_host = App(token=conf.times_app.host.bot_user_oauth_token)

    callback_list: t.List[SlackCallbackBase] = []
    callback_list += [
        TimesCallback(
            src_channel_id=channels_conf.host_channel_id,
            src_user_id=channels_conf.host_user_id,
            tgt_clients=[
                SlackClientAppModel(
                    app=App(token=slack_clients_conf.bot_user_oauth_token),
                    tgt_channel_id=slack_clients_conf.channel_id,
                )
                for slack_clients_conf in channels_conf.clients.slack
            ],
            discord_webhook_clients=[
                discord.webhook.sync.SyncWebhook.from_url(discord_webhook_url)
                for discord_webhook_url in channels_conf.clients.discord
            ],
            slack_app=times_app_host,
        )
        for channels_conf in conf.times_app.times_callback
    ]
    callback_list += [
        TwitterCallback(
            src_channel_id=channels_conf.host_channel_id,
            tgt_clients=[
                SlackClientAppModel(
                    app=App(token=slack_clients_conf.bot_user_oauth_token),
                    tgt_channel_id=slack_clients_conf.channel_id,
                )
                for slack_clients_conf in channels_conf.clients.slack
            ],
            discord_webhook_clients=[
                discord.webhook.sync.SyncWebhook.from_url(discord_webhook_url)
                for discord_webhook_url in channels_conf.clients.discord
            ],
            slack_app=times_app_host,
        )
        for channels_conf in conf.times_app.twitter_callback
    ]
    callbacks: Callbacks = Callbacks(callback_list)

    @times_app_host.action("action_transfer_send_button")
    def action_transfer_send_button(ack: t.Callable[[], None], body: t.Dict[str, t.Any]) -> None:
        ack()
        logger.info(f"{body=}")
        callbacks.action_transfer_send_button(body=body)
        client: WebhookClient = WebhookClient(url=body["response_url"])
        client.send(delete_original=True)

    @times_app_host.action("action_delete_original")
    def action_delete_original(ack: t.Callable[[], None], body: t.Dict[str, t.Any]) -> None:
        ack()
        logger.info(f"{body=}")
        client: WebhookClient = WebhookClient(url=body["response_url"])
        client.send(delete_original=True)

    @times_app_host.event("message")
    def event_message(event: t.Dict[str, t.Any], message: t.Dict[str, t.Any], say: Say) -> None:
        logger.info(f"{event=}")
        callbacks.event_message(
            event=event,
            message=message,
            say=say,
        )

    SocketModeHandler(times_app_host, conf.times_app.host.app_level_token).start()  # type: ignore


if __name__ == "__main__":
    main()
