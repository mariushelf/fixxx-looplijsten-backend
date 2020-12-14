#!/usr/bin/env bash
#
# Import BWV dump data into local bwv_db container.

set -euo pipefail

if test $# -lt 1; then
  echo "Usage: $0 /path/to/dir/with/dumps" >/dev/stderr
  exit 1
fi

DUMP_DIR=$1
DOCKER_NETWORK=looplijsten_backend
DB_HOST=bwv_db
DB_NAME=looplijsten_bwv
DB_USER=looplijsten_bwv
DB_PASS=insecure

CMD=$(cat <<'EOF' | sed -e "s/<DB_HOST>/${DB_HOST}/" -e "s/<DB_USER>/${DB_USER}/" -e "s/<DB_PASS>/${DB_PASS}/" -e "s/<DB_NAME>/${DB_NAME}/"
export PGHOST=<DB_HOST>;
export PGUSER=<DB_USER>;
export PGPASSWORD=<DB_PASS>;
#echo "<DB_PASS>" > ~/.pgpass;
#chmod 600 ~/.pgpass;
for f in /dumps/*.dump; do
  pg_restore -d <DB_NAME> "$f";
done
EOF
)

docker run --name bwv_import --rm --network "$DOCKER_NETWORK" -v ${DUMP_DIR}:/dumps amsterdam/postgres11 sh -c "${CMD[@]}"
