#!/usr/bin/env bash
set -e

celery -A settings worker  -l INFO
