#!/usr/bin/env sh

# Write the container's environmental variables somewhere so we can source them
# from the cronjobs (we need the passwords, after all).
set -o allexport
env > /root/env.env
set +o allexport
echo "Starting cron..."
touch /tmp/log
cron
echo "Running tail to capture output..."
tail -f /tmp/log
