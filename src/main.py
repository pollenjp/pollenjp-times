# Standard Library
import argparse
from logging import getLogger
from logging.config import dictConfig
from pathlib import Path
from typing import Any
from typing import Dict

# Third Party Library
import discord
import yaml
from omegaconf import OmegaConf
from slack_bolt.adapter.socket_mode.builtin import SocketModeHandler
from slack_bolt.app.app import App
from slack_bolt.context.say.say import Say
from slack_sdk import WebhookClient

# First Party Library
from pollenjp_times.callbacks import TimesCallback
from pollenjp_times.callbacks import TwitterCallback
from pollenjp_times.callbacks.base import Callbacks
from pollenjp_times.types import SlackClientAppModel

filepath = Path(__file__).parents[1] / "config" / "logging.conf.yaml"
with open(file=str(filepath), mode="rt") as f:
    config_dict = yaml.safe_load(f)
dictConfig(config=config_dict)
del filepath, config_dict

logger = getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="pollenjp times arguements")
    parser.add_argument(
        "--config",
        type=lambda x: Path(x).expanduser(),
        default=Path(__file__).parents[1] / "config" / "main.yaml",
        help="config file path",
    )
    return parser.parse_args()


def main():
    args: argparse.Namespace = parse_args()

    conf = OmegaConf.load(args.config)
    logger.info(f"{conf=}")

    times_app_host = App(token=conf.times_app.host.bot_user_oauth_token)

    callbacks: Callbacks = Callbacks(
        [
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
            for channels_conf in conf.times_app.times_callback.channels
        ]
        + [
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
            for channels_conf in conf.times_app.twitter_callback.channels
        ]
    )

    @times_app_host.action("action_transfer_send_button")
    def action_transfer_send_button(ack, body):
        ack()
        logger.info(f"{body=}")
        callbacks.action_transfer_send_button(body=body)
        client: WebhookClient = WebhookClient(url=body["response_url"])
        client.send(delete_original=True)

    @times_app_host.action("action_delete_original")
    def action_delete_original(ack, body):
        ack()
        logger.info(f"{body=}")
        client: WebhookClient = WebhookClient(url=body["response_url"])
        client.send(delete_original=True)

    @times_app_host.event("message")
    def event_message(event: Dict[str, Any], message: Dict[str, Any], say: Say) -> None:
        callbacks.event_message(
            event=event,
            message=message,
            say=say,
        )

    SocketModeHandler(times_app_host, conf.times_app.host.app_level_token).start()  # type: ignore


if __name__ == "__main__":
    main()
