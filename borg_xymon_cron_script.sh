#!/bin/bash
set -e

# Get config
source /usr/local/etc/borg.sh
export BORG_REPO="${BORG_REPO}"
export BORG_PASSPHRASE="${BORG_PASSPHRASE}"

borg list --json --format '{end}' > /var/log/local_backups/borg_backup.json



