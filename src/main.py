# Standard Library
from logging import getLogger
from logging.config import dictConfig
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

# Third Party Library
import yaml
from omegaconf import OmegaConf
from slack_bolt.adapter.socket_mode.builtin import SocketModeHandler
from slack_bolt.app.app import App
from slack_bolt.context.say.say import Say

# First Party Library
from pollenjp_times.callbacks.base import Callbacks
from pollenjp_times.callbacks.times import TimesCallback
from pollenjp_times.types import SlackClientAppModel

filepath = Path(__file__).parents[1] / "config" / "logging.conf.yaml"
with open(file=str(filepath), mode="rt") as f:
    config_dict = yaml.safe_load(f)
dictConfig(config=config_dict)
del filepath, config_dict

logger = getLogger(__name__)

conf = OmegaConf.load(Path(__file__).parents[1] / "config" / "main.yaml")


times_app_host = App(token=conf.times_app.host.bot_user_oauth_token)
times_app_clients: List[SlackClientAppModel] = [
    SlackClientAppModel(
        app=App(token=client_conf.bot_user_oauth_token),
        tgt_channel_id=client_conf.channel_id,
    )
    for client_conf in conf.times_app.clients.slack
]

callbacks: Callbacks = Callbacks(
    [
        TimesCallback(
            src_channel_id=conf.times_app.host.channel_id,
            tgt_clients=times_app_clients,
            slack_app=times_app_host,
        ),
    ]
)


@times_app_host.event("message")
def event_message(event: Dict[str, Any], message: Dict[str, Any], say: Say) -> None:
    print("hello")
    callbacks.event_message(
        event=event,
        message=message,
        say=say,
    )


if __name__ == "__main__":
    logger.info(f"{conf=}")
    SocketModeHandler(times_app_host, conf.times_app.host.app_level_token).start()  # type: ignore
