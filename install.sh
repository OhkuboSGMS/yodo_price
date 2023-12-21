#!/usr/bin/env bash

# systemdで動作するようにセットアップ
# venvを作成した状態で実行する

chmod +x main.py bot.py
sudo cp systemd/yodo_price_bot.service  /etc/systemd/system/
sudo cp systemd/yodo_price.service  /etc/systemd/system/
sudo systemctl start yodo_price_bot.service
sudo systemctl start yodo_price.service
sudo systemctl enable yodo_price.service
sudo systemctl enable yodo_price_bot.service
