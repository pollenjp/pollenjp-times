# pollenjp-times: "pollenJP's Times System"

## ToC

<!-- TOC -->

- [ToC](#toc)
- [How to use](#how-to-use)
- [How to run](#how-to-run)
  - [requirements](#requirements)
  - [config](#config)

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

### requirements

```sh
poetry install
```

### config

- `APP_CONFIG` : json format string
  - `yq '.' "config/sample.yml" > "sample.json"`
- `LOGGING_CONFIG` : json format string

```sh
PYTHONPATH='src' poetry run python src/main.py
```
