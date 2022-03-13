# pollenjp-times

## config

`config/main.yaml`

```yaml
times_app:
  host:  # slack
    bot_user_oauth_token: "xoxb-***"
    app_level_token: "xapp-***"
  channels:
    -
      host_channel_id: "CXXX"  # times
      clients:
        slack:
          -  # Hoge workspace
            bot_user_oauth_token: "xoxb-***"
            channel_id: "CXXX"  # random
          -  # Fuga workspace
            bot_user_oauth_token: "xoxb-***"
            channel_id: "CXXX"
        discord: []
    -
      host_channel_id: "CYYY"  # times2
      clients:
        slack:
          -  # Hoge workspace
            bot_user_oauth_token: "xoxb-***"
            channel_id: "CXXX"  # random
          -  # Fuga workspace
            bot_user_oauth_token: "xoxb-***"
            channel_id: "CXXX"
        discord: []
```
