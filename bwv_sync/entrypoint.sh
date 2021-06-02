#!/usr/bin/env sh

# Write the container's environmental variables somewhere so we can source them
# from the cronjobs (we need the passwords, after all).
set -o allexport
env > /root/env.env
set +o allexport
exec cron -f
