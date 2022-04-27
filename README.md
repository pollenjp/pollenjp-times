# pollenjp-times: "pollenJP's Times System"

## ToC

<!-- TOC -->

- [ToC](#toc)
- [How to use](#how-to-use)
- [How to run](#how-to-run)
  - [config](#config)
  - [systemd](#systemd)
    - [TimesCallback](#timescallback)
    - [TwitterCallback](#twittercallback)

<!-- /TOC -->

## How to use

ホストに指定した Slack 上でつぶやくと以下のように他の Slack / Discord のチャンネルにも送信するかを聞かれる.

<a href="https://gyazo.com/af83d5984bfd56d6fef956aaa2d222c0">
    <img src="https://i.gyazo.com/af83d5984bfd56d6fef956aaa2d222c0.png" alt="Image from Gyazo" width="296"/>
</a>

| Button | Description |
|:--|:--|
| Send | 各所に送信 & Botメッセージ削除 |
| No| Botメッセージ削除 |

## How to run

### config

See `config/sample.yaml`

### systemd

```sh
poetry run python3 generate_systemd_conf.py \
    --name pollenjp_times_bot \
    --config config/sample.yaml
```

#### TimesCallback

- Create `config/times.yaml`.
- Run the command as below.

```sh
poetry run python3 generate_systemd_conf.py \
    --name pollenjp_times_bot_times \
    --config config/times.yaml
systemctl --user start pollenjp_times_bot_times.service
```

#### TwitterCallback

Slack Twitter Integration が設定されたチャンネルを指定し流れてきたツイートをすべて転送する.
送信者の判定は bot しか判定していないため Twitter Integration App 以外の Bot メッセージにも反応してしまう.

- Create `config/twitter.yaml`.
- Run the command as below.

```sh
poetry run python3 generate_systemd_conf.py \
    --name pollenjp_times_bot_twitter \
    --config config/twitter.yaml
systemctl --user start pollenjp_times_bot_twitter.service
```
