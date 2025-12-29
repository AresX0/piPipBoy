#!/usr/bin/env bash
set -euo pipefail

SERVICE_FILE=/etc/systemd/system/piboy.service
WORKDIR=/home/pi/pipboy
EXECSTART="/usr/bin/python3 -u ${WORKDIR}/src/pipboy/main.py"

cat <<EOF | sudo tee $SERVICE_FILE >/dev/null
[Unit]
Description=piPipBoy service
After=network.target

[Service]
Type=simple
WorkingDirectory=${WORKDIR}
ExecStart=${EXECSTART}
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable piboy.service
sudo systemctl start piboy.service

echo "piboy.service installed and started (WorkingDirectory=${WORKDIR})"
