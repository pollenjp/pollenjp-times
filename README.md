# pollenjp-times

## config

See `config/sample.yaml`

## systemd

```sh
poetry run python3 generate_systemd_conf.py \
    --name pollenjp_times_bot \
    --config config/sample.yaml
```

### times

- Create `config/times.yaml`.
- Run the command as below.

```sh
poetry run python3 generate_systemd_conf.py \
    --name pollenjp_times_bot_times \
    --config config/times.yaml
systemctl --user start pollenjp_times_bot_times.service
```

### twitter

- Create `config/twitter.yaml`.
- Run the command as below.

```sh
poetry run python3 generate_systemd_conf.py \
    --name pollenjp_times_bot_twitter \
    --config config/twitter.yaml
systemctl --user start pollenjp_times_bot_twitter.service
```
