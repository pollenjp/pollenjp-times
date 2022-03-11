# pollenjp-times

## config

`config/main.yaml`

```yaml
times_app:
  host:  # slack
    bot_user_oauth_token: "xoxb-***"
    app_level_token: "xapp-***"
    channel_id: "CXXX"
  clients:
    slack:
      -
        bot_user_oauth_token: "xoxb-***"
        channel_id: "CYYY"
      -
        bot_user_oauth_token: "xoxb-***"
        channel_id: "CZZZ"
    discord: []
```
